"""
Rutas del portal de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, extract
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import random
import string

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
from auth import create_access_token as create_admin_token

# Importar WhatsApp client si está disponible
try:
    from whatsapp_api_client import whatsapp_api
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    whatsapp_api = None

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
    current_password: Optional[str] = None  # Opcional si el usuario no tiene contraseña
    new_password: str
    confirm_password: str


class UserPasswordResetRequest(BaseModel):
    """Solicitud de recuperación de contraseña"""
    email: EmailStr


class UserPasswordReset(BaseModel):
    """Reseteo de contraseña con token"""
    token: str
    new_password: str


class OTPRequest(BaseModel):
    """Solicitud de código OTP"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    method: str  # 'email' o 'whatsapp'


class OTPVerify(BaseModel):
    """Verificación de código OTP"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    code: str


class UserUpdateProfile(BaseModel):
    """Actualización de perfil de usuario"""
    # Información básica
    name: Optional[str] = None
    nick: Optional[str] = None
    email_personal: Optional[str] = None
    email_institutional: Optional[str] = None
    email_ieee: Optional[str] = None
    primary_email_type: Optional[str] = None  # 'email_personal', 'email_institutional', 'email_ieee'
    country_code: Optional[str] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    birthday: Optional[datetime] = None

    # Información académica
    university_id: Optional[int] = None
    academic_program_id: Optional[int] = None
    semester_range_id: Optional[int] = None
    expected_graduation: Optional[datetime] = None
    english_level_id: Optional[int] = None

    # Información IEEE
    ieee_member_id: Optional[str] = None
    ieee_membership_status_id: Optional[int] = None
    ieee_roles_history: Optional[str] = None
    ieee_society_ids: Optional[List[int]] = None  # Sociedades seleccionadas

    # Perfilamiento y disponibilidad
    interest_area_id: Optional[int] = None
    availability_level_id: Optional[int] = None
    preferred_channel_id: Optional[int] = None
    goals_in_branch: Optional[str] = None
    skill_ids: Optional[List[int]] = None  # Habilidades seleccionadas


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


# ========== FUNCIONES AUXILIARES OTP ==========
def find_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Busca un usuario por cualquiera de sus emails (principal, personal, institucional, IEEE).
    Retorna el usuario si lo encuentra, None en caso contrario.
    """
    return db.query(models.User).filter(
        or_(
            models.User.email == email,
            models.User.email_personal == email,
            models.User.email_institutional == email,
            models.User.email_ieee == email
        )
    ).first()


def generate_otp_code() -> str:
    """Genera un código OTP de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))


async def send_otp_email(email: str, code: str, user_name: str) -> bool:
    """Envía el código OTP por email"""
    try:
        print(f"[OTP] Intentando enviar código OTP a {email}...")
        result = email_service.send_email(
            to_email=email,
            subject="Tu código de acceso - IEEE Tadeo",
            html_content=f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h2 style="color: #0066cc; margin-bottom: 5px;">IEEE Tadeo Control System</h2>
                        <p style="color: #666;">Portal de Usuarios</p>
                    </div>

                    <p>Hola <strong>{user_name}</strong>,</p>

                    <p>Tu código de acceso es:</p>

                    <div style="background: linear-gradient(135deg, #0066cc, #004499); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0;">
                        <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px;">{code}</span>
                    </div>

                    <p style="color: #666; font-size: 14px;">
                        Este código es válido por <strong>1 hora</strong>.
                    </p>

                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Si no solicitaste este código, puedes ignorar este mensaje.
                    </p>

                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        IEEE Tadeo Student Branch - Universidad Jorge Tadeo Lozano
                    </p>
                </body>
            </html>
            """
        )
        print(f"[OTP] Resultado de envío de email: {result}")
        return result
    except Exception as e:
        print(f"[OTP] Error enviando OTP por email: {e}")
        import traceback
        traceback.print_exc()
        return False


async def send_otp_whatsapp(phone: str, code: str, user_name: str) -> bool:
    """Envía el código OTP por WhatsApp"""
    if not WHATSAPP_AVAILABLE or not whatsapp_api:
        return False

    try:
        # Formatear el número de teléfono
        formatted_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not formatted_phone.startswith("57"):
            formatted_phone = "57" + formatted_phone

        # Enviar mensaje de texto simple con el código
        message = f"🔐 *Tu código de acceso IEEE Tadeo*\n\n*{code}*\n\nEste código es válido por 1 hora.\n\nSi no solicitaste este código, ignora este mensaje."

        result = whatsapp_api.send_text_message(formatted_phone, message)
        return result.get("success", False)
    except Exception as e:
        print(f"Error enviando OTP por WhatsApp: {e}")
        return False


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


