from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
import os
import json
from dotenv import load_dotenv
import models
import schemas
from database import engine, get_db
from ticket_service import ticket_service
from email_service import email_service
from timezone_utils import (
    get_bogota_now_naive,
    format_datetime_bogota,
    is_same_day_bogota,
    get_day_start_bogota,
    get_day_end_bogota
)
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
    require_validator,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Cargar variables de entorno
load_dotenv()

# Configuración
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IEEE Tadeo Control System",
    description="Sistema de control y gestión para eventos IEEE",
    version="1.0.0"
)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/qr_codes", StaticFiles(directory="qr_codes"), name="qr_codes")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Importar rutas del portal de usuarios
from user_portal_routes import router as user_portal_router
app.include_router(user_portal_router)


# ========== ENDPOINTS DE AUTENTICACIÓN ==========

@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Endpoint de login - retorna token JWT"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/validators", response_model=schemas.AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_validator(
    validator_data: schemas.AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un nuevo validador (solo ADMIN)"""
    # Verificar si el username ya existe
    existing_user = db.query(models.AdminUser).filter(
        models.AdminUser.username == validator_data.username
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    # Verificar si el email ya existe
    existing_email = db.query(models.AdminUser).filter(
        models.AdminUser.email == validator_data.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Crear el validador
    hashed_password = get_password_hash(validator_data.password)

    # Convertir el string role a RoleEnum
    role_enum = models.RoleEnum.ADMIN if validator_data.role == "admin" else models.RoleEnum.VALIDATOR

    db_user = models.AdminUser(
        username=validator_data.username,
        email=validator_data.email,
        hashed_password=hashed_password,
        full_name=validator_data.full_name,
        role=role_enum,
        access_start=validator_data.access_start,
        access_end=validator_data.access_end
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/auth/validators", response_model=List[schemas.AdminUserResponse])
def list_validators(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los validadores (solo ADMIN)"""
    validators = db.query(models.AdminUser).all()
    return validators


@app.put("/auth/validators/{validator_id}", response_model=schemas.AdminUserResponse)
def update_validator(
    validator_id: int,
    validator_update: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar un usuario admin/validador (solo ADMIN)"""
    validator = db.query(models.AdminUser).filter(models.AdminUser.id == validator_id).first()
    if not validator:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar solo los campos proporcionados
    if validator_update.username is not None:
        # Verificar que el username no esté en uso por otro usuario
        existing = db.query(models.AdminUser).filter(
            models.AdminUser.username == validator_update.username,
            models.AdminUser.id != validator_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        validator.username = validator_update.username

    if validator_update.email is not None:
        # Verificar que el email no esté en uso por otro usuario
        existing = db.query(models.AdminUser).filter(
            models.AdminUser.email == validator_update.email,
            models.AdminUser.id != validator_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario")
        validator.email = validator_update.email

    if validator_update.full_name is not None:
        validator.full_name = validator_update.full_name

    if validator_update.role is not None:
        # Validar que el rol sea válido
        if validator_update.role not in ['admin', 'validator']:
            raise HTTPException(status_code=400, detail="Rol inválido. Use 'admin' o 'validator'")
        validator.role = models.RoleEnum(validator_update.role)

    if validator_update.is_active is not None:
        validator.is_active = validator_update.is_active

    if validator_update.access_start is not None:
        validator.access_start = validator_update.access_start

    if validator_update.access_end is not None:
        validator.access_end = validator_update.access_end

    if validator_update.password is not None:
        # Actualizar contraseña si se proporciona
        validator.hashed_password = get_password_hash(validator_update.password)

    db.commit()
    db.refresh(validator)

    return validator


# ========== ENDPOINTS DE UNIVERSIDADES ==========

@app.post("/universities/", response_model=schemas.UniversityResponse, status_code=status.HTTP_201_CREATED)
def create_university(
    university: schemas.UniversityCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear una nueva universidad (solo ADMIN)"""
    # Verificar si el nombre ya existe
    existing = db.query(models.University).filter(models.University.name == university.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Universidad ya existe")

    db_university = models.University(**university.model_dump())
    db.add(db_university)
    db.commit()
    db.refresh(db_university)
    return db_university


@app.get("/universities/", response_model=List[schemas.UniversityResponse])
def list_universities(
    skip: int = 0,
    limit: int = 200,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar universidades (público para formularios)"""
    query = db.query(models.University)
    if active_only:
        query = query.filter(models.University.is_active == True)
    universities = query.order_by(models.University.name).offset(skip).limit(limit).all()
    return universities


@app.get("/universities/{university_id}", response_model=schemas.UniversityResponse)
def get_university(
    university_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener una universidad por ID"""
    university = db.query(models.University).filter(models.University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")
    return university


@app.put("/universities/{university_id}", response_model=schemas.UniversityResponse)
def update_university(
    university_id: int,
    university_update: schemas.UniversityUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar una universidad (solo ADMIN)"""
    university = db.query(models.University).filter(models.University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")

    # Actualizar campos
    if university_update.name is not None:
        # Verificar que el nombre no esté en uso
        existing = db.query(models.University).filter(
            models.University.name == university_update.name,
            models.University.id != university_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El nombre ya está en uso")
        university.name = university_update.name

    if university_update.short_name is not None:
        university.short_name = university_update.short_name

    if university_update.is_active is not None:
        university.is_active = university_update.is_active

    if university_update.has_ieee_branch is not None:
        university.has_ieee_branch = university_update.has_ieee_branch

    if university_update.ieee_contact_email is not None:
        university.ieee_contact_email = university_update.ieee_contact_email

    if university_update.ieee_facebook is not None:
        university.ieee_facebook = university_update.ieee_facebook

    if university_update.ieee_instagram is not None:
        university.ieee_instagram = university_update.ieee_instagram

    if university_update.ieee_twitter is not None:
        university.ieee_twitter = university_update.ieee_twitter

    if university_update.ieee_tiktok is not None:
        university.ieee_tiktok = university_update.ieee_tiktok

    if university_update.ieee_website is not None:
        university.ieee_website = university_update.ieee_website

    db.commit()
    db.refresh(university)
    return university


@app.delete("/universities/{university_id}")
def delete_university(
    university_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar una universidad (solo ADMIN)"""
    university = db.query(models.University).filter(models.University.id == university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="Universidad no encontrada")

    # Verificar si hay usuarios asociados
    user_count = db.query(models.User).filter(models.User.university_id == university_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la universidad porque tiene {user_count} usuario(s) asociado(s)"
        )

    db.delete(university)
    db.commit()

    return {
        "success": True,
        "message": "Universidad eliminada exitosamente",
        "university_id": university_id
    }


# ========== ENDPOINTS DE TAGS ==========

@app.get("/tags/", response_model=List[schemas.TagResponse])
def list_tags(
    skip: int = 0,
    limit: int = 200,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar tags/etiquetas (público)"""
    query = db.query(models.Tag)
    if active_only:
        query = query.filter(models.Tag.is_active == True)
    tags = query.order_by(models.Tag.name).offset(skip).limit(limit).all()
    return tags


@app.post("/tags/", response_model=schemas.TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un nuevo tag (solo ADMIN)"""
    # Verificar si el nombre ya existe
    existing = db.query(models.Tag).filter(models.Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag ya existe")

    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/tags/{tag_id}", response_model=schemas.TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener un tag por ID"""
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    return tag


@app.put("/tags/{tag_id}", response_model=schemas.TagResponse)
def update_tag(
    tag_id: int,
    tag_update: schemas.TagUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar un tag (solo ADMIN)"""
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Actualizar campos
    if tag_update.name is not None:
        # Verificar que el nombre no esté en uso
        existing = db.query(models.Tag).filter(
            models.Tag.name == tag_update.name,
            models.Tag.id != tag_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El nombre ya está en uso")
        tag.name = tag_update.name

    if tag_update.color is not None:
        tag.color = tag_update.color

    if tag_update.description is not None:
        tag.description = tag_update.description

    if tag_update.is_active is not None:
        tag.is_active = tag_update.is_active

    db.commit()
    db.refresh(tag)
    return tag


@app.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar un tag (solo ADMIN)"""
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Verificar si hay usuarios asociados
    user_count = db.query(models.User).join(models.user_tags).filter(
        models.user_tags.c.tag_id == tag_id
    ).count()

    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el tag porque tiene {user_count} usuario(s) asociado(s)"
        )

    db.delete(tag)
    db.commit()

    return {
        "success": True,
        "message": "Tag eliminado exitosamente",
        "tag_id": tag_id
    }


@app.post("/users/{user_id}/tags/{tag_id}")
def add_tag_to_user(
    user_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Agregar un tag a un usuario (solo ADMIN)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Verificar si el tag ya está asignado
    if tag in user.tags:
        raise HTTPException(status_code=400, detail="El usuario ya tiene este tag")

    user.tags.append(tag)
    db.commit()

    return {
        "success": True,
        "message": f"Tag '{tag.name}' agregado al usuario '{user.name}'",
        "user_id": user_id,
        "tag_id": tag_id
    }


@app.delete("/users/{user_id}/tags/{tag_id}")
def remove_tag_from_user(
    user_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Remover un tag de un usuario (solo ADMIN)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Verificar si el tag está asignado
    if tag not in user.tags:
        raise HTTPException(status_code=400, detail="El usuario no tiene este tag")

    user.tags.remove(tag)
    db.commit()

    return {
        "success": True,
        "message": f"Tag '{tag.name}' removido del usuario '{user.name}'",
        "user_id": user_id,
        "tag_id": tag_id
    }


# ========== ENDPOINTS DE ORGANIZACIONES ==========

@app.post("/organizations/", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    organization: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear una nueva organización (solo ADMIN)"""
    # Verificar si el nombre ya existe
    existing = db.query(models.Organization).filter(models.Organization.name == organization.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organización ya existe")

    db_organization = models.Organization(**organization.model_dump())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


@app.get("/organizations/", response_model=List[schemas.OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 200,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar organizaciones (público para formularios)"""
    query = db.query(models.Organization)
    if active_only:
        query = query.filter(models.Organization.is_active == True)
    organizations = query.order_by(models.Organization.name).offset(skip).limit(limit).all()
    return organizations


@app.get("/organizations/{organization_id}", response_model=schemas.OrganizationResponse)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener una organización por ID"""
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organización no encontrada")
    return organization


@app.put("/organizations/{organization_id}", response_model=schemas.OrganizationResponse)
def update_organization(
    organization_id: int,
    organization_update: schemas.OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar una organización (solo ADMIN)"""
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    # Actualizar campos
    update_data = organization_update.model_dump(exclude_unset=True)

    # Si se actualiza el nombre, verificar que no esté en uso
    if "name" in update_data:
        existing = db.query(models.Organization).filter(
            models.Organization.name == update_data["name"],
            models.Organization.id != organization_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="El nombre ya está en uso")

    for key, value in update_data.items():
        setattr(organization, key, value)

    db.commit()
    db.refresh(organization)
    return organization


@app.delete("/organizations/{organization_id}")
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar una organización (solo ADMIN)"""
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organización no encontrada")

    # Verificar si hay usuarios asociados
    user_count = db.query(models.User).filter(models.User.organization_id == organization_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la organización porque tiene {user_count} usuario(s) asociado(s)"
        )

    # Verificar si hay eventos asociados
    event_count = db.query(models.Event).filter(models.Event.organization_id == organization_id).count()
    if event_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la organización porque tiene {event_count} evento(s) asociado(s)"
        )

    db.delete(organization)
    db.commit()

    return {
        "success": True,
        "message": "Organización eliminada exitosamente",
        "organization_id": organization_id
    }


# ========== ENDPOINTS DE USUARIOS ==========

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un nuevo usuario"""
    # Verificar si el email ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/")
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los usuarios con información de cumpleaños"""
    from birthday_utils import get_birthday_status

    users = db.query(models.User).offset(skip).limit(limit).all()

    # Enriquecer respuesta con información de cumpleaños
    users_with_birthday = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "identification": user.identification,
            "university_id": user.university_id,
            "is_ieee_member": user.is_ieee_member,
            "created_at": user.created_at,
            "birthday": user.birthday,
            "birthday_status": get_birthday_status(user.birthday)
        }
        users_with_birthday.append(user_dict)

    return users_with_birthday


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener un usuario por ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar un usuario"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Si se está actualizando el email, verificar que no esté en uso por otro usuario
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya registrado por otro usuario")

    # Actualizar solo los campos proporcionados
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.country_code is not None:
        user.country_code = user_update.country_code
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.identification is not None:
        user.identification = user_update.identification
    if user_update.university_id is not None:
        user.university_id = user_update.university_id
    if user_update.birthday is not None:
        user.birthday = user_update.birthday
    if user_update.is_ieee_member is not None:
        user.is_ieee_member = user_update.is_ieee_member

    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar un usuario"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el usuario tiene tickets
    ticket_count = db.query(models.Ticket).filter(models.Ticket.user_id == user_id).count()
    if ticket_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el usuario porque tiene {ticket_count} ticket(s) asociado(s)"
        )

    db.delete(user)
    db.commit()

    return {
        "success": True,
        "message": "Usuario eliminado exitosamente",
        "user_id": user_id
    }


@app.post("/users/import-csv")
async def import_users_from_csv(
    file: UploadFile = File(...),
    tag_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Importar usuarios desde CSV y asignar tag (solo ADMIN)"""
    import csv
    import io

    # Verificar que el tag existe
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Verificar que el archivo es CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser CSV")

    # Leer el archivo CSV
    try:
        content = await file.read()
        decoded_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_content))
        rows = list(csv_reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el archivo CSV: {str(e)}")

    # Estadísticas
    stats = {
        'created': 0,
        'duplicates': 0,
        'tag_added': 0,
        'tag_already_exists': 0,
        'errors': 0,
        'total_processed': len(rows)
    }

    errors = []

    # Procesar cada fila
    for i, row in enumerate(rows, start=1):
        try:
            email = row.get('email', '').strip().lower()
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip()

            # Validar campos obligatorios: name, email, phone
            if not email or not name or not phone:
                missing = []
                if not name: missing.append('name')
                if not email: missing.append('email')
                if not phone: missing.append('phone')
                errors.append(f"Fila {i}: Campos obligatorios vacíos: {', '.join(missing)}")
                stats['errors'] += 1
                continue

            # Buscar usuario existente
            existing_user = db.query(models.User).filter(models.User.email == email).first()

            if existing_user:
                # Usuario duplicado - agregar tag si no lo tiene
                stats['duplicates'] += 1

                if tag in existing_user.tags:
                    stats['tag_already_exists'] += 1
                else:
                    existing_user.tags.append(tag)
                    stats['tag_added'] += 1
            else:
                # Usuario nuevo - crear con el tag
                # phone ya está extraído en la validación
                country_code = row.get('country_code', '').strip() or '+57'
                identification = row.get('identification', '').strip() or None
                university_name = row.get('university_name', '').strip()
                is_ieee_member = row.get('is_ieee_member', '').strip().lower() in ['true', '1', 'yes', 'sí', 'si']
                ieee_member_id = row.get('ieee_member_id', '').strip() or None

                # Buscar universidad
                university_id = None
                if university_name:
                    university = db.query(models.University).filter(
                        models.University.name == university_name
                    ).first()
                    if university:
                        university_id = university.id

                # Crear usuario
                new_user = models.User(
                    name=name,
                    email=email,
                    phone=phone,
                    country_code=country_code,
                    identification=identification,
                    university_id=university_id,
                    is_ieee_member=is_ieee_member,
                    ieee_member_id=ieee_member_id,
                    created_at=get_bogota_now_naive()
                )

                db.add(new_user)
                db.flush()  # Para obtener el ID

                # Agregar el tag
                new_user.tags.append(tag)
                stats['created'] += 1

        except Exception as e:
            errors.append(f"Fila {i}: {str(e)}")
            stats['errors'] += 1
            db.rollback()
            continue

    # Commit final
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar los cambios: {str(e)}")

    return {
        "success": True,
        "message": "Importación completada",
        "stats": stats,
        "tag_name": tag.name,
        "errors": errors[:50]  # Limitar a 50 errores
    }


@app.post("/users/{user_id}/send-birthday")
def send_birthday_greeting(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Enviar mensaje de cumpleaños manual (email + WhatsApp)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = {
        "user_id": user_id,
        "user_name": user.name,
        "email_sent": False,
        "whatsapp_sent": False,
        "errors": []
    }

    # 1. Enviar email
    try:
        email_success = email_service.send_birthday_email(
            to_email=user.email,
            user_name=user.name,
            nick=user.nick
        )
        results["email_sent"] = email_success
        if not email_success:
            results["errors"].append("No se pudo enviar el email")
    except Exception as e:
        results["errors"].append(f"Error en email: {str(e)}")

    # 2. Enviar WhatsApp (si tiene teléfono)
    if user.phone and user.country_code:
        try:
            from whatsapp_client import send_birthday_whatsapp, WhatsAppClient

            # Verificar que WhatsApp esté disponible
            whatsapp_client = WhatsAppClient()
            if whatsapp_client.is_ready():
                whatsapp_success = send_birthday_whatsapp(
                    phone=user.phone,
                    country_code=user.country_code,
                    user_name=user.name,
                    nick=user.nick
                )
                results["whatsapp_sent"] = whatsapp_success
                if not whatsapp_success:
                    results["errors"].append("No se pudo enviar WhatsApp")
            else:
                results["errors"].append("Servicio de WhatsApp no disponible")

        except Exception as e:
            results["errors"].append(f"Error en WhatsApp: {str(e)}")
    else:
        results["errors"].append("Usuario sin número de teléfono")

    # Determinar el resultado general
    if results["email_sent"] or results["whatsapp_sent"]:
        return {
            "success": True,
            "message": "Mensaje de cumpleaños enviado",
            "details": results
        }
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "No se pudo enviar ningún mensaje",
                "details": results
            }
        )
@app.get("/users/by-tag/{tag_id}", response_model=List[schemas.UserResponse])
def get_users_by_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener todos los usuarios que tienen una etiqueta específica"""
    from sqlalchemy.orm import joinedload

    # Verificar que el tag existe
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Obtener usuarios con ese tag
    users = db.query(models.User).options(
        joinedload(models.User.university),
        joinedload(models.User.tags)
    ).join(models.user_tags).filter(
        models.user_tags.c.tag_id == tag_id
    ).all()

    return users


# ========== ENDPOINTS DE CUMPLEAÑOS ==========

@app.get("/birthdays/last-check")
def get_last_birthday_check(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener información de la última ejecución del sistema de cumpleaños"""
    last_check = db.query(models.BirthdayCheckLog).order_by(
        desc(models.BirthdayCheckLog.executed_at)
    ).first()

    if not last_check:
        return {
            "has_logs": False,
            "message": "No hay registros de ejecuciones anteriores"
        }

    # Calcular tiempo desde la última ejecución
    now = datetime.now()
    time_since = now - last_check.executed_at
    hours_since = int(time_since.total_seconds() / 3600)
    minutes_since = int((time_since.total_seconds() % 3600) / 60)

    # Determinar mensaje de tiempo
    if hours_since < 1:
        time_message = f"Hace {minutes_since} minuto{'s' if minutes_since != 1 else ''}"
    elif hours_since < 24:
        time_message = f"Hace {hours_since} hora{'s' if hours_since != 1 else ''}"
    else:
        days_since = int(hours_since / 24)
        time_message = f"Hace {days_since} día{'s' if days_since != 1 else ''}"

    return {
        "has_logs": True,
        "last_check": {
            "id": last_check.id,
            "executed_at": last_check.executed_at.isoformat(),
            "time_since": time_message,
            "hours_since": hours_since,
            "birthdays_found": last_check.birthdays_found,
            "emails_sent": last_check.emails_sent,
            "emails_failed": last_check.emails_failed,
            "whatsapp_sent": last_check.whatsapp_sent,
            "whatsapp_failed": last_check.whatsapp_failed,
            "whatsapp_available": last_check.whatsapp_available,
            "execution_type": last_check.execution_type,
            "notes": last_check.notes,
            "success_rate": {
                "email": f"{(last_check.emails_sent / (last_check.emails_sent + last_check.emails_failed) * 100):.1f}%" if (last_check.emails_sent + last_check.emails_failed) > 0 else "N/A",
                "whatsapp": f"{(last_check.whatsapp_sent / (last_check.whatsapp_sent + last_check.whatsapp_failed) * 100):.1f}%" if (last_check.whatsapp_sent + last_check.whatsapp_failed) > 0 else "N/A"
            }
        }
    }


@app.post("/birthdays/check-now")
def check_birthdays_now(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Ejecutar manualmente el verificador de cumpleaños"""
    from birthday_checker import check_and_send_birthday_emails

    try:
        # Ejecutar verificación manual
        check_and_send_birthday_emails(execution_type="manual")

        # Obtener el último log para retornar la información
        last_check = db.query(models.BirthdayCheckLog).order_by(
            desc(models.BirthdayCheckLog.executed_at)
        ).first()

        return {
            "success": True,
            "message": "Verificación de cumpleaños ejecutada exitosamente",
            "result": {
                "birthdays_found": last_check.birthdays_found if last_check else 0,
                "emails_sent": last_check.emails_sent if last_check else 0,
                "whatsapp_sent": last_check.whatsapp_sent if last_check else 0
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar verificación: {str(e)}"
        )

# ========== ENDPOINTS DE EVENTOS ==========

@app.post("/events/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un nuevo evento"""
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get("/events/", response_model=List[schemas.EventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los eventos"""
    query = db.query(models.Event)
    if active_only:
        query = query.filter(models.Event.is_active == True)
    events = query.offset(skip).limit(limit).all()
    return events


@app.get("/events/{event_id}", response_model=schemas.EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener un evento por ID"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event


@app.put("/events/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar un evento"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Actualizar solo los campos proporcionados
    if event_update.name is not None:
        event.name = event_update.name
    if event_update.description is not None:
        event.description = event_update.description
    if event_update.location is not None:
        event.location = event_update.location
    if event_update.event_date is not None:
        event.event_date = event_update.event_date
    if event_update.is_active is not None:
        event.is_active = event_update.is_active
    if event_update.organization_id is not None:
        event.organization_id = event_update.organization_id
    if event_update.whatsapp_template is not None:
        event.whatsapp_template = event_update.whatsapp_template
    if event_update.email_template is not None:
        event.email_template = event_update.email_template
    if event_update.send_qr_with_whatsapp is not None:
        event.send_qr_with_whatsapp = event_update.send_qr_with_whatsapp

    db.commit()
    db.refresh(event)
    return event


@app.post("/events/{event_id}/upload-whatsapp-image")
async def upload_event_whatsapp_image(
    event_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Subir imagen de WhatsApp para un evento"""
    import os
    from pathlib import Path

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Validar que sea una imagen
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Validar tamaño (máx 5MB)
    content = await image.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen no puede superar los 5MB")

    # Generar nombre único para el archivo
    ext = Path(image.filename).suffix
    filename = f"event_{event_id}_{int(datetime.now().timestamp())}{ext}"
    filepath = f"static/event_images/{filename}"

    # Guardar el archivo
    try:
        with open(filepath, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")

    # Eliminar imagen anterior si existe
    if event.whatsapp_image_path and os.path.exists(event.whatsapp_image_path):
        try:
            os.remove(event.whatsapp_image_path)
        except:
            pass

    # Actualizar el evento
    event.whatsapp_image_path = filepath
    db.commit()
    db.refresh(event)

    return {
        "message": "Imagen subida exitosamente",
        "image_path": filepath,
        "image_url": f"/{filepath}"
    }


@app.delete("/events/{event_id}/whatsapp-image")
def delete_event_whatsapp_image(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar imagen de WhatsApp de un evento"""
    import os

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if not event.whatsapp_image_path:
        raise HTTPException(status_code=404, detail="El evento no tiene imagen de WhatsApp")

    # Eliminar el archivo
    if os.path.exists(event.whatsapp_image_path):
        try:
            os.remove(event.whatsapp_image_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al eliminar la imagen: {str(e)}")

    # Actualizar el evento
    event.whatsapp_image_path = None
    db.commit()
    db.refresh(event)

    return {"message": "Imagen eliminada exitosamente"}


@app.get("/events/{event_id}/tickets")
def get_event_tickets(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener todos los tickets de un evento con información del usuario"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Obtener tickets con información del usuario
    tickets = db.query(
        models.Ticket,
        models.User
    ).join(
        models.User, models.Ticket.user_id == models.User.id
    ).filter(
        models.Ticket.event_id == event_id
    ).all()

    result = []
    for ticket, user in tickets:
        result.append({
            "ticket_id": ticket.id,
            "ticket_code": ticket.ticket_code,
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "user_identification": user.identification,
            "companions": ticket.companions,
            "total_people": 1 + ticket.companions,
            "is_used": ticket.is_used,
            "used_at": ticket.used_at.isoformat() if ticket.used_at else None,
            "created_at": ticket.created_at.isoformat()
        })

    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_tickets": len(result),
        "tickets_used": sum(1 for t in result if t["is_used"]),
        "tickets": result
    }


# ========== ENDPOINTS DE TICKETS ==========

@app.post("/tickets/", response_model=schemas.TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un ticket para un usuario en un evento"""
    # Verificar que el usuario existe
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar que el evento existe
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Verificar que el usuario no tenga ya un ticket para este evento
    existing_ticket = db.query(models.Ticket).filter(
        models.Ticket.user_id == ticket.user_id,
        models.Ticket.event_id == ticket.event_id
    ).first()
    if existing_ticket:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un ticket para este evento")

    # Generar código de ticket
    ticket_code = ticket_service.generate_ticket_code(ticket.user_id, ticket.event_id)

    # Generar URL única y PIN
    unique_url = ticket_service.generate_unique_url()
    access_pin = ticket_service.generate_pin()

    # Generar QR code
    qr_path = ticket_service.generate_qr_code(
        ticket_code=ticket_code,
        user_name=user.name,
        event_name=event.name,
        event_date=event.event_date.isoformat()
    )

    # Crear ticket en la BD
    db_ticket = models.Ticket(
        ticket_code=ticket_code,
        user_id=ticket.user_id,
        event_id=ticket.event_id,
        qr_path=qr_path,
        unique_url=unique_url,
        access_pin=access_pin
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    event_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los tickets, opcionalmente filtrados por evento"""
    from sqlalchemy.orm import joinedload

    query = db.query(models.Ticket).options(
        joinedload(models.Ticket.user),
        joinedload(models.Ticket.event)
    )

    if event_id:
        query = query.filter(models.Ticket.event_id == event_id)

    tickets = query.offset(skip).limit(limit).all()
    return tickets


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener un ticket por ID"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@app.post("/tickets/{ticket_id}/reactivate")
def reactivate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Reactivar un ticket usado (marcarlo como no usado)"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if not ticket.is_used:
        raise HTTPException(status_code=400, detail="El ticket no ha sido usado aún")

    # Eliminar todos los registros de validación de este ticket
    db.query(models.ValidationLog).filter(
        models.ValidationLog.ticket_id == ticket_id
    ).delete()

    # Reactivar el ticket
    ticket.is_used = False
    ticket.used_at = None
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "message": "Ticket reactivado exitosamente (validaciones eliminadas)",
        "ticket_id": ticket.id,
        "ticket_code": ticket.ticket_code
    }


@app.put("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Actualizar un ticket (acompañantes y modo de validación)"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Actualizar solo los campos proporcionados
    if ticket_update.companions is not None:
        ticket.companions = ticket_update.companions

    if ticket_update.validation_mode is not None:
        ticket.validation_mode = ticket_update.validation_mode

    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar un ticket"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Eliminar el archivo QR si existe
    if ticket.qr_path:
        import os
        try:
            if os.path.exists(ticket.qr_path):
                os.remove(ticket.qr_path)
        except Exception as e:
            print(f"Error al eliminar archivo QR: {e}")

    db.delete(ticket)
    db.commit()

    return {
        "success": True,
        "message": "Ticket eliminado exitosamente",
        "ticket_id": ticket_id
    }


@app.get("/tickets/{ticket_id}/qr")
def get_ticket_qr(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener la imagen QR de un ticket - regenera el QR optimizado"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Obtener datos del usuario y evento para regenerar el QR
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    # Regenerar el QR con la versión optimizada (solo ticket_code)
    qr_path = ticket_service.generate_qr_code(
        ticket_code=ticket.ticket_code,
        user_name=user.name,
        event_name=event.name,
        event_date=event.event_date.isoformat()
    )

    # Actualizar la ruta en la base de datos
    ticket.qr_path = qr_path
    db.commit()

    return FileResponse(qr_path, filename=f"ticket_{ticket_id}.png")


@app.get("/tickets/{ticket_id}/qr-base64")
def get_ticket_qr_base64(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener el QR en formato base64 para mostrar en web"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    qr_base64 = ticket_service.generate_qr_base64(
        ticket_code=ticket.ticket_code,
        user_name=user.name,
        event_name=event.name,
        event_date=event.event_date.isoformat()
    )

    return {"qr_code": qr_base64}


@app.post("/tickets/{ticket_id}/send-email")
def send_ticket_email(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Enviar ticket por correo electrónico al usuario"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Construir URL completa del ticket
    ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

    # Enviar correo
    success = email_service.send_ticket_email(
        to_email=user.email,
        user_name=user.name,
        event_name=event.name,
        event_date=event.event_date,
        event_location=event.location,
        ticket_code=ticket.ticket_code,
        ticket_url=ticket_url,
        access_pin=ticket.access_pin,
        companions=ticket.companions,
        organization=organization,
        event=event
    )

    if success:
        return {"message": "Correo enviado exitosamente", "email": user.email}
    else:
        raise HTTPException(status_code=500, detail="Error al enviar el correo")


@app.post("/tickets/send-email-by-event-stream")
async def send_tickets_email_by_event_stream(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Enviar tickets por Email masivamente con Server-Sent Events para progreso en tiempo real

    Body:
    - event_id: ID del evento

    Retorna un stream de eventos con el formato:
    - event: progress -> Progreso de envío individual
    - event: complete -> Resumen final
    """
    event_id = data.get('event_id')

    if not event_id:
        raise HTTPException(status_code=400, detail="event_id es requerido")

    # Función generadora para SSE
    async def event_generator():
        try:
            # Verificar que el evento existe
            event = db.query(models.Event).filter(models.Event.id == event_id).first()
            if not event:
                yield f"data: {json.dumps({'event': 'error', 'message': 'Evento no encontrado'})}\n\n"
                return

            # Cargar organización del evento si existe
            organization = None
            if event.organization_id:
                organization = db.query(models.Organization).filter(
                    models.Organization.id == event.organization_id
                ).first()

            # Obtener todos los tickets del evento con sus usuarios
            from sqlalchemy.orm import joinedload

            tickets = db.query(models.Ticket).options(
                joinedload(models.Ticket.user)
            ).filter(
                models.Ticket.event_id == event_id
            ).all()

            if not tickets:
                yield f"data: {json.dumps({'event': 'error', 'message': 'No se encontraron tickets para este evento'})}\n\n"
                return

            # Enviar evento de inicio
            yield f"data: {json.dumps({'event': 'start', 'total': len(tickets), 'event_name': event.name})}\n\n"

            # Enviar tickets por Email
            sent_count = 0
            skipped_count = 0
            errors = []

            import asyncio

            for idx, ticket in enumerate(tickets):
                user = ticket.user

                try:
                    # Verificar que el usuario tenga email
                    if not user.email:
                        skipped_count += 1
                        error_msg = f"{user.name}: Sin correo electrónico"
                        errors.append(error_msg)

                        # Enviar evento de skip
                        yield f"data: {json.dumps({'event': 'skip', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': 'Sin email'})}\n\n"
                        continue

                    # Enviar evento de progreso - enviando
                    yield f"data: {json.dumps({'event': 'sending', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'email': user.email})}\n\n"

                    # Construir URL completa del ticket
                    ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

                    # Enviar por Email
                    success = email_service.send_ticket_email(
                        to_email=user.email,
                        user_name=user.name,
                        event_name=event.name,
                        event_date=event.event_date,
                        event_location=event.location,
                        ticket_code=ticket.ticket_code,
                        ticket_url=ticket_url,
                        access_pin=ticket.access_pin,
                        companions=ticket.companions,
                        organization=organization,
                        event=event
                    )

                    if success:
                        sent_count += 1
                        # Enviar evento de éxito
                        yield f"data: {json.dumps({'event': 'success', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'email': user.email})}\n\n"
                    else:
                        skipped_count += 1
                        error_msg = f"{user.name}: Error al enviar email"
                        errors.append(error_msg)
                        # Enviar evento de error
                        yield f"data: {json.dumps({'event': 'error', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': 'Error al enviar'})}\n\n"

                    # Pequeño delay entre envíos para evitar rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    skipped_count += 1
                    error_msg = f"{user.name}: {str(e)}"
                    errors.append(error_msg)
                    # Enviar evento de error
                    yield f"data: {json.dumps({'event': 'error', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': str(e)})}\n\n"
                    continue

            # Enviar evento de completado
            yield f"data: {json.dumps({'event': 'complete', 'sent': sent_count, 'skipped': skipped_count, 'total': len(tickets), 'errors': errors})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============================================
# WhatsApp Webhook Endpoints
# ============================================

@app.get("/webhooks/whatsapp")
async def whatsapp_webhook_verification(request: Request):
    """
    Endpoint de verificación del webhook de WhatsApp.
    Meta enviará una petición GET con estos parámetros para verificar el webhook.
    """
    # Obtener parámetros de la query
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Token de verificación (configurable en .env)
    WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "mi_token_secreto_123")

    # Verificar que el modo sea "subscribe" y el token coincida
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        print(f"[WEBHOOK] Verificación exitosa del webhook de WhatsApp")
        # Retornar el challenge para completar la verificación
        return int(challenge)
    else:
        print(f"[WEBHOOK] Verificación fallida - Mode: {mode}, Token válido: {token == WEBHOOK_VERIFY_TOKEN}")
        raise HTTPException(status_code=403, detail="Verificación fallida")


@app.post("/webhooks/whatsapp")
async def whatsapp_webhook_handler(request: Request):
    """
    Endpoint que recibe notificaciones de WhatsApp sobre:
    - Mensajes recibidos
    - Estados de mensajes enviados (entregado, leído, etc.)
    - Otros eventos
    """
    db = next(get_db())
    try:
        body = await request.json()

        # Logging del evento recibido
        print(f"[WEBHOOK] Evento de WhatsApp recibido:")
        print(json.dumps(body, indent=2))

        if "entry" in body:
            for entry in body["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if "value" in change:
                            value = change["value"]

                            # Procesar mensajes recibidos
                            if "messages" in value:
                                contacts = value.get("contacts", [])
                                messages = value["messages"]

                                for message in messages:
                                    from_number = message.get("from")
                                    msg_type = message.get("type")
                                    msg_id = message.get("id")
                                    timestamp = message.get("timestamp")

                                    # Obtener nombre del contacto
                                    contact_name = None
                                    for contact in contacts:
                                        if contact.get("wa_id") == from_number:
                                            contact_name = contact.get("profile", {}).get("name")
                                            break

                                    print(f"[WEBHOOK] Mensaje de {from_number} ({contact_name}): {msg_type}")

                                    # Verificar si el mensaje ya existe
                                    existing = db.query(models.WhatsAppMessage).filter(
                                        models.WhatsAppMessage.wa_message_id == msg_id
                                    ).first()

                                    if not existing:
                                        # Extraer contenido según tipo
                                        text_body = None
                                        media_id = None
                                        caption = None

                                        if msg_type == "text":
                                            text_body = message.get("text", {}).get("body")
                                        elif msg_type in ["image", "video", "audio", "document", "sticker"]:
                                            media_data = message.get(msg_type, {})
                                            media_id = media_data.get("id")
                                            caption = media_data.get("caption")
                                        elif msg_type == "location":
                                            loc = message.get("location", {})
                                            text_body = f"Ubicación: {loc.get('latitude')}, {loc.get('longitude')}"

                                        # Crear mensaje en BD
                                        new_message = models.WhatsAppMessage(
                                            wa_message_id=msg_id,
                                            from_number=from_number,
                                            from_name=contact_name,
                                            message_type=msg_type,
                                            text_body=text_body,
                                            media_id=media_id,
                                            caption=caption,
                                            context_message_id=message.get("context", {}).get("id"),
                                            is_forwarded=message.get("context", {}).get("forwarded", False),
                                            timestamp=datetime.fromtimestamp(int(timestamp)) if timestamp else datetime.utcnow(),
                                            raw_payload=json.dumps(message)
                                        )
                                        db.add(new_message)

                                        # Actualizar o crear conversación
                                        conversation = db.query(models.WhatsAppConversation).filter(
                                            models.WhatsAppConversation.phone_number == from_number
                                        ).first()

                                        if conversation:
                                            conversation.last_message_at = datetime.utcnow()
                                            conversation.last_user_message_at = datetime.utcnow()
                                            conversation.unread_count += 1
                                            conversation.is_active = True
                                            if contact_name and not conversation.contact_name:
                                                conversation.contact_name = contact_name
                                        else:
                                            # Buscar usuario por teléfono
                                            user = db.query(models.User).filter(
                                                models.User.phone == from_number[-10:]  # Últimos 10 dígitos
                                            ).first()

                                            conversation = models.WhatsAppConversation(
                                                phone_number=from_number,
                                                contact_name=contact_name,
                                                user_id=user.id if user else None,
                                                last_message_at=datetime.utcnow(),
                                                last_user_message_at=datetime.utcnow(),
                                                unread_count=1,
                                                is_active=True
                                            )
                                            db.add(conversation)

                                        db.commit()

                            # Procesar estados de mensajes
                            if "statuses" in value:
                                statuses = value["statuses"]
                                for status_data in statuses:
                                    msg_id = status_data.get("id")
                                    status_type = status_data.get("status")
                                    recipient = status_data.get("recipient_id")
                                    print(f"[WEBHOOK] Estado: {msg_id} -> {status_type}")

                                    # Actualizar MessageRecipient si existe
                                    recipient_record = db.query(models.MessageRecipient).filter(
                                        models.MessageRecipient.whatsapp_message_id == msg_id
                                    ).first()

                                    if recipient_record:
                                        recipient_record.whatsapp_status = status_type
                                        recipient_record.whatsapp_status_updated_at = datetime.utcnow()
                                        if status_type == "failed":
                                            recipient_record.whatsapp_sent = False
                                            error_info = status_data.get("errors", [{}])[0]
                                            recipient_record.whatsapp_error = error_info.get("message", "Error desconocido")
                                        db.commit()

        return {"status": "ok"}

    except Exception as e:
        print(f"[WEBHOOK] Error procesando webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# ============================================
# WhatsApp Sending Endpoints
# ============================================

@app.post("/tickets/{ticket_id}/send-whatsapp")
def send_ticket_whatsapp_endpoint(
    ticket_id: int,
    use_template: bool = False,
    template_name: str = "ticket_evento",
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Enviar ticket por WhatsApp al usuario.

    Args:
        ticket_id: ID del ticket a enviar
        use_template: Si es True, usa template de Meta (funciona fuera de 24h). Si es False, mensaje libre.
        template_name: Nombre del template a usar (solo si use_template=True)
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Verificar que el usuario tenga teléfono
    if not user.phone or not user.country_code:
        raise HTTPException(
            status_code=400,
            detail="El usuario no tiene número de teléfono registrado"
        )

    # Construir URL completa del ticket
    ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

    # Formatear fecha del evento
    event_date_formatted = event.event_date.strftime('%d/%m/%Y a las %H:%M')

    # Enviar por WhatsApp
    from whatsapp_client import send_ticket_whatsapp, send_ticket_with_template, WhatsAppClient

    # Verificar que WhatsApp esté disponible
    whatsapp_client = WhatsAppClient()
    if not whatsapp_client.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Servicio de WhatsApp no disponible. Verifica que esté conectado."
        )

    try:
        if use_template:
            # Usar template de Meta (funciona fuera de ventana de 24h)
            # Generar QR si está habilitado para el evento
            qr_base64 = None
            if event and hasattr(event, 'send_qr_with_whatsapp') and event.send_qr_with_whatsapp:
                try:
                    from ticket_service import ticket_service
                    qr_base64 = ticket_service.generate_qr_base64(
                        ticket_code=ticket.ticket_code,
                        user_name=user.name,
                        event_name=event.name,
                        event_date=event_date_formatted
                    )
                except Exception as e:
                    print(f"[WARNING] No se pudo generar QR para template: {e}")

            result = send_ticket_with_template(
                phone=user.phone,
                country_code=user.country_code,
                user_name=user.name,
                event_name=event.name,
                event_location=event.location,
                event_date=event_date_formatted,
                ticket_code=ticket.ticket_code,
                ticket_url=ticket_url,
                access_pin=ticket.access_pin,
                companions=ticket.companions or 0,
                template_name=template_name,
                qr_image_base64=qr_base64
            )

            if result.get("success"):
                return {
                    "message": "Ticket enviado por WhatsApp exitosamente (template)",
                    "phone": f"{user.country_code}{user.phone}",
                    "user_name": user.name,
                    "method": "template",
                    "template_used": result.get("template_used")
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al enviar template: {result.get('error')}"
                )
        else:
            # Mensaje libre (solo funciona dentro de ventana de 24h)
            success = send_ticket_whatsapp(
                phone=user.phone,
                country_code=user.country_code,
                user_name=user.name,
                event_name=event.name,
                event_location=event.location,
                event_date=event_date_formatted,
                ticket_code=ticket.ticket_code,
                ticket_url=ticket_url,
                access_pin=ticket.access_pin,
                companions=ticket.companions or 0,
                organization=organization,
                event=event
            )

            if success:
                return {
                    "message": "Ticket enviado por WhatsApp exitosamente",
                    "phone": f"{user.country_code}{user.phone}",
                    "user_name": user.name,
                    "method": "free_text"
                }
            else:
                raise HTTPException(status_code=500, detail="Error al enviar el ticket por WhatsApp")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error al enviar WhatsApp: {str(e)}"
        print(f"[ERROR] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/tickets/{ticket_id}/whatsapp-preview")
def get_whatsapp_preview(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtiene un preview del mensaje de WhatsApp que se enviará para este ticket
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Construir URL completa del ticket
    ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

    # Formatear fecha del evento
    event_date_formatted = event.event_date.strftime('%d/%m/%Y a las %H:%M')

    # Generar preview del mensaje usando template service
    from template_service import template_service

    message_preview = template_service.render_whatsapp_template(
        organization=organization,
        user_name=user.name,
        event_name=event.name,
        event_date=event_date_formatted,
        event_location=event.location,
        ticket_code=ticket.ticket_code,
        ticket_url=ticket_url,
        access_pin=ticket.access_pin,
        companions=ticket.companions or 0,
        event=event
    )

    return {
        "ticket_id": ticket_id,
        "user_name": user.name,
        "phone": f"{user.country_code}{user.phone}" if user.phone else None,
        "event_name": event.name,
        "message_preview": message_preview,
        "template_source": "evento" if event.whatsapp_template else ("organizacion" if organization and organization.whatsapp_template else "default"),
        "has_image": bool(event.whatsapp_image_path),
        "image_url": f"/{event.whatsapp_image_path}" if event.whatsapp_image_path else None,
        "send_qr_with_whatsapp": event.send_qr_with_whatsapp if hasattr(event, 'send_qr_with_whatsapp') else False
    }


@app.get("/tickets/{ticket_id}/email-preview")
def get_email_preview(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtiene un preview del email que se enviará para este ticket
    """
    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")

        user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
        event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

        # Cargar organización del evento si existe
        organization = None
        if event.organization_id:
            organization = db.query(models.Organization).filter(
                models.Organization.id == event.organization_id
            ).first()

        # Construir URL completa del ticket
        ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

        # Generar preview del email usando template service
        from template_service import template_service
        from ticket_service import ticket_service as ts

        # Formatear fecha del evento
        event_date_str = event.event_date.strftime("%d/%m/%Y %I:%M %p")

        # Generar QR code
        qr_base64 = ts.generate_qr_base64(
            ticket_code=ticket.ticket_code,
            user_name=user.name,
            event_name=event.name,
            event_date=event.event_date.isoformat()
        )

        # Renderizar HTML del email (para preview usamos base64 directo, no CID)
        html_preview = template_service.render_email_template(
            organization=organization,
            user_name=user.name,
            event_name=event.name,
            event_date=event_date_str,  # Pasar como string formateado
            event_location=event.location,
            ticket_code=ticket.ticket_code,
            ticket_url=ticket_url,
            access_pin=ticket.access_pin,
            companions=ticket.companions,
            qr_base64=qr_base64,  # Para preview en navegador, usar base64 completo
            event=event
        )

        # Obtener subject del email
        subject = template_service.get_email_subject(organization, event.name)

        return {
            "ticket_id": ticket_id,
            "user_name": user.name,
            "email": user.email,
            "event_name": event.name,
            "subject": subject,
            "html_preview": html_preview,
            "template_source": "evento" if event.email_template else ("organizacion" if organization and organization.email_template else "default"),
            "qr_base64": qr_base64
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Error en email preview: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al generar preview: {str(e)}")


@app.get("/events/{event_id}/whatsapp-template-preview")
def get_event_whatsapp_template_preview(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtiene un preview del template de WhatsApp que se usará para este evento
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Formatear fecha del evento
    event_date_formatted = event.event_date.strftime('%d/%m/%Y a las %H:%M')

    # Generar preview del mensaje usando template service
    from template_service import template_service

    # Usar valores de ejemplo
    message_preview = template_service.render_whatsapp_template(
        organization=organization,
        user_name="[Nombre del Usuario]",
        event_name=event.name,
        event_date=event_date_formatted,
        event_location=event.location,
        ticket_code="XXXX-XXXX-XXXX",
        ticket_url="https://ticket.ieeetadeo.org/ticket/...",
        access_pin="****",
        companions=0,
        event=event
    )

    return {
        "event_id": event_id,
        "event_name": event.name,
        "message_preview": message_preview,
        "template_source": "evento" if event.whatsapp_template else ("organizacion" if organization and organization.whatsapp_template else "default"),
        "template_source_name": event.name if event.whatsapp_template else (organization.name if organization and organization.whatsapp_template else "IEEE Tadeo (predeterminado)"),
        "has_image": bool(event.whatsapp_image_path),
        "image_url": f"/{event.whatsapp_image_path}" if event.whatsapp_image_path else None,
        "send_qr_with_whatsapp": event.send_qr_with_whatsapp if hasattr(event, 'send_qr_with_whatsapp') else False
    }


@app.get("/events/{event_id}/email-template-preview")
def get_event_email_template_preview(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtiene un preview del template de Email que se usará para este evento
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Generar preview del email usando template service
    from template_service import template_service
    from ticket_service import ticket_service as ts

    # Generar QR de ejemplo
    example_ticket_url = f"{BASE_URL}/ticket/ejemplo-preview"
    qr_base64 = ts.generate_qr_base64(
        ticket_code="XXXX-XXXX-XXXX",
        user_name="[Nombre del Usuario]",
        event_name=event.name,
        event_date=event.event_date.isoformat()
    )

    # Renderizar HTML del email
    html_preview = template_service.render_email_template(
        organization=organization,
        user_name="[Nombre del Usuario]",
        event_name=event.name,
        event_date=event.event_date,
        event_location=event.location,
        ticket_code="XXXX-XXXX-XXXX",
        ticket_url=example_ticket_url,
        access_pin="****",
        companions=0,
        qr_base64=qr_base64,
        event=event
    )

    # Obtener subject del email
    subject = template_service.get_email_subject(organization, event.name)

    return {
        "event_id": event_id,
        "event_name": event.name,
        "subject": subject,
        "html_preview": html_preview,
        "template_source": "evento" if event.email_template else ("organizacion" if organization and organization.email_template else "default"),
        "template_source_name": event.name if event.email_template else (organization.name if organization and organization.email_template else "IEEE Tadeo (predeterminado)"),
        "qr_base64": qr_base64
    }


@app.post("/tickets/bulk-by-tag")
def create_bulk_tickets_by_tag(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Crear tickets masivos para todos los usuarios con una etiqueta específica

    Body:
    - event_id: ID del evento
    - tag_id: ID de la etiqueta
    - companions: Número de acompañantes (0-4) para todos los tickets
    """
    event_id = data.get('event_id')
    tag_id = data.get('tag_id')
    companions = data.get('companions', 0)

    if not event_id or not tag_id:
        raise HTTPException(status_code=400, detail="event_id y tag_id son requeridos")

    # Verificar que el evento existe
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Verificar que el tag existe
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    # Obtener todos los usuarios con ese tag
    users = db.query(models.User).join(models.user_tags).filter(
        models.user_tags.c.tag_id == tag_id
    ).all()

    if not users:
        raise HTTPException(status_code=404, detail=f"No se encontraron usuarios con la etiqueta '{tag.name}'")

    # Crear tickets para cada usuario
    created_count = 0
    skipped_count = 0
    errors = []

    for user in users:
        try:
            # Verificar si el usuario ya tiene un ticket para este evento
            existing_ticket = db.query(models.Ticket).filter(
                models.Ticket.user_id == user.id,
                models.Ticket.event_id == event_id
            ).first()

            if existing_ticket:
                skipped_count += 1
                continue

            # Generar código de ticket
            ticket_code = ticket_service.generate_ticket_code(user.id, event_id)

            # Generar URL única y PIN
            unique_url = ticket_service.generate_unique_url()
            access_pin = ticket_service.generate_pin()

            # Generar QR code
            qr_path = ticket_service.generate_qr_code(
                ticket_code=ticket_code,
                user_name=user.name,
                event_name=event.name,
                event_date=event.event_date.isoformat()
            )

            # Crear ticket en la BD
            db_ticket = models.Ticket(
                ticket_code=ticket_code,
                user_id=user.id,
                event_id=event_id,
                qr_path=qr_path,
                unique_url=unique_url,
                access_pin=access_pin,
                companions=companions
            )
            db.add(db_ticket)
            created_count += 1

        except Exception as e:
            errors.append(f"Error al crear ticket para {user.name}: {str(e)}")
            continue

    # Commit de todos los tickets creados
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar tickets: {str(e)}")

    return {
        "success": True,
        "message": f"Se crearon {created_count} tickets exitosamente",
        "created_count": created_count,
        "skipped_count": skipped_count,
        "total_users": len(users),
        "tag_name": tag.name,
        "event_name": event.name,
        "errors": errors if errors else []
    }


@app.post("/tickets/send-whatsapp-by-event")
def send_tickets_whatsapp_by_event(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Enviar tickets por WhatsApp masivamente a todos los usuarios con ticket de un evento

    Body:
    - event_id: ID del evento
    """
    event_id = data.get('event_id')

    if not event_id:
        raise HTTPException(status_code=400, detail="event_id es requerido")

    # Verificar que el evento existe
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Cargar organización del evento si existe
    organization = None
    if event.organization_id:
        organization = db.query(models.Organization).filter(
            models.Organization.id == event.organization_id
        ).first()

    # Verificar que WhatsApp esté disponible
    from whatsapp_client import send_ticket_whatsapp, WhatsAppClient

    whatsapp_client = WhatsAppClient()
    if not whatsapp_client.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Servicio de WhatsApp no disponible. Verifica que esté conectado."
        )

    # Obtener todos los tickets del evento con sus usuarios
    from sqlalchemy.orm import joinedload

    tickets = db.query(models.Ticket).options(
        joinedload(models.Ticket.user)
    ).filter(
        models.Ticket.event_id == event_id
    ).all()

    if not tickets:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron tickets para el evento '{event.name}'"
        )

    # Enviar tickets por WhatsApp con delay entre mensajes
    sent_count = 0
    skipped_count = 0
    errors = []

    # Formatear fecha del evento
    event_date_formatted = event.event_date.strftime('%d/%m/%Y a las %H:%M')

    import time

    for idx, ticket in enumerate(tickets):
        user = ticket.user

        try:
            # Verificar que el usuario tenga teléfono
            if not user.phone or not user.country_code:
                skipped_count += 1
                errors.append(f"{user.name}: Sin número de teléfono")
                continue

            # Construir URL completa del ticket
            ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

            # Enviar por WhatsApp
            success = send_ticket_whatsapp(
                phone=user.phone,
                country_code=user.country_code,
                user_name=user.name,
                event_name=event.name,
                event_location=event.location,
                event_date=event_date_formatted,
                ticket_code=ticket.ticket_code,
                ticket_url=ticket_url,
                access_pin=ticket.access_pin,
                companions=ticket.companions or 0,
                organization=organization,
                event=event
            )

            if success:
                sent_count += 1
            else:
                skipped_count += 1
                errors.append(f"{user.name}: Error al enviar mensaje")

            # Delay progresivo entre mensajes para evitar colapso
            # 2 segundos base + 0.5s extra cada 10 mensajes
            base_delay = 2.0
            extra_delay = (idx // 10) * 0.5
            total_delay = min(base_delay + extra_delay, 5.0)  # Max 5 segundos

            if idx < len(tickets) - 1:  # No esperar después del último
                time.sleep(total_delay)

        except Exception as e:
            skipped_count += 1
            errors.append(f"{user.name}: {str(e)}")
            continue

    return {
        "success": True,
        "message": f"Se enviaron {sent_count} tickets exitosamente por WhatsApp",
        "sent_count": sent_count,
        "skipped_count": skipped_count,
        "total_tickets": len(tickets),
        "event_name": event.name,
        "errors": errors if errors else []
    }


@app.post("/tickets/send-whatsapp-by-event-stream")
async def send_tickets_whatsapp_by_event_stream(
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Enviar tickets por WhatsApp masivamente con Server-Sent Events para progreso en tiempo real

    Body:
    - event_id: ID del evento
    - use_template: (opcional) Si es True, usa template de Meta. Default: False
    - template_name: (opcional) Nombre del template a usar. Default: "ticket_evento"

    Retorna un stream de eventos con el formato:
    - event: progress -> Progreso de envío individual
    - event: complete -> Resumen final
    """
    event_id = data.get('event_id')
    use_template = data.get('use_template', False)
    template_name = data.get('template_name', 'ticket_evento')

    if not event_id:
        raise HTTPException(status_code=400, detail="event_id es requerido")

    # Función generadora para SSE
    async def event_generator():
        try:
            # Verificar que el evento existe
            event = db.query(models.Event).filter(models.Event.id == event_id).first()
            if not event:
                yield f"data: {json.dumps({'event': 'error', 'message': 'Evento no encontrado'})}\n\n"
                return

            # Cargar organización del evento si existe
            organization = None
            if event.organization_id:
                organization = db.query(models.Organization).filter(
                    models.Organization.id == event.organization_id
                ).first()

            # Verificar que WhatsApp esté disponible
            from whatsapp_client import send_ticket_whatsapp, send_ticket_with_template, WhatsAppClient

            whatsapp_client = WhatsAppClient()
            if not whatsapp_client.is_ready():
                yield f"data: {json.dumps({'event': 'error', 'message': 'Servicio de WhatsApp no disponible'})}\n\n"
                return

            # Obtener todos los tickets del evento con sus usuarios
            from sqlalchemy.orm import joinedload

            tickets = db.query(models.Ticket).options(
                joinedload(models.Ticket.user)
            ).filter(
                models.Ticket.event_id == event_id
            ).all()

            if not tickets:
                yield f"data: {json.dumps({'event': 'error', 'message': 'No se encontraron tickets para este evento'})}\n\n"
                return

            # Enviar evento de inicio
            yield f"data: {json.dumps({'event': 'start', 'total': len(tickets), 'event_name': event.name})}\n\n"

            # Enviar tickets por WhatsApp con delay entre mensajes
            sent_count = 0
            skipped_count = 0
            errors = []

            # Formatear fecha del evento
            event_date_formatted = event.event_date.strftime('%d/%m/%Y a las %H:%M')

            import time
            import asyncio

            for idx, ticket in enumerate(tickets):
                user = ticket.user

                try:
                    # Verificar que el usuario tenga teléfono
                    if not user.phone or not user.country_code:
                        skipped_count += 1
                        error_msg = f"{user.name}: Sin número de teléfono"
                        errors.append(error_msg)

                        # Enviar evento de skip
                        yield f"data: {json.dumps({'event': 'skip', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': 'Sin teléfono'})}\n\n"
                        continue

                    # Enviar evento de progreso - enviando
                    yield f"data: {json.dumps({'event': 'sending', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'phone': f'{user.country_code}{user.phone}'})}\n\n"

                    # Construir URL completa del ticket
                    ticket_url = f"{BASE_URL}/ticket/{ticket.unique_url}"

                    # Enviar por WhatsApp
                    if use_template:
                        # Usar template de Meta
                        # Generar QR si está habilitado para el evento
                        qr_base64 = None
                        if event and hasattr(event, 'send_qr_with_whatsapp') and event.send_qr_with_whatsapp:
                            try:
                                from ticket_service import ticket_service
                                qr_base64 = ticket_service.generate_qr_base64(
                                    ticket_code=ticket.ticket_code,
                                    user_name=user.name,
                                    event_name=event.name,
                                    event_date=event_date_formatted
                                )
                            except Exception as qr_err:
                                print(f"[WARNING] No se pudo generar QR para template: {qr_err}")

                        result = send_ticket_with_template(
                            phone=user.phone,
                            country_code=user.country_code,
                            user_name=user.name,
                            event_name=event.name,
                            event_location=event.location,
                            event_date=event_date_formatted,
                            ticket_code=ticket.ticket_code,
                            ticket_url=ticket_url,
                            access_pin=ticket.access_pin,
                            companions=ticket.companions or 0,
                            template_name=template_name,
                            qr_image_base64=qr_base64
                        )
                        success = result.get("success", False)
                        error_reason = result.get("error", "Error al enviar template")
                    else:
                        # Mensaje libre
                        success = send_ticket_whatsapp(
                            phone=user.phone,
                            country_code=user.country_code,
                            user_name=user.name,
                            event_name=event.name,
                            event_location=event.location,
                            event_date=event_date_formatted,
                            ticket_code=ticket.ticket_code,
                            ticket_url=ticket_url,
                            access_pin=ticket.access_pin,
                            companions=ticket.companions or 0,
                            organization=organization,
                            event=event
                        )
                        error_reason = "Error al enviar mensaje"

                    if success:
                        sent_count += 1
                        # Enviar evento de éxito
                        method_info = f" (template: {template_name})" if use_template else ""
                        yield f"data: {json.dumps({'event': 'success', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'phone': f'{user.country_code}{user.phone}', 'method': 'template' if use_template else 'free_text'})}\n\n"
                    else:
                        skipped_count += 1
                        error_msg = f"{user.name}: {error_reason}"
                        errors.append(error_msg)
                        # Enviar evento de error
                        yield f"data: {json.dumps({'event': 'error', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': error_reason})}\n\n"

                    # Delay progresivo entre mensajes para evitar colapso
                    # 2 segundos base + 0.5s extra cada 10 mensajes
                    base_delay = 2.0
                    extra_delay = (idx // 10) * 0.5
                    total_delay = min(base_delay + extra_delay, 5.0)  # Max 5 segundos

                    if idx < len(tickets) - 1:  # No esperar después del último
                        await asyncio.sleep(total_delay)

                except Exception as e:
                    skipped_count += 1
                    error_msg = f"{user.name}: {str(e)}"
                    errors.append(error_msg)
                    # Enviar evento de error
                    yield f"data: {json.dumps({'event': 'error', 'index': idx + 1, 'total': len(tickets), 'user': user.name, 'reason': str(e)})}\n\n"
                    continue

            # Enviar evento de finalización
            yield f"data: {json.dumps({'event': 'complete', 'sent_count': sent_count, 'skipped_count': skipped_count, 'total_tickets': len(tickets), 'errors': errors})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ========== ENDPOINTS DE VALIDACIÓN ==========

@app.post("/validate/", response_model=schemas.TicketValidationResponse)
def validate_ticket(
    validation: schemas.TicketValidation,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_validator)
):
    """
    Validar un ticket en la entrada del evento.
    Soporta validaciones múltiples según la configuración del ticket:
    - 'once': Ticket puede ser validado una sola vez
    - 'daily': Ticket puede ser validado una vez por día durante la duración del evento
    """
    try:
        # Buscar el ticket por código
        ticket = db.query(models.Ticket).filter(
            models.Ticket.ticket_code == validation.ticket_code
        ).first()

        if not ticket:
            return schemas.TicketValidationResponse(
                valid=False,
                message="Ticket no encontrado o inválido"
            )

        # Obtener usuario y evento
        user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
        event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

        if not user or not event:
            return schemas.TicketValidationResponse(
                valid=False,
                message="Error: Usuario o evento no encontrado"
            )

        # Obtener todas las validaciones previas del ticket
        previous_validations = db.query(models.ValidationLog).filter(
            models.ValidationLog.ticket_id == ticket.id,
            models.ValidationLog.success == True
        ).order_by(models.ValidationLog.validated_at.desc()).all()

        validation_count = len(previous_validations)
        current_time_bogota = get_bogota_now_naive()

        # Lógica de validación según el modo
        if ticket.validation_mode == 'once':
            # Modo: Una sola validación
            if validation_count > 0:
                last_validation = previous_validations[0]
                last_validation_time = format_datetime_bogota(
                    last_validation.validated_at,
                    '%d/%m/%Y %H:%M'
                )
                return schemas.TicketValidationResponse(
                    valid=False,
                    message=f"Ticket ya fue utilizado el {last_validation_time}",
                    validation_count=validation_count
                )

        elif ticket.validation_mode == 'daily':
            # Modo: Una validación por día
            if validation_count > 0:
                # Verificar si ya hay una validación hoy
                validations_today = [
                    v for v in previous_validations
                    if is_same_day_bogota(v.validated_at, current_time_bogota)
                ]

                if validations_today:
                    last_validation_today = validations_today[0]
                    last_validation_time = format_datetime_bogota(
                        last_validation_today.validated_at,
                        '%d/%m/%Y %H:%M'
                    )
                    return schemas.TicketValidationResponse(
                        valid=False,
                        message=f"Ticket ya fue validado hoy a las {last_validation_time}. En modo diario solo se permite 1 validación por día.",
                        validation_count=validation_count
                    )

                # Hay validaciones previas pero no de hoy - es válido
                # Informar que es una validación adicional
                is_second_validation = True
                last_validation = previous_validations[0]
                last_validation_date = format_datetime_bogota(
                    last_validation.validated_at,
                    '%d/%m/%Y'
                )
                message = f"Ticket válido - Acceso permitido. Validación #{validation_count + 1}. Última validación: {last_validation_date}"

        # Si llegamos aquí, el ticket es válido
        # Crear registro de validación
        validation_log = models.ValidationLog(
            ticket_id=ticket.id,
            validator_id=current_user.id,
            validated_at=current_time_bogota,
            success=True,
            notes=f"Validación en modo {ticket.validation_mode}"
        )
        db.add(validation_log)

        # Actualizar campos deprecated para compatibilidad
        ticket.is_used = True
        ticket.used_at = current_time_bogota

        db.commit()
        db.refresh(ticket)

        # Preparar mensaje apropiado
        if ticket.validation_mode == 'once':
            message = "Ticket válido - Acceso permitido"
        elif ticket.validation_mode == 'daily' and validation_count == 0:
            message = "Ticket válido - Acceso permitido. Primera validación"
        else:
            # Ya definido arriba para validaciones adicionales
            pass

        return schemas.TicketValidationResponse(
            valid=True,
            message=message,
            ticket=schemas.TicketResponse.model_validate(ticket),
            user=schemas.UserResponse.model_validate(user),
            event=schemas.EventResponse.model_validate(event),
            validation_count=validation_count + 1,
            is_second_validation=(validation_count > 0)
        )

    except Exception as e:
        db.rollback()
        return schemas.TicketValidationResponse(
            valid=False,
            message=f"Error al validar ticket: {str(e)}"
        )


@app.post("/validate/scan/", response_model=schemas.TicketValidationResponse)
def validate_scanned_qr(
    encrypted_data: str,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_validator)
):
    """Validar un QR escaneado (datos encriptados)"""
    try:
        # Desencriptar datos del QR
        qr_data = ticket_service.decrypt_qr_data(encrypted_data)
        ticket_code = qr_data.get("ticket_code")

        # Validar usando el código de ticket
        return validate_ticket(schemas.TicketValidation(ticket_code=ticket_code), db, current_user)

    except ValueError as e:
        return schemas.TicketValidationResponse(
            valid=False,
            message=str(e)
        )


class QRDataValidation(BaseModel):
    qr_data: str

@app.post("/validate/qr", response_model=schemas.TicketValidationResponse)
def validate_qr_data(
    data: QRDataValidation,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_validator)
):
    """Validar QR desde datos escaneados - recibe datos encriptados del QR"""
    try:
        # Intentar desencriptar los datos del QR
        decrypted_data = ticket_service.decrypt_qr_data(data.qr_data)
        ticket_code = decrypted_data.get("ticket_code")

        # Validar usando el código de ticket
        return validate_ticket(schemas.TicketValidation(ticket_code=ticket_code), db, current_user)

    except Exception as e:
        return schemas.TicketValidationResponse(
            valid=False,
            message=f"QR inválido o corrupto: {str(e)}"
        )


# ========== ENDPOINTS DE GESTIÓN DE MODO DE VALIDACIÓN ==========

class ChangeValidationModeRequest(BaseModel):
    """Request para cambiar modo de validación"""
    validation_mode: str
    ticket_ids: Optional[List[int]] = None  # IDs específicos de tickets (opcional)

    @validator('validation_mode')
    def validate_mode(cls, v):
        if v not in ['once', 'daily']:
            raise ValueError('El modo de validación debe ser "once" o "daily"')
        return v


@app.post("/events/{event_id}/change-validation-mode")
def change_event_validation_mode(
    event_id: int,
    request: ChangeValidationModeRequest,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Cambiar el modo de validación de todos los tickets de un evento.
    Útil para eventos de varios días donde se necesita validación diaria.
    """
    # Verificar que el evento existe
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Si se especificaron ticket_ids, solo cambiar esos tickets
    if request.ticket_ids:
        tickets = db.query(models.Ticket).filter(
            models.Ticket.event_id == event_id,
            models.Ticket.id.in_(request.ticket_ids)
        ).all()
    else:
        # Cambiar todos los tickets del evento
        tickets = db.query(models.Ticket).filter(
            models.Ticket.event_id == event_id
        ).all()

    if not tickets:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron tickets para este evento"
        )

    # Actualizar modo de validación
    updated_count = 0
    for ticket in tickets:
        ticket.validation_mode = request.validation_mode
        updated_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"{updated_count} tickets actualizados a modo '{request.validation_mode}'",
        "event_id": event_id,
        "event_name": event.name,
        "updated_count": updated_count,
        "validation_mode": request.validation_mode
    }


@app.post("/tickets/batch-change-validation-mode")
def batch_change_validation_mode(
    request: ChangeValidationModeRequest,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Cambiar el modo de validación de múltiples tickets por sus IDs.
    """
    if not request.ticket_ids:
        raise HTTPException(
            status_code=400,
            detail="Debes especificar al menos un ticket_id"
        )

    tickets = db.query(models.Ticket).filter(
        models.Ticket.id.in_(request.ticket_ids)
    ).all()

    if not tickets:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron tickets con los IDs especificados"
        )

    updated_count = 0
    for ticket in tickets:
        ticket.validation_mode = request.validation_mode
        updated_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"{updated_count} tickets actualizados a modo '{request.validation_mode}'",
        "updated_count": updated_count,
        "validation_mode": request.validation_mode,
        "ticket_ids": request.ticket_ids
    }


@app.get("/events/{event_id}/validation-stats")
def get_event_validation_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtener estadísticas de validación para un evento.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Contar tickets por modo
    total_tickets = db.query(func.count(models.Ticket.id)).filter(
        models.Ticket.event_id == event_id
    ).scalar()

    once_tickets = db.query(func.count(models.Ticket.id)).filter(
        models.Ticket.event_id == event_id,
        models.Ticket.validation_mode == 'once'
    ).scalar()

    daily_tickets = db.query(func.count(models.Ticket.id)).filter(
        models.Ticket.event_id == event_id,
        models.Ticket.validation_mode == 'daily'
    ).scalar()

    # Contar validaciones
    total_validations = db.query(func.count(models.ValidationLog.id)).join(
        models.Ticket
    ).filter(
        models.Ticket.event_id == event_id,
        models.ValidationLog.success == True
    ).scalar()

    validated_tickets = db.query(func.count(func.distinct(models.ValidationLog.ticket_id))).join(
        models.Ticket
    ).filter(
        models.Ticket.event_id == event_id,
        models.ValidationLog.success == True
    ).scalar()

    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_tickets": total_tickets,
        "validation_modes": {
            "once": once_tickets,
            "daily": daily_tickets
        },
        "validations": {
            "total_validations": total_validations,
            "validated_tickets": validated_tickets,
            "pending_tickets": total_tickets - validated_tickets
        }
    }


@app.get("/events/{event_id}/validation-history")
def get_event_validation_history(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Obtener historial completo de validaciones para un evento, agrupado por día.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Obtener todas las validaciones exitosas del evento con información completa
    validations = db.query(
        models.ValidationLog,
        models.Ticket,
        models.User,
        models.AdminUser
    ).join(
        models.Ticket, models.ValidationLog.ticket_id == models.Ticket.id
    ).join(
        models.User, models.Ticket.user_id == models.User.id
    ).join(
        models.AdminUser, models.ValidationLog.validator_id == models.AdminUser.id
    ).filter(
        models.Ticket.event_id == event_id,
        models.ValidationLog.success == True
    ).order_by(
        models.ValidationLog.validated_at.desc()
    ).all()

    # Agrupar validaciones por día
    from collections import defaultdict
    from timezone_utils import format_datetime_bogota, get_date_only_bogota

    validations_by_day = defaultdict(list)

    for val_log, ticket, user, validator in validations:
        # Obtener fecha en formato legible
        date_str = format_datetime_bogota(val_log.validated_at, '%A %d de %B, %Y')

        # Contar cuántas validaciones tiene este ticket
        ticket_validation_count = db.query(func.count(models.ValidationLog.id)).filter(
            models.ValidationLog.ticket_id == ticket.id,
            models.ValidationLog.success == True,
            models.ValidationLog.id <= val_log.id
        ).scalar()

        validations_by_day[date_str].append({
            "validation_id": val_log.id,
            "ticket_id": ticket.id,
            "user_name": user.name,
            "user_email": user.email,
            "validation_mode": ticket.validation_mode,
            "validator_name": validator.full_name or validator.username,
            "validated_at": val_log.validated_at.isoformat(),
            "notes": val_log.notes,
            "validation_count": ticket_validation_count
        })

    # Convertir a lista ordenada por fecha (más reciente primero)
    validations_list = [
        {
            "date": date,
            "validations": validations
        }
        for date, validations in sorted(validations_by_day.items(), reverse=True)
    ]

    # Estadísticas generales
    total_validations = len(validations)
    unique_tickets = len(set(val_log.ticket_id for val_log, _, _, _ in validations))

    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_validations": total_validations,
        "unique_tickets": unique_tickets,
        "validations_by_day": validations_list
    }


@app.get("/validator/my-validations-history")
def get_my_validations_history(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(get_current_user)
):
    """
    Obtener historial de validaciones realizadas por el usuario actual, agrupadas por día.
    Solo incluye las validaciones realizadas por el validador logueado.
    """
    # Obtener todas las validaciones exitosas del usuario actual
    validations = db.query(
        models.ValidationLog,
        models.Ticket,
        models.User,
        models.Event
    ).join(
        models.Ticket, models.ValidationLog.ticket_id == models.Ticket.id
    ).join(
        models.User, models.Ticket.user_id == models.User.id
    ).join(
        models.Event, models.Ticket.event_id == models.Event.id
    ).filter(
        models.ValidationLog.validator_id == current_user.id,
        models.ValidationLog.success == True
    ).order_by(
        models.ValidationLog.validated_at.desc()
    ).all()

    # Agrupar validaciones por día
    from collections import defaultdict
    from timezone_utils import format_datetime_bogota

    validations_by_day = defaultdict(list)

    for val_log, ticket, user, event in validations:
        # Obtener fecha en formato legible
        date_str = format_datetime_bogota(val_log.validated_at, '%A %d de %B, %Y')

        # Contar cuántas validaciones tiene este ticket
        ticket_validation_count = db.query(func.count(models.ValidationLog.id)).filter(
            models.ValidationLog.ticket_id == ticket.id,
            models.ValidationLog.success == True,
            models.ValidationLog.id <= val_log.id
        ).scalar()

        validations_by_day[date_str].append({
            "validation_id": val_log.id,
            "ticket_id": ticket.id,
            "ticket_code": ticket.ticket_code,
            "user_name": user.name,
            "user_email": user.email,
            "event_name": event.name,
            "event_id": event.id,
            "validation_mode": ticket.validation_mode,
            "validated_at": format_datetime_bogota(val_log.validated_at, '%H:%M:%S'),
            "validation_count": ticket_validation_count,
            "companions": ticket.companions
        })

    # Convertir a lista ordenada por fecha (más reciente primero)
    validations_list = [
        {
            "date": date,
            "count": len(validations),
            "validations": validations
        }
        for date, validations in sorted(validations_by_day.items(), reverse=True)
    ]

    # Estadísticas generales
    total_validations = len(validations)
    unique_tickets = len(set(val_log.ticket_id for val_log, _, _, _ in validations))
    unique_events = len(set(event.id for _, _, _, event in validations))

    return {
        "validator_name": current_user.full_name or current_user.username,
        "total_validations": total_validations,
        "unique_tickets": unique_tickets,
        "unique_events": unique_events,
        "validations_by_day": validations_list
    }


# ========== RUTAS DE ADMINISTRACIÓN ==========

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {
        "request": request
    })


@app.get("/admin/access", response_class=HTMLResponse)
async def admin_access_management(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de validadores (solo admin)"""
    validators = db.query(models.AdminUser).all()

    # Convertir validators a formato serializable
    validators_list = []
    for v in validators:
        v_dict = {
            "id": v.id,
            "username": v.username,
            "email": v.email,
            "full_name": v.full_name,
            "role": v.role.value if v.role else None,  # Convertir enum a string
            "is_active": v.is_active,
            "created_at": v.created_at,
            "access_start": v.access_start,
            "access_end": v.access_end
        }
        validators_list.append(type('Validator', (), v_dict))

    return templates.TemplateResponse("access_management.html", {
        "request": request,
        "validators": validators_list
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Dashboard de administración"""
    # Obtener estadísticas básicas
    total_users = db.query(func.count(models.User.id)).scalar()
    total_events = db.query(func.count(models.Event.id)).scalar()
    total_tickets = db.query(func.count(models.Ticket.id)).scalar()
    tickets_used = db.query(func.count(models.Ticket.id)).filter(models.Ticket.is_used == True).scalar()

    # Obtener eventos activos (futuros o en curso) con conteo de tickets
    from datetime import datetime
    from sqlalchemy import or_
    now = datetime.now()

    active_events = db.query(
        models.Event,
        func.count(models.Ticket.id).label('ticket_count')
    ).outerjoin(models.Ticket).filter(
        models.Event.is_active == True,
        # Evento futuro O evento de varios días aún en curso
        or_(
            models.Event.event_date >= now,
            models.Event.event_end_date >= now
        )
    ).group_by(models.Event.id).order_by(models.Event.event_date.asc()).limit(4).all()

    active_events_list = []
    for event, ticket_count in active_events:
        event_dict = event.__dict__.copy()
        event_dict['ticket_count'] = ticket_count
        active_events_list.append(type('Event', (), event_dict))

    # Obtener eventos pasados (últimos 4) con conteo de tickets
    from sqlalchemy import and_
    past_events = db.query(
        models.Event,
        func.count(models.Ticket.id).label('ticket_count')
    ).outerjoin(models.Ticket).filter(
        models.Event.event_date < now,
        # Si tiene fecha de fin, también debe haber pasado
        or_(
            models.Event.event_end_date == None,
            models.Event.event_end_date < now
        )
    ).group_by(models.Event.id).order_by(models.Event.event_date.desc()).limit(4).all()

    past_events_list = []
    for event, ticket_count in past_events:
        event_dict = event.__dict__.copy()
        event_dict['ticket_count'] = ticket_count
        past_events_list.append(type('Event', (), event_dict))

    # Obtener distribución por universidad
    university_stats = db.query(
        models.University.name,
        models.University.short_name,
        func.count(models.User.id).label('count')
    ).outerjoin(
        models.User, models.University.id == models.User.university_id
    ).group_by(
        models.University.id
    ).order_by(
        desc('count')
    ).all()

    # Agregar usuarios sin universidad asignada
    users_without_university = db.query(func.count(models.User.id)).filter(
        models.User.university_id == None
    ).scalar()

    university_stats_list = []
    for name, short_name, count in university_stats:
        if count > 0:  # Solo incluir universidades con usuarios
            university_stats_list.append({
                'name': name,
                'short_name': short_name,
                'count': count
            })

    # Agregar usuarios sin universidad si existen
    if users_without_university > 0:
        university_stats_list.append({
            'name': 'Sin Universidad',
            'short_name': 'N/A',
            'count': users_without_university
        })

    # Obtener estadísticas de membresía IEEE
    ieee_members = db.query(func.count(models.User.id)).filter(
        models.User.is_ieee_member == True
    ).scalar()
    non_ieee_members = db.query(func.count(models.User.id)).filter(
        models.User.is_ieee_member == False
    ).scalar()

    stats = {
        "total_users": total_users,
        "total_events": total_events,
        "total_tickets": total_tickets,
        "tickets_used": tickets_used,
        "ieee_members": ieee_members,
        "non_ieee_members": non_ieee_members
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "active_events": active_events_list,
        "past_events": past_events_list,
        "university_stats": university_stats_list
    })


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de usuarios - Con soporte para tags"""
    from birthday_utils import get_birthday_status

    # Obtener usuarios con conteo de tickets
    from sqlalchemy.orm import joinedload

    users = db.query(
        models.User,
        func.count(models.Ticket.id).label('ticket_count')
    ).options(
        joinedload(models.User.university),
        joinedload(models.User.tags)
    ).outerjoin(models.Ticket).group_by(models.User.id).all()

    users_list = []
    for user, ticket_count in users:
        # Obtener información del cumpleaños
        birthday_status = get_birthday_status(user.birthday)

        # Crear objeto con atributos accesibles directamente
        class UserWrapper:
            pass

        user_obj = UserWrapper()
        user_obj.id = user.id
        user_obj.name = user.name
        user_obj.nick = user.nick
        user_obj.email = user.email
        user_obj.country_code = user.country_code
        user_obj.phone = user.phone
        user_obj.identification = user.identification
        user_obj.university_id = user.university_id
        user_obj.is_ieee_member = user.is_ieee_member
        user_obj.birthday = user.birthday
        user_obj.created_at = user.created_at
        user_obj.ticket_count = ticket_count
        user_obj.university = user.university
        user_obj.tags = user.tags
        user_obj.birthday_status = birthday_status

        users_list.append(user_obj)

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users_list
    })


@app.get("/admin/universities", response_class=HTMLResponse)
async def admin_universities(
    request: Request
):
    """Página de gestión de universidades"""
    return templates.TemplateResponse("universities.html", {
        "request": request
    })


@app.get("/admin/organizations", response_class=HTMLResponse)
async def admin_organizations(
    request: Request
):
    """Página de gestión de organizaciones"""
    return templates.TemplateResponse("organizations.html", {
        "request": request
    })


@app.get("/admin/events", response_class=HTMLResponse)
async def admin_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de eventos"""
    from sqlalchemy.orm import joinedload

    events = db.query(
        models.Event,
        func.count(models.Ticket.id).label('ticket_count')
    ).options(joinedload(models.Event.organization)).outerjoin(models.Ticket).group_by(models.Event.id).all()

    events_list = []
    for event, ticket_count in events:
        # Agregar el ticket_count como atributo temporal del evento
        event.ticket_count = ticket_count
        events_list.append(event)

    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events_list
    })


@app.get("/admin/events/{event_id}/edit", response_class=HTMLResponse)
async def admin_edit_event(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db)
):
    """Página para editar un evento"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    return templates.TemplateResponse("edit_event.html", {
        "request": request,
        "event": event
    })


@app.get("/admin/tickets", response_class=HTMLResponse)
async def admin_tickets(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de tickets"""
    tickets = db.query(models.Ticket).all()
    users = db.query(models.User).all()
    events = db.query(models.Event).filter(models.Event.is_active == True).all()

    # Agregar nombres de usuario y evento a los tickets
    tickets_list = []
    for ticket in tickets:
        user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
        event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()
        ticket_dict = ticket.__dict__.copy()
        ticket_dict['user_name'] = user.name if user else 'N/A'
        ticket_dict['event_name'] = event.name if event else 'N/A'
        tickets_list.append(type('Ticket', (), ticket_dict))

    return templates.TemplateResponse("tickets.html", {
        "request": request,
        "tickets": tickets_list,
        "users": users,
        "events": events
    })


@app.get("/admin/validate", response_class=HTMLResponse)
async def admin_validate(
    request: Request
):
    """Página de validación de tickets"""
    return templates.TemplateResponse("validate.html", {
        "request": request
    })


@app.get("/admin/messages", response_class=HTMLResponse)
async def admin_messages(
    request: Request
):
    """Página de envío de mensajes masivos"""
    return templates.TemplateResponse("messages.html", {
        "request": request
    })


@app.get("/admin/campaigns", response_class=HTMLResponse)
async def admin_campaigns(
    request: Request
):
    """Página de histórico de campañas de mensajes"""
    return templates.TemplateResponse("campaigns.html", {
        "request": request
    })


@app.get("/admin/campaigns/{campaign_id}", response_class=HTMLResponse)
async def admin_campaign_details(
    request: Request,
    campaign_id: int
):
    """Página de detalles de una campaña específica"""
    return templates.TemplateResponse("campaign_details.html", {
        "request": request,
        "campaign_id": campaign_id
    })


@app.post("/messages/bulk-send")
async def bulk_send_messages(
    user_ids: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    link: str = Form(""),
    link_text: str = Form(""),
    send_email: str = Form("false"),
    send_whatsapp: str = Form("false"),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Enviar mensajes masivos a usuarios seleccionados con tracking completo"""
    import json
    import base64
    from PIL import Image
    from io import BytesIO
    from pathlib import Path

    # Parsear IDs de usuarios
    try:
        user_id_list = json.loads(user_ids)
    except:
        raise HTTPException(status_code=400, detail="Formato de IDs inválido")

    # Convertir booleanos
    send_email_bool = send_email.lower() == "true"
    send_whatsapp_bool = send_whatsapp.lower() == "true"

    if not send_email_bool and not send_whatsapp_bool:
        raise HTTPException(status_code=400, detail="Debes seleccionar al menos un canal de envío")

    # Procesar imagen si fue proporcionada
    image_url = None
    image_path_for_db = None
    if image and image.filename:
        # Leer y procesar imagen
        image_content = await image.read()
        img = Image.open(BytesIO(image_content))

        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # Redimensionar
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Comprimir
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        compressed_content = buffer.getvalue()

        # Guardar en directorio message_images
        import os
        import time
        message_images_dir = "static/message_images"
        os.makedirs(message_images_dir, exist_ok=True)

        timestamp = int(time.time())
        image_filename = f"msg_{timestamp}_{image.filename}"
        image_path = os.path.join(message_images_dir, image_filename)

        with open(image_path, 'wb') as f:
            f.write(compressed_content)

        image_path_for_db = image_path

        # Convertir a base64 data URL
        image_base64 = base64.b64encode(compressed_content).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{image_base64}"

        print(f"[INFO] Imagen guardada: {image_path} ({len(compressed_content)/1024:.2f}KB)")

    # Obtener usuarios
    users = db.query(models.User).filter(models.User.id.in_(user_id_list)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios")

    # CREAR CAMPAÑA
    campaign = models.MessageCampaign(
        subject=subject,
        message=message,
        link=link if link else None,
        link_text=link_text if link_text else None,
        has_image=image_url is not None,
        image_path=image_path_for_db,
        send_email=send_email_bool,
        send_whatsapp=send_whatsapp_bool,
        total_recipients=len(users),
        created_by=current_user.id
    )
    db.add(campaign)
    db.flush()  # Get campaign ID without committing

    print(f"[CAMPAIGN] Created campaign ID {campaign.id}: '{subject}' to {len(users)} users")

    import time

    # Enviar mensajes y crear registros de destinatarios
    for idx, user in enumerate(users):
        # Personalizar mensaje
        display_name = user.nick if user.nick else user.name.split()[0]
        personalized_message = message.replace("{nombre}", display_name)

        # Crear registro de destinatario
        recipient = models.MessageRecipient(
            campaign_id=campaign.id,
            user_id=user.id
        )
        db.add(recipient)
        db.flush()  # Get recipient ID

        # Enviar por email
        if send_email_bool:
            try:
                success = email_service.send_bulk_message(
                    to_email=user.email,
                    user_name=display_name,
                    subject=subject,
                    message=personalized_message,
                    link=link if link else None,
                    link_text=link_text if link_text else None,
                    image_url=image_url
                )

                recipient.email_sent = success
                recipient.email_sent_at = get_bogota_now_naive() if success else None

                if success:
                    campaign.emails_sent += 1
                else:
                    campaign.emails_failed += 1
                    recipient.email_error = "Email sending failed"

            except Exception as e:
                campaign.emails_failed += 1
                recipient.email_sent = False
                recipient.email_error = str(e)
                print(f"[ERROR] Email to {user.email}: {str(e)}")

        # Enviar por WhatsApp
        if send_whatsapp_bool and user.phone and user.country_code:
            try:
                from whatsapp_client import send_bulk_whatsapp, WhatsAppClient

                whatsapp_client = WhatsAppClient()
                if whatsapp_client.is_ready():
                    result = send_bulk_whatsapp(
                        phone=user.phone,
                        country_code=user.country_code,
                        user_name=display_name,
                        subject=subject,
                        message=personalized_message,
                        link=link if link else None,
                        image_base64=image_url if image_url else None
                    )

                    if result.get("success"):
                        recipient.whatsapp_sent = True
                        recipient.whatsapp_sent_at = get_bogota_now_naive()
                        recipient.whatsapp_message_id = result.get("message_id")
                        recipient.whatsapp_status = "pending"
                        campaign.whatsapp_sent += 1
                    else:
                        recipient.whatsapp_sent = False
                        recipient.whatsapp_error = result.get("error", "Unknown error")
                        campaign.whatsapp_failed += 1
                else:
                    recipient.whatsapp_sent = False
                    recipient.whatsapp_error = "WhatsApp service not ready"
                    campaign.whatsapp_failed += 1

            except Exception as e:
                campaign.whatsapp_failed += 1
                recipient.whatsapp_sent = False
                recipient.whatsapp_error = str(e)
                print(f"[ERROR] WhatsApp to {user.phone}: {str(e)}")

        # Delay progresivo entre mensajes para evitar colapso del servicio de WhatsApp
        # Solo si se envió WhatsApp y no es el último usuario
        if send_whatsapp_bool and idx < len(users) - 1:
            # 2 segundos base + 0.5s extra cada 10 mensajes (max 5 segundos)
            base_delay = 2.0
            extra_delay = (idx // 10) * 0.5
            total_delay = min(base_delay + extra_delay, 5.0)
            time.sleep(total_delay)

    # Commit todas las transacciones
    db.commit()

    print(f"[CAMPAIGN] Completed campaign ID {campaign.id}:")
    print(f"  Emails: {campaign.emails_sent} sent, {campaign.emails_failed} failed")
    print(f"  WhatsApp: {campaign.whatsapp_sent} sent, {campaign.whatsapp_failed} failed")

    return {
        "success": True,
        "campaign_id": campaign.id,
        "total_recipients": len(users),
        "emails_sent": campaign.emails_sent,
        "emails_failed": campaign.emails_failed,
        "whatsapp_sent": campaign.whatsapp_sent,
        "whatsapp_failed": campaign.whatsapp_failed
    }


# ========== ENDPOINTS DE CAMPAÑAS ==========

@app.get("/campaigns/")
def list_campaigns(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todas las campañas de mensajes"""
    campaigns = db.query(models.MessageCampaign).order_by(
        desc(models.MessageCampaign.created_at)
    ).offset(skip).limit(limit).all()

    result = []
    for campaign in campaigns:
        # Get creator info
        creator = db.query(models.AdminUser).filter(
            models.AdminUser.id == campaign.created_by
        ).first()

        result.append({
            "id": campaign.id,
            "subject": campaign.subject,
            "message": campaign.message[:100] + "..." if len(campaign.message) > 100 else campaign.message,
            "has_image": campaign.has_image,
            "send_email": campaign.send_email,
            "send_whatsapp": campaign.send_whatsapp,
            "total_recipients": campaign.total_recipients,
            "emails_sent": campaign.emails_sent,
            "emails_failed": campaign.emails_failed,
            "whatsapp_sent": campaign.whatsapp_sent,
            "whatsapp_failed": campaign.whatsapp_failed,
            "created_by_name": creator.full_name if creator else "Unknown",
            "created_at": campaign.created_at.isoformat()
        })

    return result


@app.get("/campaigns/{campaign_id}")
def get_campaign_details(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener detalles de una campaña con todos sus destinatarios"""
    campaign = db.query(models.MessageCampaign).filter(
        models.MessageCampaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    # Get creator info
    creator = db.query(models.AdminUser).filter(
        models.AdminUser.id == campaign.created_by
    ).first()

    # Get recipients with user info
    recipients = db.query(
        models.MessageRecipient,
        models.User
    ).join(
        models.User, models.MessageRecipient.user_id == models.User.id
    ).filter(
        models.MessageRecipient.campaign_id == campaign_id
    ).all()

    recipients_data = []
    for recipient, user in recipients:
        recipients_data.append({
            "recipient_id": recipient.id,
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "user_phone": user.phone,
            "email_sent": recipient.email_sent,
            "email_sent_at": recipient.email_sent_at.isoformat() if recipient.email_sent_at else None,
            "email_error": recipient.email_error,
            "whatsapp_sent": recipient.whatsapp_sent,
            "whatsapp_sent_at": recipient.whatsapp_sent_at.isoformat() if recipient.whatsapp_sent_at else None,
            "whatsapp_status": recipient.whatsapp_status,
            "whatsapp_status_updated_at": recipient.whatsapp_status_updated_at.isoformat() if recipient.whatsapp_status_updated_at else None,
            "whatsapp_error": recipient.whatsapp_error
        })

    # Calculate WhatsApp delivery stats
    whatsapp_delivered = sum(1 for r, u in recipients if r.whatsapp_status == "delivered")
    whatsapp_read = sum(1 for r, u in recipients if r.whatsapp_status == "read")

    return {
        "id": campaign.id,
        "subject": campaign.subject,
        "message": campaign.message,
        "link": campaign.link,
        "link_text": campaign.link_text,
        "has_image": campaign.has_image,
        "image_path": campaign.image_path,
        "send_email": campaign.send_email,
        "send_whatsapp": campaign.send_whatsapp,
        "total_recipients": campaign.total_recipients,
        "emails_sent": campaign.emails_sent,
        "emails_failed": campaign.emails_failed,
        "whatsapp_sent": campaign.whatsapp_sent,
        "whatsapp_failed": campaign.whatsapp_failed,
        "whatsapp_delivered": whatsapp_delivered,
        "whatsapp_read": whatsapp_read,
        "created_by": campaign.created_by,
        "created_by_name": creator.full_name if creator else "Unknown",
        "created_at": campaign.created_at.isoformat(),
        "recipients": recipients_data
    }


@app.delete("/campaigns/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar una campaña y todos sus destinatarios"""
    campaign = db.query(models.MessageCampaign).filter(
        models.MessageCampaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")

    # Eliminar imagen si existe
    if campaign.image_path:
        import os
        try:
            if os.path.exists(campaign.image_path):
                os.remove(campaign.image_path)
                print(f"[INFO] Imagen eliminada: {campaign.image_path}")
        except Exception as e:
            print(f"[WARNING] Error al eliminar imagen: {e}")

    # Los destinatarios se eliminan automáticamente por cascade
    db.delete(campaign)
    db.commit()

    return {
        "success": True,
        "message": "Campaña eliminada exitosamente",
        "campaign_id": campaign_id
    }


# ========== WEBHOOKS ==========

@app.post("/webhooks/whatsapp-status")
async def whatsapp_status_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """
    Recibe actualizaciones de estado de WhatsApp desde el servicio Node.js

    Expected payload:
    {
        "message_id": "whatsapp_message_id",
        "status": "pending|sent|delivered|read|failed",
        "ack": 0|1|2|3|4|5
    }
    """
    try:
        message_id = webhook_data.get("message_id")
        status = webhook_data.get("status")

        if not message_id or not status:
            return {"success": False, "error": "Missing message_id or status"}

        # Buscar el destinatario por whatsapp_message_id
        recipient = db.query(models.MessageRecipient).filter(
            models.MessageRecipient.whatsapp_message_id == message_id
        ).first()

        if not recipient:
            # No encontrado - puede ser un mensaje que no es de campaña
            return {
                "success": True,
                "message": "Message ID not tracked in campaigns"
            }

        # Actualizar estado
        recipient.whatsapp_status = status
        recipient.whatsapp_status_updated_at = get_bogota_now_naive()

        # Si el estado es "failed", marcar como no enviado
        if status == "failed":
            recipient.whatsapp_sent = False

        db.commit()

        print(f"[WEBHOOK] Estado actualizado: {message_id} -> {status}")

        return {
            "success": True,
            "message": "Status updated",
            "recipient_id": recipient.id,
            "new_status": status
        }

    except Exception as e:
        print(f"[WEBHOOK ERROR] {str(e)}")
        return {"success": False, "error": str(e)}


# ========== ENDPOINTS PÚBLICOS DE TICKETS ==========

@app.get("/ticket/{unique_url}", response_class=HTMLResponse)
async def view_ticket_pin_form(
    unique_url: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Muestra el formulario para ingresar PIN del ticket"""
    # Verificar que el ticket existe
    ticket = db.query(models.Ticket).filter(
        models.Ticket.unique_url == unique_url
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return templates.TemplateResponse("ticket_pin.html", {
        "request": request,
        "unique_url": unique_url
    })


@app.post("/ticket/{unique_url}/verify")
async def verify_ticket_pin(
    unique_url: str,
    pin: str,
    db: Session = Depends(get_db)
):
    """Verifica el PIN y retorna la información del ticket"""
    ticket = db.query(models.Ticket).filter(
        models.Ticket.unique_url == unique_url
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if ticket.access_pin != pin:
        raise HTTPException(status_code=401, detail="PIN incorrecto")

    # Obtener información del usuario y evento
    user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

    # Obtener nombre de la universidad
    university_name = None
    if user.university_id:
        university = db.query(models.University).filter(
            models.University.id == user.university_id
        ).first()
        if university:
            university_name = university.name

    # Generar QR en base64
    qr_base64 = ticket_service.generate_qr_base64(
        ticket_code=ticket.ticket_code,
        user_name=user.name,
        event_name=event.name,
        event_date=event.event_date.isoformat()
    )

    return {
        "valid": True,
        "ticket": {
            "ticket_code": ticket.ticket_code,
            "qr_code": qr_base64,
            "is_used": ticket.is_used,
            "used_at": ticket.used_at.isoformat() if ticket.used_at else None,
            "companions": ticket.companions,
            "created_at": ticket.created_at.isoformat()
        },
        "user": {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "identification": user.identification,
            "university": university_name
        },
        "event": {
            "name": event.name,
            "description": event.description,
            "location": event.location,
            "event_date": event.event_date.isoformat()
        }
    }


# ========== ENDPOINT PRINCIPAL ==========

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal - redirige al login"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IEEE Tadeo Control System</title>
        <meta http-equiv="refresh" content="0; url=/login">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            <h1>IEEE Tadeo Control System</h1>
            <p>Redirigiendo al login...</p>
            <p><a href="/login" style="color: white;">Haz clic aquí si no eres redirigido automáticamente</a></p>
        </div>
    </body>
    </html>
    """


# ========== PÁGINAS LEGALES (Para Meta/Facebook) ==========

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Política de Privacidad"""
    return templates.TemplateResponse("privacy.html", {"request": request})


@app.get("/terms", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    """Términos del Servicio"""
    return templates.TemplateResponse("terms.html", {"request": request})


@app.get("/data-deletion", response_class=HTMLResponse)
async def data_deletion(request: Request):
    """Instrucciones para Eliminación de Datos"""
    return templates.TemplateResponse("data_deletion.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Endpoint para servir QR codes (alternativa a archivos estáticos)
from fastapi.responses import FileResponse
import os

@app.get("/api/qr/{ticket_code}")
async def get_qr_code(ticket_code: str):
    """Sirve el código QR de un ticket"""
    # Usar ruta absoluta desde el directorio de la aplicación
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qr_path = os.path.join(base_dir, "qr_codes", f"{ticket_code}.png")

    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail=f"QR code not found: {ticket_code}")


# ========== ENDPOINTS DE GESTIÓN DE WHATSAPP ==========

@app.get("/admin/whatsapp", response_class=HTMLResponse)
async def admin_whatsapp(
    request: Request
):
    """Página de gestión de WhatsApp"""
    return templates.TemplateResponse("whatsapp_admin.html", {
        "request": request
    })


@app.get("/whatsapp/status")
def get_whatsapp_status(
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener estado del servicio de WhatsApp"""
    try:
        from whatsapp_client import WhatsAppClient
        client = WhatsAppClient()
        status = client.get_status()
        return status
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "message": "Error al conectar con el servicio de WhatsApp"
        }


@app.post("/whatsapp/restart")
def restart_whatsapp(
    current_user: models.AdminUser = Depends(require_admin)
):
    """Verificar conexion con la API de WhatsApp (Meta Cloud API no requiere reinicio)"""
    try:
        from whatsapp_client import WhatsAppClient

        client = WhatsAppClient()
        result = client.restart()

        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "API de WhatsApp funcionando correctamente"),
                "details": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error al verificar: {result.get('error', 'Error desconocido')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar WhatsApp: {str(e)}"
        )


class TestMessageRequest(BaseModel):
    phone: str
    message: str


@app.post("/whatsapp/test-message")
def send_whatsapp_test_message(
    request: TestMessageRequest,
    current_user: models.AdminUser = Depends(require_admin)
):
    """Enviar mensaje de prueba por WhatsApp"""
    try:
        from whatsapp_client import WhatsAppClient

        client = WhatsAppClient()

        if not client.is_ready():
            raise HTTPException(
                status_code=503,
                detail="WhatsApp API no esta configurada correctamente"
            )

        result = client.send_message(request.phone, request.message)

        if result.get("success"):
            return {
                "success": True,
                "message_id": result.get("messageId"),
                "message": "Mensaje enviado exitosamente"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido")
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar mensaje: {str(e)}"
        )


# ============================================
# WhatsApp Templates Management
# ============================================

@app.post("/whatsapp/upload-template-image")
def upload_template_image(
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Sube una imagen para usar como ejemplo en un template de WhatsApp.
    La imagen debe enviarse como base64 en el body.
    Devuelve la URL pública de la imagen.
    """
    # Este endpoint se maneja diferente - recibe JSON con la imagen base64
    pass  # Se implementará como endpoint separado


class UploadImageRequest(BaseModel):
    image_base64: str
    filename: Optional[str] = "template_image.jpg"


@app.post("/whatsapp/upload-image")
def upload_whatsapp_image(
    request: UploadImageRequest,
    current_user: models.AdminUser = Depends(require_admin)
):
    """
    Sube una imagen y devuelve su URL pública para usar en templates.
    Meta requiere URLs HTTPS públicas para ejemplos de templates con imagen.
    """
    import base64
    import uuid
    from pathlib import Path

    try:
        # Limpiar base64
        image_data = request.image_base64
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]

        # Decodificar
        image_bytes = base64.b64decode(image_data)

        # Generar nombre único
        ext = ".jpg"
        if request.filename and request.filename.lower().endswith(".png"):
            ext = ".png"
        unique_filename = f"template_{uuid.uuid4().hex[:12]}{ext}"

        # Guardar en static/whatsapp_images/
        static_path = Path("static/whatsapp_images")
        static_path.mkdir(parents=True, exist_ok=True)

        file_path = static_path / unique_filename
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        # Construir URL pública
        # Usar el dominio público configurado
        base_url = os.getenv("PUBLIC_URL", "https://ticket.ieeetadeo.org")
        public_url = f"{base_url}/static/whatsapp_images/{unique_filename}"

        print(f"[TEMPLATE IMAGE] Guardada: {file_path} -> {public_url}")

        return {
            "success": True,
            "url": public_url,
            "filename": unique_filename
        }

    except Exception as e:
        print(f"[ERROR] upload_whatsapp_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/whatsapp/templates")
def get_whatsapp_templates(
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener todos los templates de WhatsApp de Meta"""
    try:
        from whatsapp_client import WhatsAppClient
        client = WhatsAppClient()
        result = client.get_templates()

        if result.get("success"):
            return {
                "success": True,
                "templates": result.get("templates", [])
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateTemplateRequest(BaseModel):
    name: str
    display_name: str
    category: str = "UTILITY"
    language: str = "es_MX"
    body_text: Optional[str] = None
    header_type: Optional[str] = None
    header_text: Optional[str] = None
    header_image_base64: Optional[str] = None  # Imagen en base64 para header IMAGE
    footer_text: Optional[str] = None
    variable_examples: Optional[List[str]] = None


@app.post("/whatsapp/templates")
def create_whatsapp_template(
    request: CreateTemplateRequest,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Crear un nuevo template y enviarlo a Meta para aprobación"""
    try:
        from whatsapp_client import WhatsAppClient
        import requests

        client = WhatsAppClient()

        # Para templates de AUTHENTICATION, usar formato especial de Meta
        if request.category == "AUTHENTICATION":
            payload = {
                "name": request.name,
                "category": "AUTHENTICATION",
                "language": request.language,
                "components": [
                    {
                        "type": "BODY",
                        "add_security_recommendation": True
                    },
                    {
                        "type": "FOOTER",
                        "code_expiration_minutes": 60
                    },
                    {
                        "type": "BUTTONS",
                        "buttons": [
                            {
                                "type": "OTP",
                                "otp_type": "COPY_CODE",
                                "text": "Copiar código"
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                f"https://graph.facebook.com/{client.api_version}/{client.business_account_id}/message_templates",
                headers=client.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result_data = response.json()
                result = {
                    "success": True,
                    "template_id": result_data.get("id"),
                    "status": result_data.get("status", "PENDING")
                }
            else:
                error_data = response.json()
                error_info = error_data.get("error", {})
                result = {
                    "success": False,
                    "error": error_info.get("message", "Error desconocido"),
                    "error_user_msg": error_info.get("error_user_msg")
                }
        else:
            # Para UTILITY y MARKETING usar el método normal
            header_image_handle = None

            # Si es header de imagen, subir usando Resumable Upload API
            # Meta requiere un header_handle obtenido de su API de upload
            if request.header_type == "IMAGE" and request.header_image_base64:
                print(f"[TEMPLATE] Subiendo imagen para header usando Resumable Upload API...")

                # Verificar si META_APP_ID está configurado
                app_id = os.getenv("META_APP_ID") or os.getenv("FACEBOOK_APP_ID")
                if not app_id:
                    return {
                        "success": False,
                        "error": "META_APP_ID no configurado",
                        "error_user_msg": "Para crear templates con imagen, configura META_APP_ID en .env. "
                                        "Obtén el App ID desde https://developers.facebook.com/apps/"
                    }

                # Usar la función de upload del cliente
                upload_result = client.upload_media_for_template(
                    image_base64=request.header_image_base64,
                    filename=f"template_{request.name}.jpg"
                )

                if not upload_result.get("success"):
                    print(f"[TEMPLATE] Error en upload: {upload_result.get('error')}")
                    return {
                        "success": False,
                        "error": f"Error al subir imagen: {upload_result.get('error')}",
                        "error_user_msg": "No se pudo subir la imagen a Meta. Verifica tu configuración."
                    }

                header_image_handle = upload_result.get("handle")
                print(f"[TEMPLATE] Imagen subida. Handle: {header_image_handle[:50] if header_image_handle else 'None'}...")

            result = client.create_template(
                name=request.name,
                category=request.category,
                language=request.language,
                body_text=request.body_text or "",
                header_type=request.header_type,
                header_text=request.header_text,
                header_image_handle=header_image_handle,  # Handle de Resumable Upload API
                footer_text=request.footer_text,
                variable_examples=request.variable_examples
            )

        if result.get("success"):
            # Obtener el status real de la respuesta
            meta_status = result.get("status", "PENDING")

            # Guardar en BD local
            template = models.WhatsAppTemplate(
                name=request.name,
                display_name=request.display_name,
                category=request.category,
                language=request.language,
                header_type=request.header_type,
                header_text=request.header_text,
                body_text=request.body_text or "[AUTHENTICATION TEMPLATE]",
                footer_text=request.footer_text,
                variables_count=(request.body_text or "").count("{{"),
                variable_examples=json.dumps(request.variable_examples) if request.variable_examples else None,
                meta_template_id=result.get("template_id"),
                meta_status=meta_status,
                submitted_at=datetime.utcnow()
            )
            db.add(template)
            db.commit()

            return {
                "success": True,
                "template_id": result.get("template_id"),
                "status": meta_status,
                "message": f"Template {'aprobado' if meta_status == 'APPROVED' else 'rechazado' if meta_status == 'REJECTED' else 'enviado a Meta para aprobación'}"
            }
        else:
            # Log detailed error for debugging
            print(f"[TEMPLATE ERROR] Meta API Error: {result}")
            return {
                "success": False,
                "error": result.get("error", "Error desconocido"),
                "error_user_msg": result.get("error_user_msg"),
                "error_code": result.get("error_code"),
                "error_subcode": result.get("error_subcode"),
                "full_error": result.get("full_error")
            }
    except Exception as e:
        print(f"[TEMPLATE ERROR] Exception: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/whatsapp/templates/{template_name}")
def delete_whatsapp_template(
    template_name: str,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Eliminar un template de Meta y de la BD local"""
    try:
        from whatsapp_client import WhatsAppClient
        client = WhatsAppClient()

        result = client.delete_template(template_name)

        # Eliminar de BD local también
        db.query(models.WhatsAppTemplate).filter(
            models.WhatsAppTemplate.name == template_name
        ).delete()
        db.commit()

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


class SendTemplateRequest(BaseModel):
    phone: str
    template_name: str
    language: str = "es"
    variables: Optional[List[str]] = None


@app.post("/whatsapp/send-template")
def send_template_message(
    request: SendTemplateRequest,
    current_user: models.AdminUser = Depends(require_admin)
):
    """Enviar mensaje usando un template aprobado"""
    try:
        from whatsapp_client import WhatsAppClient
        client = WhatsAppClient()

        result = client.send_template_message(
            phone=request.phone,
            template_name=request.template_name,
            language=request.language,
            variables=request.variables
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WhatsApp Messages (Inbox)
# ============================================

@app.get("/whatsapp/conversations")
def get_whatsapp_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener lista de conversaciones de WhatsApp"""
    conversations = db.query(models.WhatsAppConversation).order_by(
        desc(models.WhatsAppConversation.last_message_at)
    ).offset(skip).limit(limit).all()

    total = db.query(func.count(models.WhatsAppConversation.id)).scalar()

    return {
        "conversations": [
            {
                "id": conv.id,
                "phone_number": conv.phone_number,
                "contact_name": conv.contact_name,
                "user_id": conv.user_id,
                "is_active": conv.is_active,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "unread_count": conv.unread_count
            }
            for conv in conversations
        ],
        "total": total
    }


@app.get("/whatsapp/conversations/{phone_number}/messages")
def get_conversation_messages(
    phone_number: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener mensajes de una conversación específica"""
    messages = db.query(models.WhatsAppMessage).filter(
        models.WhatsAppMessage.from_number == phone_number
    ).order_by(desc(models.WhatsAppMessage.timestamp)).offset(skip).limit(limit).all()

    # Marcar conversación como leída
    conversation = db.query(models.WhatsAppConversation).filter(
        models.WhatsAppConversation.phone_number == phone_number
    ).first()

    if conversation:
        conversation.unread_count = 0
        db.commit()

    return {
        "messages": [
            {
                "id": msg.id,
                "wa_message_id": msg.wa_message_id,
                "from_number": msg.from_number,
                "from_name": msg.from_name,
                "message_type": msg.message_type,
                "text_body": msg.text_body,
                "media_id": msg.media_id,
                "caption": msg.caption,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "is_read": msg.is_read,
                "replied": msg.replied
            }
            for msg in messages
        ]
    }


@app.post("/whatsapp/conversations/{phone_number}/reply")
def reply_to_conversation(
    phone_number: str,
    request: TestMessageRequest,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Responder a una conversación"""
    try:
        from whatsapp_client import WhatsAppClient
        client = WhatsAppClient()

        result = client.send_message(phone_number, request.message)

        if result.get("success"):
            # Actualizar conversación
            conversation = db.query(models.WhatsAppConversation).filter(
                models.WhatsAppConversation.phone_number == phone_number
            ).first()

            if conversation:
                conversation.last_message_at = datetime.utcnow()
                db.commit()

            return {
                "success": True,
                "message_id": result.get("messageId"),
                "message": "Respuesta enviada exitosamente"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/whatsapp/unread-count")
def get_unread_messages_count(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Obtener cantidad de mensajes no leídos"""
    total_unread = db.query(func.sum(models.WhatsAppConversation.unread_count)).scalar() or 0
    return {"unread_count": total_unread}


