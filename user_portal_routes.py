"""
Rutas del portal de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

import models
import schemas
from database import get_db
from user_auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from email_service import email_service

# Router
router = APIRouter(prefix="/portal", tags=["Portal de Usuarios"])

# Templates
templates = Jinja2Templates(directory="templates")


# ========== SCHEMAS ==========
class UserLoginRequest(BaseModel):
    """Solicitud de login de usuario"""
    email: EmailStr
    password: str


class UserPasswordChange(BaseModel):
    """Cambio de contraseña"""
    current_password: str
    new_password: str


class UserPasswordResetRequest(BaseModel):
    """Solicitud de recuperación de contraseña"""
    email: EmailStr


class UserPasswordReset(BaseModel):
    """Reseteo de contraseña con token"""
    token: str
    new_password: str


class UserUpdateProfile(BaseModel):
    """Actualización de perfil de usuario"""
    name: Optional[str] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    birthday: Optional[datetime] = None
    university_id: Optional[int] = None


class UserTicketResponse(BaseModel):
    """Respuesta de ticket para usuario"""
    id: int
    ticket_code: str
    event_name: str
    event_date: datetime
    event_location: str
    companions: int
    is_used: bool
    used_at: Optional[datetime]
    qr_path: Optional[str]

    class Config:
        from_attributes = True


# ========== PÁGINAS HTML ==========
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login del portal de usuarios"""
    return templates.TemplateResponse("portal_login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página principal del portal de usuarios (requiere autenticación en el frontend)"""
    return templates.TemplateResponse("portal_dashboard.html", {"request": request})


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """Página para restablecer contraseña con token"""
    return templates.TemplateResponse("portal_reset_password.html", {"request": request})


@router.get("/ticket/{unique_url}", response_class=HTMLResponse)
async def public_ticket_page(request: Request, unique_url: str):
    """Página pública para ver un ticket (no requiere autenticación)"""
    return templates.TemplateResponse("public_ticket.html", {
        "request": request,
        "unique_url": unique_url
    })


# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@router.post("/auth/login")
async def user_login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Login de usuario con email y contraseña"""
    # Buscar usuario por email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    # Verificar contraseña
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    # Crear token de acceso
    access_token = create_access_token(
        data={"sub": user.email, "type": "user"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/auth/request-password-reset")
async def request_password_reset(
    request_data: UserPasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Solicita un enlace de recuperación de contraseña"""
    user = db.query(models.User).filter(models.User.email == request_data.email).first()

    if not user:
        # Por seguridad, no revelamos si el email existe o no
        return {"message": "Si el email existe, recibirás un enlace de recuperación"}

    # Generar token de recuperación
    reset_token = create_reset_token()
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)

    db.commit()

    # Enviar email con el token
    reset_link = f"https://ticket.ieeetadeo.org/portal/reset-password?token={reset_token}"

    try:
        email_service.send_email(
            to_email=user.email,
            subject="Recuperación de contraseña - Sistema de Tickets IEEE",
            html_content=f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0066cc;">Recuperación de Contraseña</h2>
                    <p>Hola {user.name},</p>
                    <p>Has solicitado recuperar tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                    <p style="margin: 30px 0;">
                        <a href="{reset_link}"
                           style="background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                            Recuperar Contraseña
                        </a>
                    </p>
                    <p style="color: #666; font-size: 14px;">Este enlace expirará en 1 hora.</p>
                    <p style="color: #666; font-size: 14px;">Si no solicitaste este cambio, puedes ignorar este email.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px;">Sistema de Tickets - IEEE Tadeo</p>
                </body>
            </html>
            """
        )
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        # No lanzamos error al usuario por seguridad

    return {"message": "Si el email existe, recibirás un enlace de recuperación"}


@router.post("/auth/reset-password")
async def reset_password(
    reset_data: UserPasswordReset,
    db: Session = Depends(get_db)
):
    """Resetea la contraseña usando el token"""
    user = db.query(models.User).filter(
        models.User.password_reset_token == reset_data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido o expirado"
        )

    # Verificar que el token no haya expirado
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación expirado"
        )

    # Actualizar contraseña
    user.hashed_password = hash_password(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None

    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}


@router.post("/auth/change-password")
async def change_password(
    password_data: UserPasswordChange,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario autenticado"""
    # Verificar contraseña actual
    if not current_user.hashed_password or not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    # Actualizar contraseña
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}