# ========== ENDPOINTS DE AUTENTICACIÓN OTP ==========
@router.post("/auth/otp/request")
async def request_otp(
    otp_request: OTPRequest,
    db: Session = Depends(get_db)
):
    """
    Solicita un código OTP para autenticación.
    El usuario puede identificarse por email o teléfono.
    """
    user = None

    # Buscar usuario por email (cualquiera de los 3) o teléfono
    if otp_request.email:
        user = find_user_by_email(db, otp_request.email)
    elif otp_request.phone:
        # Normalizar el número de teléfono para búsqueda
        phone_clean = otp_request.phone.replace("+", "").replace(" ", "").replace("-", "")
        # Buscar con diferentes formatos
        user = db.query(models.User).filter(
            (models.User.phone == otp_request.phone) |
            (models.User.phone == phone_clean) |
            (models.User.phone.contains(phone_clean[-10:]))  # Últimos 10 dígitos
        ).first()

    if not user:
        # Por seguridad, no revelamos si el usuario existe
        return {
            "success": True,
            "message": "Si existe una cuenta con esos datos, recibirás un código de verificación"
        }

    # Verificar que el método solicitado es válido para el usuario
    if otp_request.method == "email" and not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario no tiene email registrado"
        )

    if otp_request.method == "whatsapp" and not user.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario no tiene teléfono registrado"
        )

    # Invalidar códigos OTP anteriores del usuario
    db.query(models.UserOTP).filter(
        models.UserOTP.user_id == user.id,
        models.UserOTP.used == False
    ).update({"used": True})

    # Generar nuevo código OTP
    code = generate_otp_code()

    # Crear registro OTP (válido por 1 hora)
    otp = models.UserOTP(
        user_id=user.id,
        code=code,
        method=otp_request.method,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(otp)
    db.commit()

    # Enviar el código
    sent = False
    if otp_request.method == "email":
        # Determinar a qué email enviar basado en primary_email_type
        email_to_send = user.email  # Fallback al email original
        primary_type = getattr(user, 'primary_email_type', None)

        if primary_type == 'email_personal' and user.email_personal:
            email_to_send = user.email_personal
        elif primary_type == 'email_institutional' and user.email_institutional:
            email_to_send = user.email_institutional
        elif primary_type == 'email_ieee' and user.email_ieee:
            email_to_send = user.email_ieee

        sent = await send_otp_email(email_to_send, code, user.name)
    elif otp_request.method == "whatsapp":
        if WHATSAPP_AVAILABLE:
            phone_to_send = user.phone
            if user.country_code and not user.phone.startswith("+"):
                phone_to_send = user.country_code + user.phone
            sent = await send_otp_whatsapp(phone_to_send, code, user.name)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WhatsApp no está disponible en este momento. Por favor usa email."
            )

    if not sent:
        # Si falló el envío, marcar OTP como usado
        otp.used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar el código por {otp_request.method}"
        )

    return {
        "success": True,
        "message": f"Código enviado por {otp_request.method}",
        "expires_in": 3600  # 1 hora en segundos
    }


