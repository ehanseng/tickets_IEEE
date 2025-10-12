from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional


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


# Schemas de Usuario
class UserCreate(BaseModel):
    """Schema para crear usuario"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    identification: Optional[str] = None  # Cédula
    university_id: Optional[int] = None  # ID de universidad
    is_ieee_member: bool = False  # Miembro activo de IEEE


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    university_id: Optional[int] = None
    birthday: Optional[datetime] = None
    is_ieee_member: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    name: str
    email: str
    phone: Optional[str]
    identification: Optional[str]
    university_id: Optional[int]
    is_ieee_member: bool
    created_at: datetime
    university: Optional[UniversityResponse] = None

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """Schema para crear evento"""
    name: str
    description: Optional[str] = None
    location: str
    event_date: datetime


class EventUpdate(BaseModel):
    """Schema para actualizar evento"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class EventResponse(BaseModel):
    """Schema para respuesta de evento"""
    id: int
    name: str
    description: Optional[str]
    location: str
    event_date: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    """Schema para crear ticket"""
    user_id: int
    event_id: int
    companions: int = 0  # Cantidad de acompañantes (0-4)

    @validator('companions')
    def validate_companions(cls, v):
        if v < 0 or v > 4:
            raise ValueError('La cantidad de acompañantes debe estar entre 0 y 4')
        return v


class TicketUpdate(BaseModel):
    """Schema para actualizar ticket"""
    companions: Optional[int] = None

    @validator('companions')
    def validate_companions(cls, v):
        if v is not None and (v < 0 or v > 4):
            raise ValueError('La cantidad de acompañantes debe estar entre 0 y 4')
        return v


class TicketResponse(BaseModel):
    """Schema para respuesta de ticket"""
    id: int
    ticket_code: str
    user_id: int
    event_id: int
    companions: int
    created_at: datetime
    is_used: bool
    used_at: Optional[datetime]

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
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    access_start: Optional[datetime] = None
    access_end: Optional[datetime] = None
    password: Optional[str] = None
