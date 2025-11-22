from __future__ import annotations
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List


# Schemas de Tag/Etiqueta
class TagCreate(BaseModel):
    """Schema para crear tag"""
    name: str
    color: str = "#3B82F6"
    description: Optional[str] = None


class TagUpdate(BaseModel):
    """Schema para actualizar tag"""
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TagResponse(BaseModel):
    """Schema para respuesta de tag"""
    id: int
    name: str
    color: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Universidad
class UniversityCreate(BaseModel):
    """Schema para crear universidad"""
    name: str
    short_name: Optional[str] = None
    has_ieee_branch: bool = False
    ieee_contact_email: Optional[str] = None
    ieee_facebook: Optional[str] = None
    ieee_instagram: Optional[str] = None
    ieee_twitter: Optional[str] = None
    ieee_tiktok: Optional[str] = None
    ieee_website: Optional[str] = None


class UniversityUpdate(BaseModel):
    """Schema para actualizar universidad"""
    name: Optional[str] = None
    short_name: Optional[str] = None
    is_active: Optional[bool] = None
    has_ieee_branch: Optional[bool] = None
    ieee_contact_email: Optional[str] = None
    ieee_facebook: Optional[str] = None
    ieee_instagram: Optional[str] = None
    ieee_twitter: Optional[str] = None
    ieee_tiktok: Optional[str] = None
    ieee_website: Optional[str] = None


class UniversityResponse(BaseModel):
    """Schema para respuesta de universidad"""
    id: int
    name: str
    short_name: Optional[str]
    is_active: bool
    has_ieee_branch: bool
    ieee_contact_email: Optional[str]
    ieee_facebook: Optional[str]
    ieee_instagram: Optional[str]
    ieee_twitter: Optional[str]
    ieee_tiktok: Optional[str]
    ieee_website: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Organización
class OrganizationCreate(BaseModel):
    """Schema para crear organización"""
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    email_template: Optional[str] = None
    whatsapp_template: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Schema para actualizar organización"""
    name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    email_template: Optional[str] = None
    whatsapp_template: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """Schema para respuesta de organización"""
    id: int
    name: str
    short_name: Optional[str]
    description: Optional[str]
    logo_path: Optional[str]
    email_template: Optional[str]
    whatsapp_template: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    website: Optional[str]
    facebook: Optional[str]
    instagram: Optional[str]
    twitter: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Usuario
class UserCreate(BaseModel):
    """Schema para crear usuario"""
    name: str
    nick: Optional[str] = None  # Apodo o forma corta de llamar al usuario
    email: EmailStr
    country_code: Optional[str] = "+57"
    phone: Optional[str] = None
    identification: Optional[str] = None  # Cédula
    university_id: Optional[int] = None  # ID de universidad
    organization_id: Optional[int] = None  # ID de organización externa
    birthday: Optional[datetime] = None  # Fecha de cumpleaños
    is_ieee_member: bool = False  # Miembro activo de IEEE
    ieee_member_id: Optional[str] = None  # ID de membresía IEEE


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    name: Optional[str] = None
    nick: Optional[str] = None
    email: Optional[EmailStr] = None
    country_code: Optional[str] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    university_id: Optional[int] = None
    organization_id: Optional[int] = None
    birthday: Optional[datetime] = None
    is_ieee_member: Optional[bool] = None
    ieee_member_id: Optional[str] = None


class UserResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    name: str
    nick: Optional[str]
    email: str
    country_code: Optional[str]
    phone: Optional[str]
    identification: Optional[str]
    university_id: Optional[int]
    organization_id: Optional[int]
    birthday: Optional[datetime]
    is_ieee_member: bool
    ieee_member_id: Optional[str]
    created_at: datetime
    university: Optional[UniversityResponse] = None
    organization: Optional[OrganizationResponse] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """Schema para crear evento"""
    name: str
    description: Optional[str] = None
    location: str
    event_date: datetime
    event_end_date: Optional[datetime] = None  # Fecha de finalización del evento
    event_duration_days: Optional[int] = 1  # Duración del evento en días
    organization_id: Optional[int] = None  # ID de organización (opcional)
    whatsapp_template: Optional[str] = None  # Template personalizado de WhatsApp
    email_template: Optional[str] = None  # Template personalizado de Email
    whatsapp_image_path: Optional[str] = None  # Ruta de la imagen para WhatsApp
    send_qr_with_whatsapp: Optional[bool] = False  # Enviar QR con mensaje de WhatsApp


class EventUpdate(BaseModel):
    """Schema para actualizar evento"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    event_duration_days: Optional[int] = None
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None
    whatsapp_template: Optional[str] = None  # Template personalizado de WhatsApp
    email_template: Optional[str] = None  # Template personalizado de Email
    whatsapp_image_path: Optional[str] = None  # Ruta de la imagen para WhatsApp
    send_qr_with_whatsapp: Optional[bool] = None  # Enviar QR con mensaje de WhatsApp