@router.post("/auth/otp/verify")
async def verify_otp(
    otp_verify: OTPVerify,
    db: Session = Depends(get_db)
):
    """
    Verifica el código OTP y devuelve un token de acceso.
    """
    user = None

    # Buscar usuario por email (cualquiera de los 3) o teléfono
    if otp_verify.email:
        user = find_user_by_email(db, otp_verify.email)
    elif otp_verify.phone:
        phone_clean = otp_verify.phone.replace("+", "").replace(" ", "").replace("-", "")
        user = db.query(models.User).filter(
            (models.User.phone == otp_verify.phone) |
            (models.User.phone == phone_clean) |
            (models.User.phone.contains(phone_clean[-10:]))
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código inválido o expirado"
        )

    # Buscar OTP válido
    otp = db.query(models.UserOTP).filter(
        models.UserOTP.user_id == user.id,
        models.UserOTP.code == otp_verify.code,
        models.UserOTP.used == False,
        models.UserOTP.expires_at > datetime.utcnow()
    ).first()

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código inválido o expirado"
        )

    # Marcar OTP como usado
    otp.used = True

    # Registrar login
    now = datetime.utcnow()
    if not user.first_login:
        user.first_login = now
    user.last_login = now
    user.login_count = (user.login_count or 0) + 1

    db.commit()

    # Crear token de acceso (válido por 24 horas para usuarios)
    access_token = create_access_token(
        data={"sub": user.email, "type": "user"},
        expires_delta=timedelta(hours=24)
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


@router.get("/auth/otp/methods")
async def get_otp_methods(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene los métodos de OTP disponibles para un usuario.
    """
    user = None

    if email:
        user = find_user_by_email(db, email)
    elif phone:
        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        user = db.query(models.User).filter(
            (models.User.phone == phone) |
            (models.User.phone == phone_clean) |
            (models.User.phone.contains(phone_clean[-10:]))
        ).first()

    if not user:
        # Por seguridad, devolvemos ambos métodos incluso si el usuario no existe
        return {
            "methods": ["email"],
            "email_hint": None,
            "phone_hint": None
        }

    methods = []
    email_hint = None
    phone_hint = None

    if user.email:
        methods.append("email")
        # Ocultar parte del email: j***@gmail.com
        parts = user.email.split("@")
        if len(parts) == 2:
            name = parts[0]
            if len(name) > 2:
                email_hint = name[0] + "***" + name[-1] + "@" + parts[1]
            else:
                email_hint = name[0] + "***@" + parts[1]

    if user.phone and WHATSAPP_AVAILABLE:
        methods.append("whatsapp")
        # Ocultar parte del teléfono: +57 ***1234
        if len(user.phone) > 4:
            phone_hint = "***" + user.phone[-4:]

    return {
        "methods": methods,
        "email_hint": email_hint,
        "phone_hint": phone_hint
    }


# ========== ENDPOINTS DE AUTENTICACIÓN ==========
@router.post("/auth/login")
async def user_login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Login de usuario con email y contraseña"""
    # Buscar usuario por email (cualquiera de los 3)
    user = find_user_by_email(db, login_data.email)

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

    # Registrar login
    now = datetime.utcnow()
    if not user.first_login:
        user.first_login = now
    user.last_login = now
    user.login_count = (user.login_count or 0) + 1
    db.commit()

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
    user = find_user_by_email(db, request_data.email)

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
    """Cambia o crea la contraseña del usuario autenticado"""
    # Validar que las contraseñas coincidan
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas no coinciden"
        )

    # Validar longitud mínima
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres"
        )

    # Guardar si ya tenía contraseña antes de actualizar
    had_password = bool(current_user.hashed_password)

    # Actualizar/crear contraseña (sin validar contraseña actual por ahora)
    new_hashed_password = hash_password(password_data.new_password)
    current_user.hashed_password = new_hashed_password

    # Sincronizar contraseña con AdminUser vinculado si existe
    admin_user = db.query(models.AdminUser).filter(
        models.AdminUser.is_active == True,
        (models.AdminUser.linked_user_id == current_user.id) |
        (models.AdminUser.email == current_user.email)
    ).first()
    if admin_user:
        admin_user.hashed_password = new_hashed_password

    db.commit()

    # Mensaje diferente si es creación o cambio
    if had_password:
        return {"message": "Contraseña actualizada exitosamente"}
    else:
        return {"message": "Contraseña creada exitosamente"}


# ========== ENDPOINTS DE CATÁLOGOS ==========
@router.get("/catalogs/academic-programs")
async def get_academic_programs(db: Session = Depends(get_db)):
    """Obtiene los programas académicos disponibles"""
    programs = db.query(models.AcademicProgram).filter(
        models.AcademicProgram.is_active == True
    ).order_by(models.AcademicProgram.display_order, models.AcademicProgram.name).all()
    return [{"id": p.id, "name": p.name, "short_name": p.short_name, "category": p.category} for p in programs]


@router.get("/catalogs/semester-ranges")
async def get_semester_ranges(db: Session = Depends(get_db)):
    """Obtiene los rangos de semestre disponibles"""
    ranges = db.query(models.SemesterRange).filter(
        models.SemesterRange.is_active == True
    ).order_by(models.SemesterRange.display_order).all()
    return [{"id": r.id, "name": r.name} for r in ranges]


@router.get("/catalogs/english-levels")
async def get_english_levels(db: Session = Depends(get_db)):
    """Obtiene los niveles de inglés disponibles"""
    levels = db.query(models.EnglishLevel).filter(
        models.EnglishLevel.is_active == True
    ).order_by(models.EnglishLevel.display_order).all()
    return [{"id": l.id, "code": l.code, "name": l.name} for l in levels]


@router.get("/catalogs/ieee-membership-statuses")
async def get_ieee_membership_statuses(db: Session = Depends(get_db)):
    """Obtiene los estados de membresía IEEE disponibles"""
    statuses = db.query(models.IEEEMembershipStatus).filter(
        models.IEEEMembershipStatus.is_active == True
    ).order_by(models.IEEEMembershipStatus.display_order).all()
    return [{"id": s.id, "name": s.name, "description": s.description} for s in statuses]