# ========== ENDPOINTS DE PERFIL ==========
@router.get("/profile")
async def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el perfil del usuario autenticado"""
    # Cargar la universidad si existe
    user = db.query(models.User).options(
        joinedload(models.User.university)
    ).filter(models.User.id == current_user.id).first()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "identification": user.identification,
        "birthday": user.birthday,
        "university_id": user.university_id,
        "university": {
            "id": user.university.id,
            "name": user.university.name,
            "short_name": user.university.short_name
        } if user.university else None,
        "is_ieee_member": user.is_ieee_member,
        "created_at": user.created_at
    }


@router.put("/profile")
async def update_profile(
    profile_data: UserUpdateProfile,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el perfil del usuario autenticado"""
    if profile_data.name is not None:
        current_user.name = profile_data.name

    if profile_data.phone is not None:
        current_user.phone = profile_data.phone

    if profile_data.identification is not None:
        current_user.identification = profile_data.identification

    if profile_data.birthday is not None:
        current_user.birthday = profile_data.birthday

    if profile_data.university_id is not None:
        # Verificar que la universidad existe
        university = db.query(models.University).filter(
            models.University.id == profile_data.university_id
        ).first()
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidad no encontrada"
            )
        current_user.university_id = profile_data.university_id

    db.commit()
    db.refresh(current_user)

    return {"message": "Perfil actualizado exitosamente"}


# ========== ENDPOINTS DE TICKETS ==========
@router.get("/tickets")
async def get_user_tickets(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los tickets del usuario autenticado"""
    tickets = db.query(models.Ticket).options(
        joinedload(models.Ticket.event)
    ).filter(models.Ticket.user_id == current_user.id).order_by(
        models.Ticket.created_at.desc()
    ).all()

    return [
        {
            "id": ticket.id,
            "ticket_code": ticket.ticket_code,
            "unique_url": ticket.unique_url,
            "event_name": ticket.event.name,
            "event_date": ticket.event.event_date,
            "event_location": ticket.event.location,
            "event_description": ticket.event.description,
            "companions": ticket.companions,
            "is_used": ticket.is_used,
            "used_at": ticket.used_at,
            "qr_path": ticket.qr_path,
            "created_at": ticket.created_at
        }
        for ticket in tickets
    ]


@router.get("/tickets/{ticket_id}")
async def get_user_ticket(
    ticket_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene un ticket específico del usuario"""
    ticket = db.query(models.Ticket).options(
        joinedload(models.Ticket.event)
    ).filter(
        models.Ticket.id == ticket_id,
        models.Ticket.user_id == current_user.id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )

    return {
        "id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "event_name": ticket.event.name,
        "event_date": ticket.event.event_date,
        "event_location": ticket.event.location,
        "event_description": ticket.event.description,
        "companions": ticket.companions,
        "is_used": ticket.is_used,
        "used_at": ticket.used_at,
        "qr_path": ticket.qr_path,
        "created_at": ticket.created_at
    }


# ========== ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN) ==========
@router.get("/api/public/ticket/{unique_url}")
async def get_public_ticket(
    unique_url: str,
    db: Session = Depends(get_db)
):
    """Obtiene información del ticket usando la URL única (sin autenticación)"""
    ticket = db.query(models.Ticket).options(
        joinedload(models.Ticket.event),
        joinedload(models.Ticket.user)
    ).filter(
        models.Ticket.unique_url == unique_url
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )

    return {
        "id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "user_name": ticket.user.name,
        "event": {
            "name": ticket.event.name,
            "date": ticket.event.event_date,
            "location": ticket.event.location,
            "description": ticket.event.description
        },
        "companions": ticket.companions,
        "is_used": ticket.is_used,
        "used_at": ticket.used_at,
        "qr_path": ticket.qr_path,
        "created_at": ticket.created_at
    }