class EventResponse(BaseModel):
    """Schema para respuesta de evento"""
    id: int
    name: str
    description: Optional[str]
    location: str
    event_date: datetime
    event_end_date: Optional[datetime] = None
    event_duration_days: int = 1
    organization_id: Optional[int]
    whatsapp_template: Optional[str] = None  # Template personalizado de WhatsApp
    email_template: Optional[str] = None  # Template personalizado de Email
    whatsapp_image_path: Optional[str] = None  # Ruta de la imagen para WhatsApp
    send_qr_with_whatsapp: bool = False  # Enviar QR con mensaje de WhatsApp
    is_active: bool
    created_at: datetime
    organization: Optional[OrganizationResponse] = None

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    """Schema para crear ticket"""
    user_id: int
    event_id: int
    companions: int = 0  # Cantidad de acompañantes (0-4)
    validation_mode: Optional[str] = 'once'  # 'once' = 1 vez total, 'daily' = 1 vez por día

    @validator('companions')
    def validate_companions(cls, v):
        if v < 0 or v > 4:
            raise ValueError('La cantidad de acompañantes debe estar entre 0 y 4')
        return v

    @validator('validation_mode')
    def validate_validation_mode(cls, v):
        if v not in ['once', 'daily']:
            raise ValueError('El modo de validación debe ser "once" o "daily"')
        return v


class TicketUpdate(BaseModel):
    """Schema para actualizar ticket"""
    companions: Optional[int] = None
    validation_mode: Optional[str] = None

    @validator('companions')
    def validate_companions(cls, v):
        if v is not None and (v < 0 or v > 4):
            raise ValueError('La cantidad de acompañantes debe estar entre 0 y 4')
        return v

    @validator('validation_mode')
    def validate_validation_mode(cls, v):
        if v is not None and v not in ['once', 'daily']:
            raise ValueError('El modo de validación debe ser "once" o "daily"')
        return v


class ValidationLogResponse(BaseModel):
    """Schema para respuesta de log de validación"""
    id: int
    ticket_id: int
    validator_id: int
    validated_at: datetime
    success: bool
    notes: Optional[str]

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Schema para respuesta de ticket"""
    id: int
    ticket_code: str
    user_id: int
    event_id: int
    companions: int
    validation_mode: str
    created_at: datetime
    is_used: bool
    used_at: Optional[datetime]
    user: Optional[UserResponse] = None
    event: Optional[EventResponse] = None
    validations: List[ValidationLogResponse] = []

    class Config:
        from_attributes = True


class TicketValidation(BaseModel):
    """Schema para validación de ticket"""
    ticket_code: str


class TicketValidationResponse(BaseModel):
    """Schema para respuesta de validación"""
    valid: bool
    message: str
    ticket: Optional[TicketResponse] = None
    user: Optional[UserResponse] = None
    event: Optional[EventResponse] = None
    validation_count: Optional[int] = None  # Número de validaciones previas
    is_second_validation: Optional[bool] = False  # Si es la segunda validación del día


# Schemas de Autenticación
class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema para respuesta de token"""
    access_token: str
    token_type: str


class AdminUserCreate(BaseModel):
    """Schema para crear usuario administrador o validador"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str  # "admin" o "validator"
    access_start: Optional[datetime] = None  # Para validadores
    access_end: Optional[datetime] = None  # Para validadores


class AdminUserResponse(BaseModel):
    """Schema para respuesta de usuario admin"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    access_start: Optional[datetime]
    access_end: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Schema para actualizar usuario admin"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    access_start: Optional[datetime] = None
    access_end: Optional[datetime] = None
    password: Optional[str] = None