@router.get("/catalogs/ieee-societies")
async def get_ieee_societies(db: Session = Depends(get_db)):
    """Obtiene las sociedades IEEE disponibles"""
    societies = db.query(models.IEEESociety).filter(
        models.IEEESociety.is_active == True
    ).order_by(models.IEEESociety.display_order).all()
    return [{"id": s.id, "code": s.code, "name": s.name, "full_name": s.full_name, "society_type": s.society_type, "color": s.color} for s in societies]


@router.get("/catalogs/interest-areas")
async def get_interest_areas(db: Session = Depends(get_db)):
    """Obtiene las áreas de interés disponibles"""
    areas = db.query(models.InterestArea).filter(
        models.InterestArea.is_active == True
    ).order_by(models.InterestArea.display_order).all()
    return [{"id": a.id, "name": a.name, "description": a.description, "icon": a.icon} for a in areas]


@router.get("/catalogs/availability-levels")
async def get_availability_levels(db: Session = Depends(get_db)):
    """Obtiene los niveles de disponibilidad disponibles"""
    levels = db.query(models.AvailabilityLevel).filter(
        models.AvailabilityLevel.is_active == True
    ).order_by(models.AvailabilityLevel.display_order).all()
    return [{"id": l.id, "name": l.name, "hours_description": l.hours_description} for l in levels]


@router.get("/catalogs/communication-channels")
async def get_communication_channels(db: Session = Depends(get_db)):
    """Obtiene los canales de comunicación disponibles"""
    channels = db.query(models.CommunicationChannel).filter(
        models.CommunicationChannel.is_active == True
    ).order_by(models.CommunicationChannel.display_order).all()
    return [{"id": c.id, "name": c.name, "description": c.description, "icon": c.icon} for c in channels]


@router.get("/catalogs/skills")
async def get_skills(db: Session = Depends(get_db)):
    """Obtiene las habilidades disponibles"""
    skills = db.query(models.Skill).filter(
        models.Skill.is_active == True
    ).order_by(models.Skill.category, models.Skill.display_order).all()
    return [{"id": s.id, "name": s.name, "category": s.category, "icon": s.icon, "color": s.color} for s in skills]


