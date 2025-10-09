from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
import models
import schemas
from database import engine, get_db
from ticket_service import ticket_service
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
    require_validator,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Tickets IEEE",
    description="Sistema de control de ingreso a eventos con QR",
    version="1.0.0"
)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")


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
    """Actualizar un validador (solo ADMIN)"""
    validator = db.query(models.AdminUser).filter(models.AdminUser.id == validator_id).first()
    if not validator:
        raise HTTPException(status_code=404, detail="Validador no encontrado")

    # Actualizar solo los campos proporcionados
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

    if validator_update.is_active is not None:
        validator.is_active = validator_update.is_active

    if validator_update.access_start is not None:
        validator.access_start = validator_update.access_start

    if validator_update.access_end is not None:
        validator.access_end = validator_update.access_end

    db.commit()
    db.refresh(validator)

    return validator


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


@app.get("/users/", response_model=List[schemas.UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los usuarios"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


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
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.identification is not None:
        user.identification = user_update.identification
    if user_update.university is not None:
        user.university = user_update.university

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
        qr_path=qr_path
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_admin)
):
    """Listar todos los tickets"""
    tickets = db.query(models.Ticket).offset(skip).limit(limit).all()
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

    # Reactivar el ticket
    ticket.is_used = False
    ticket.used_at = None
    db.commit()
    db.refresh(ticket)

    return {
        "success": True,
        "message": "Ticket reactivado exitosamente",
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
    """Actualizar un ticket (solo acompañantes por ahora)"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Actualizar solo los campos proporcionados
    if ticket_update.companions is not None:
        ticket.companions = ticket_update.companions

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


# ========== ENDPOINTS DE VALIDACIÓN ==========

@app.post("/validate/", response_model=schemas.TicketValidationResponse)
def validate_ticket(
    validation: schemas.TicketValidation,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(require_validator)
):
    """Validar un ticket en la entrada del evento"""
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

        # Verificar si ya fue usado
        if ticket.is_used:
            return schemas.TicketValidationResponse(
                valid=False,
                message=f"Ticket ya fue utilizado el {ticket.used_at.strftime('%d/%m/%Y %H:%M')}"
            )

        # Obtener usuario y evento
        user = db.query(models.User).filter(models.User.id == ticket.user_id).first()
        event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()

        # Marcar ticket como usado
        ticket.is_used = True
        ticket.used_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)

        return schemas.TicketValidationResponse(
            valid=True,
            message="Ticket válido - Acceso permitido",
            ticket=schemas.TicketResponse.model_validate(ticket),
            user=schemas.UserResponse.model_validate(user),
            event=schemas.EventResponse.model_validate(event)
        )

    except Exception as e:
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
        return validate_ticket(schemas.TicketValidation(ticket_code=ticket_code), db)

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
        return validate_ticket(schemas.TicketValidation(ticket_code=ticket_code), db)

    except Exception as e:
        return schemas.TicketValidationResponse(
            valid=False,
            message=f"QR inválido o corrupto: {str(e)}"
        )


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
    # Obtener estadísticas
    total_users = db.query(func.count(models.User.id)).scalar()
    total_events = db.query(func.count(models.Event.id)).scalar()
    total_tickets = db.query(func.count(models.Ticket.id)).scalar()
    tickets_used = db.query(func.count(models.Ticket.id)).filter(models.Ticket.is_used == True).scalar()

    # Obtener eventos activos con conteo de tickets
    active_events = db.query(
        models.Event,
        func.count(models.Ticket.id).label('ticket_count')
    ).outerjoin(models.Ticket).filter(
        models.Event.is_active == True
    ).group_by(models.Event.id).limit(5).all()

    active_events_list = []
    for event, ticket_count in active_events:
        event_dict = event.__dict__.copy()
        event_dict['ticket_count'] = ticket_count
        active_events_list.append(type('Event', (), event_dict))

    stats = {
        "total_users": total_users,
        "total_events": total_events,
        "total_tickets": total_tickets,
        "tickets_used": tickets_used
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "active_events": active_events_list
    })


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de usuarios"""
    users = db.query(
        models.User,
        func.count(models.Ticket.id).label('ticket_count')
    ).outerjoin(models.Ticket).group_by(models.User.id).all()

    users_list = []
    for user, ticket_count in users:
        user_dict = user.__dict__.copy()
        user_dict['ticket_count'] = ticket_count
        users_list.append(type('User', (), user_dict))

    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users_list
    })


@app.get("/admin/events", response_class=HTMLResponse)
async def admin_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """Página de gestión de eventos"""
    events = db.query(
        models.Event,
        func.count(models.Ticket.id).label('ticket_count')
    ).outerjoin(models.Ticket).group_by(models.Event.id).all()

    events_list = []
    for event, ticket_count in events:
        event_dict = event.__dict__.copy()
        event_dict['ticket_count'] = ticket_count
        events_list.append(type('Event', (), event_dict))

    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events_list
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


# ========== ENDPOINT PRINCIPAL ==========

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal - redirige al login"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Tickets IEEE</title>
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
            <h1>Sistema de Tickets IEEE</h1>
            <p>Redirigiendo al login...</p>
            <p><a href="/login" style="color: white;">Haz clic aquí si no eres redirigido automáticamente</a></p>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
