from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema para crear usuario"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    identification: Optional[str] = None  # Cédula
    university: Optional[str] = None  # Universidad


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    identification: Optional[str] = None
    university: Optional[str] = None


class UserResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    name: str
    email: str
    phone: Optional[str]
    identification: Optional[str]
    university: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    """Schema para crear evento"""
    name: str
    description: Optional[str] = None
    location: str
    event_date: datetime


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