# ========== ENDPOINTS DE PERFIL ==========
@router.get("/profile")
async def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el perfil completo del usuario autenticado"""
    # Cargar todas las relaciones
    user = db.query(models.User).options(
        joinedload(models.User.university),
        joinedload(models.User.academic_program),
        joinedload(models.User.semester_range),
        joinedload(models.User.english_level),
        joinedload(models.User.ieee_membership_status),
        joinedload(models.User.ieee_societies),
        joinedload(models.User.interest_area),
        joinedload(models.User.availability_level),
        joinedload(models.User.preferred_channel),
        joinedload(models.User.skills)
    ).filter(models.User.id == current_user.id).first()

    return {
        "id": user.id,
        # Información básica
        "name": user.name,
        "nick": user.nick,
        "photo_path": user.photo_path,
        "email": user.email,
        "email_personal": user.email_personal,
        "email_institutional": user.email_institutional,
        "email_ieee": user.email_ieee,
        "primary_email_type": user.primary_email_type or 'email_personal',
        "country_code": user.country_code,
        "phone": user.phone,
        "identification": user.identification,
        "birthday": user.birthday,

        # Información académica
        "university_id": user.university_id,
        "university": {"id": user.university.id, "name": user.university.name, "short_name": user.university.short_name} if user.university else None,
        "academic_program_id": user.academic_program_id,
        "academic_program": {"id": user.academic_program.id, "name": user.academic_program.name} if user.academic_program else None,
        "semester_range_id": user.semester_range_id,
        "semester_range": {"id": user.semester_range.id, "name": user.semester_range.name} if user.semester_range else None,
        "expected_graduation": user.expected_graduation,
        "english_level_id": user.english_level_id,
        "english_level": {"id": user.english_level.id, "code": user.english_level.code, "name": user.english_level.name} if user.english_level else None,

        # Información IEEE
        "is_ieee_member": user.is_ieee_member,
        "ieee_member_id": user.ieee_member_id,
        "ieee_membership_status_id": user.ieee_membership_status_id,
        "ieee_membership_status": {"id": user.ieee_membership_status.id, "name": user.ieee_membership_status.name} if user.ieee_membership_status else None,
        "ieee_roles_history": user.ieee_roles_history,
        "ieee_societies": [{"id": s.id, "code": s.code, "name": s.name, "color": s.color} for s in user.ieee_societies],

        # Perfilamiento y disponibilidad
        "interest_area_id": user.interest_area_id,
        "interest_area": {"id": user.interest_area.id, "name": user.interest_area.name} if user.interest_area else None,
        "availability_level_id": user.availability_level_id,
        "availability_level": {"id": user.availability_level.id, "name": user.availability_level.name} if user.availability_level else None,
        "preferred_channel_id": user.preferred_channel_id,
        "preferred_channel": {"id": user.preferred_channel.id, "name": user.preferred_channel.name} if user.preferred_channel else None,
        "goals_in_branch": user.goals_in_branch,
        "skills": [{"id": s.id, "name": s.name, "category": s.category, "color": s.color} for s in user.skills],

        # Metadatos
        "has_password": bool(user.hashed_password),  # Indica si el usuario tiene contraseña
        "profile_completed": user.profile_completed,
        "created_at": user.created_at,

        # Acceso administrativo (verifica si tiene cuenta de admin vinculada)
        "has_admin_access": db.query(models.AdminUser).filter(
            models.AdminUser.is_active == True,
            (models.AdminUser.linked_user_id == user.id) | (models.AdminUser.email == user.email)
        ).first() is not None
    }


@router.put("/profile")
async def update_profile(
    profile_data: UserUpdateProfile,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el perfil completo del usuario autenticado"""

    # ========== INFORMACIÓN BÁSICA ==========
    if profile_data.name is not None:
        current_user.name = profile_data.name

    if profile_data.nick is not None:
        current_user.nick = profile_data.nick if profile_data.nick else None

    # ========== EMAILS ==========
    if profile_data.email_personal is not None:
        current_user.email_personal = profile_data.email_personal if profile_data.email_personal else None

    if profile_data.email_institutional is not None:
        current_user.email_institutional = profile_data.email_institutional if profile_data.email_institutional else None

    if profile_data.email_ieee is not None:
        current_user.email_ieee = profile_data.email_ieee if profile_data.email_ieee else None

    if profile_data.primary_email_type is not None:
        # Validar que el tipo sea válido
        valid_types = ['email_personal', 'email_institutional', 'email_ieee']
        if profile_data.primary_email_type in valid_types:
            current_user.primary_email_type = profile_data.primary_email_type

            # Actualizar el email principal (campo email) basado en el tipo seleccionado
            if profile_data.primary_email_type == 'email_personal' and current_user.email_personal:
                current_user.email = current_user.email_personal
            elif profile_data.primary_email_type == 'email_institutional' and current_user.email_institutional:
                current_user.email = current_user.email_institutional
            elif profile_data.primary_email_type == 'email_ieee' and current_user.email_ieee:
                current_user.email = current_user.email_ieee

    if profile_data.country_code is not None:
        current_user.country_code = profile_data.country_code

    if profile_data.phone is not None:
        current_user.phone = profile_data.phone if profile_data.phone else None

    if profile_data.identification is not None:
        current_user.identification = profile_data.identification if profile_data.identification else None

    if profile_data.birthday is not None:
        current_user.birthday = profile_data.birthday

    # ========== INFORMACIÓN ACADÉMICA ==========
    if profile_data.university_id is not None:
        if profile_data.university_id == 0:
            current_user.university_id = None
        else:
            university = db.query(models.University).filter(models.University.id == profile_data.university_id).first()
            if not university:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Universidad no encontrada")
            current_user.university_id = profile_data.university_id

    if profile_data.academic_program_id is not None:
        if profile_data.academic_program_id == 0:
            current_user.academic_program_id = None
        else:
            program = db.query(models.AcademicProgram).filter(models.AcademicProgram.id == profile_data.academic_program_id).first()
            if not program:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa académico no encontrado")
            current_user.academic_program_id = profile_data.academic_program_id

    if profile_data.semester_range_id is not None:
        if profile_data.semester_range_id == 0:
            current_user.semester_range_id = None
        else:
            semester = db.query(models.SemesterRange).filter(models.SemesterRange.id == profile_data.semester_range_id).first()
            if not semester:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rango de semestre no encontrado")
            current_user.semester_range_id = profile_data.semester_range_id

            # Auto-sincronizar estado de estudio principal con semestre
            # Si es "Egresado / Graduado" (min_semester y max_semester son None)
            primary_study = db.query(models.UserStudy).filter(
                models.UserStudy.user_id == current_user.id,
                models.UserStudy.is_primary == True
            ).first()

            if primary_study:
                if semester.min_semester is None and semester.max_semester is None:
                    # Es egresado o posgrado
                    if "egresado" in semester.name.lower() or "graduado" in semester.name.lower():
                        primary_study.status = models.StudyStatus.egresado
                else:
                    # Está cursando
                    primary_study.status = models.StudyStatus.cursando

    if profile_data.expected_graduation is not None:
        current_user.expected_graduation = profile_data.expected_graduation

    if profile_data.english_level_id is not None:
        if profile_data.english_level_id == 0:
            current_user.english_level_id = None
        else:
            level = db.query(models.EnglishLevel).filter(models.EnglishLevel.id == profile_data.english_level_id).first()
            if not level:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nivel de inglés no encontrado")
            current_user.english_level_id = profile_data.english_level_id

    # ========== INFORMACIÓN IEEE ==========
    if profile_data.ieee_member_id is not None:
        current_user.ieee_member_id = profile_data.ieee_member_id.strip() if profile_data.ieee_member_id else None
        current_user.is_ieee_member = bool(current_user.ieee_member_id)

    if profile_data.ieee_membership_status_id is not None:
        if profile_data.ieee_membership_status_id == 0:
            current_user.ieee_membership_status_id = None
        else:
            status_obj = db.query(models.IEEEMembershipStatus).filter(models.IEEEMembershipStatus.id == profile_data.ieee_membership_status_id).first()
            if not status_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estado de membresía no encontrado")
            current_user.ieee_membership_status_id = profile_data.ieee_membership_status_id

    if profile_data.ieee_roles_history is not None:
        current_user.ieee_roles_history = profile_data.ieee_roles_history if profile_data.ieee_roles_history else None

    if profile_data.ieee_society_ids is not None:
        # Actualizar sociedades IEEE (relación many-to-many)
        societies = db.query(models.IEEESociety).filter(models.IEEESociety.id.in_(profile_data.ieee_society_ids)).all()
        current_user.ieee_societies = societies

    # ========== PERFILAMIENTO Y DISPONIBILIDAD ==========
    if profile_data.interest_area_id is not None:
        if profile_data.interest_area_id == 0:
            current_user.interest_area_id = None
        else:
            area = db.query(models.InterestArea).filter(models.InterestArea.id == profile_data.interest_area_id).first()
            if not area:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área de interés no encontrada")
            current_user.interest_area_id = profile_data.interest_area_id

    if profile_data.availability_level_id is not None:
        if profile_data.availability_level_id == 0:
            current_user.availability_level_id = None
        else:
            availability = db.query(models.AvailabilityLevel).filter(models.AvailabilityLevel.id == profile_data.availability_level_id).first()
            if not availability:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nivel de disponibilidad no encontrado")
            current_user.availability_level_id = profile_data.availability_level_id

    if profile_data.preferred_channel_id is not None:
        if profile_data.preferred_channel_id == 0:
            current_user.preferred_channel_id = None
        else:
            channel = db.query(models.CommunicationChannel).filter(models.CommunicationChannel.id == profile_data.preferred_channel_id).first()
            if not channel:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canal de comunicación no encontrado")
            current_user.preferred_channel_id = profile_data.preferred_channel_id

    if profile_data.goals_in_branch is not None:
        current_user.goals_in_branch = profile_data.goals_in_branch if profile_data.goals_in_branch else None

    if profile_data.skill_ids is not None:
        # Actualizar habilidades (relación many-to-many)
        skills = db.query(models.Skill).filter(models.Skill.id.in_(profile_data.skill_ids)).all()
        current_user.skills = skills

    # ========== METADATOS ==========
    current_user.last_profile_update = datetime.utcnow()

    # Verificar si el perfil está completo (campos mínimos requeridos)
    required_fields = [
        current_user.name,
        current_user.university_id,
        current_user.academic_program_id,
        current_user.semester_range_id,
        current_user.ieee_membership_status_id
    ]
    if all(required_fields) and not current_user.profile_completed:
        current_user.profile_completed = True
        current_user.profile_completed_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    return {"message": "Perfil actualizado exitosamente", "profile_completed": current_user.profile_completed}


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


# ========== ENDPOINT DE FOTO DE PERFIL ==========
@router.post("/profile/photo")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube y optimiza la foto de perfil del usuario.
    Redimensiona a máximo 400x400 px y comprime en JPEG.
    """
    import os
    from PIL import Image
    import io
    import uuid

    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Use JPG, PNG, WebP o GIF."
        )

    # Leer el archivo
    try:
        content = await photo.read()
        if len(content) > 10 * 1024 * 1024:  # 10 MB máximo
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La imagen es demasiado grande. Máximo 10 MB."
            )

        # Abrir con PIL
        image = Image.open(io.BytesIO(content))

        # Convertir a RGB si es necesario (para PNG con transparencia)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background

        # Redimensionar manteniendo proporción (máximo 400x400)
        max_size = (400, 400)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Crear directorio si no existe
        upload_dir = "static/profile_photos"
        os.makedirs(upload_dir, exist_ok=True)

        # Eliminar foto anterior si existe
        if current_user.photo_path:
            old_path = current_user.photo_path
            if old_path.startswith('/'):
                old_path = old_path[1:]
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        # Generar nombre único
        filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(upload_dir, filename)

        # Guardar optimizado como JPEG
        image.save(filepath, "JPEG", quality=85, optimize=True)

        # Actualizar ruta en la base de datos
        current_user.photo_path = f"/{filepath}"
        db.commit()

        return {
            "success": True,
            "message": "Foto de perfil actualizada",
            "photo_path": current_user.photo_path
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la imagen: {str(e)}"
        )


@router.delete("/profile/photo")
async def delete_profile_photo(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina la foto de perfil del usuario"""
    import os

    if not current_user.photo_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay foto de perfil para eliminar"
        )

    # Eliminar archivo
    old_path = current_user.photo_path
    if old_path.startswith('/'):
        old_path = old_path[1:]
    if os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception:
            pass

    # Actualizar base de datos
    current_user.photo_path = None
    db.commit()

    return {"success": True, "message": "Foto de perfil eliminada"}


# ========== ENDPOINTS DE ESTUDIOS DEL USUARIO ==========

@router.get("/profile/studies")
async def get_user_studies(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de estudios del usuario"""
    studies = db.query(models.UserStudy).filter(
        models.UserStudy.user_id == current_user.id
    ).order_by(models.UserStudy.is_primary.desc(), models.UserStudy.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "study_type": s.study_type.value if hasattr(s.study_type, 'value') else s.study_type,
            "program_name": s.program_name,
            "institution": s.institution,
            "status": s.status.value if hasattr(s.status, 'value') else (s.status or "cursando"),
            "is_primary": s.is_primary,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in studies
    ]


@router.post("/profile/studies")
async def add_user_study(
    study_data: schemas.UserStudyCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agrega un nuevo estudio al usuario"""
    # Validar tipo de estudio
    valid_types = ['tecnica', 'tecnologia', 'pregrado', 'posgrado', 'otro']
    if study_data.study_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de estudio inválido. Debe ser uno de: {', '.join(valid_types)}"
        )

    # Validar estado
    valid_statuses = ['cursando', 'sin_terminar', 'egresado']
    if study_data.status and study_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
        )

    # Si es primario, quitar el flag de primario de los demás
    if study_data.is_primary:
        db.query(models.UserStudy).filter(
            models.UserStudy.user_id == current_user.id
        ).update({"is_primary": False})

    # Crear el nuevo estudio
    new_study = models.UserStudy(
        user_id=current_user.id,
        study_type=models.StudyType(study_data.study_type),
        program_name=study_data.program_name,
        institution=study_data.institution,
        status=models.StudyStatus(study_data.status) if study_data.status else models.StudyStatus.cursando,
        is_primary=study_data.is_primary
    )
    db.add(new_study)
    db.commit()
    db.refresh(new_study)

    return {
        "success": True,
        "message": "Estudio agregado exitosamente",
        "study": {
            "id": new_study.id,
            "study_type": new_study.study_type.value,
            "program_name": new_study.program_name,
            "institution": new_study.institution,
            "status": new_study.status.value if new_study.status else "cursando",
            "is_primary": new_study.is_primary
        }
    }


@router.put("/profile/studies/{study_id}")
async def update_user_study(
    study_id: int,
    study_data: schemas.UserStudyUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza un estudio del usuario"""
    study = db.query(models.UserStudy).filter(
        models.UserStudy.id == study_id,
        models.UserStudy.user_id == current_user.id
    ).first()

    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudio no encontrado"
        )

    # Validar tipo de estudio si se proporciona
    if study_data.study_type:
        valid_types = ['tecnica', 'tecnologia', 'pregrado', 'posgrado', 'otro']
        if study_data.study_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de estudio inválido. Debe ser uno de: {', '.join(valid_types)}"
            )
        study.study_type = models.StudyType(study_data.study_type)

    if study_data.program_name is not None:
        study.program_name = study_data.program_name

    if study_data.institution is not None:
        study.institution = study_data.institution

    # Validar y actualizar estado
    if study_data.status is not None:
        valid_statuses = ['cursando', 'sin_terminar', 'egresado']
        if study_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
            )
        study.status = models.StudyStatus(study_data.status)

    if study_data.is_primary is not None:
        if study_data.is_primary:
            # Quitar el flag de primario de los demás
            db.query(models.UserStudy).filter(
                models.UserStudy.user_id == current_user.id,
                models.UserStudy.id != study_id
            ).update({"is_primary": False})
        study.is_primary = study_data.is_primary

    db.commit()
    db.refresh(study)

    return {
        "success": True,
        "message": "Estudio actualizado exitosamente",
        "study": {
            "id": study.id,
            "study_type": study.study_type.value,
            "program_name": study.program_name,
            "institution": study.institution,
            "status": study.status.value if study.status else "cursando",
            "is_primary": study.is_primary
        }
    }


@router.delete("/profile/studies/{study_id}")
async def delete_user_study(
    study_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina un estudio del usuario"""
    study = db.query(models.UserStudy).filter(
        models.UserStudy.id == study_id,
        models.UserStudy.user_id == current_user.id
    ).first()

    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudio no encontrado"
        )

    db.delete(study)
    db.commit()

    return {"success": True, "message": "Estudio eliminado exitosamente"}


# ========== ENDPOINT DE CROSS-LOGIN (PORTAL <-> ADMIN) ==========
@router.get("/auth/admin-token")
async def get_admin_token(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un token de admin para el usuario del portal si tiene acceso administrativo.
    Permite transición transparente del portal al panel de admin.
    """
    # Buscar cuenta de admin vinculada
    admin_user = db.query(models.AdminUser).filter(
        models.AdminUser.is_active == True,
        (models.AdminUser.linked_user_id == current_user.id) |
        (models.AdminUser.email == current_user.email)
    ).first()

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso administrativo"
        )

    # Verificar acceso temporal si aplica
    now = datetime.utcnow()
    if admin_user.access_start and admin_user.access_start > now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu acceso aún no está activo"
        )
    if admin_user.access_end and admin_user.access_end < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu acceso ha expirado"
        )

    # Obtener permisos del usuario admin
    # Los permisos se guardan como JSON string en la BD, hay que parsearlos
    permissions = {}
    if admin_user.permissions:
        import json
        try:
            permissions = json.loads(admin_user.permissions) if isinstance(admin_user.permissions, str) else admin_user.permissions
        except (json.JSONDecodeError, TypeError):
            permissions = {}

    # Generar token de admin con permisos
    admin_token = create_admin_token(
        data={"sub": admin_user.username, "role": admin_user.role.value if admin_user.role else "admin", "permissions": permissions},
        expires_delta=timedelta(hours=8)
    )

    return {
        "access_token": admin_token,
        "token_type": "bearer",
        "username": admin_user.username,
        "full_name": admin_user.full_name,
        "role": admin_user.role.value if admin_user.role else "ADMIN",
        "permissions": permissions
    }


# ============================================================
# GENERACIÓN DE TOKEN PARA MÓDULOS EXTERNOS
# ============================================================

@router.post("/generate-external-token", response_model=schemas.ExternalTokenResponse)
def generate_external_token(
    body: schemas.ExternalTokenRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un token temporal para que el usuario acceda a un módulo externo.
    El usuario debe estar autenticado en el portal.
    """
    module = db.query(models.ExternalModule).filter(
        models.ExternalModule.name == body.module_name,
        models.ExternalModule.is_active == True
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(minutes=30)

    db.add(models.ExternalUserToken(
        token=token,
        user_id=current_user.id,
        module_id=module.id,
        expires_at=expires
    ))
    db.commit()

    redirect_url = f"{module.callback_url}?token={token}" if module.callback_url else None

    return schemas.ExternalTokenResponse(
        token=token,
        expires_at=expires,
        redirect_url=redirect_url
    )


@router.get("/birthdays")
async def get_member_birthdays(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna los cumpleaños de todos los miembros con fecha registrada"""
    users = db.query(models.User).options(
        joinedload(models.User.academic_program)
    ).filter(
        models.User.birthday.isnot(None)
    ).all()

    birthdays = []
    for user in users:
        bday = user.birthday
        birthdays.append({
            "name": user.name,
            "photo_path": user.photo_path,
            "month": bday.month,
            "day": bday.day,
            "academic_program": user.academic_program.name if user.academic_program else None,
        })

    birthdays.sort(key=lambda x: (x["month"], x["day"]))
    return birthdays


@router.get("/events")
async def get_portal_events(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna eventos para el calendario del portal"""
    events = db.query(models.Event).filter(
        models.Event.is_active == True
    ).order_by(models.Event.event_date.asc()).all()

    return [
        {
            "id": e.id,
            "name": e.name,
            "location": e.location,
            "event_date": e.event_date.isoformat() if e.event_date else None,
            "event_end_date": e.event_end_date.isoformat() if e.event_end_date else None,
            "event_type": e.event_type,
        }
        for e in events
    ]
