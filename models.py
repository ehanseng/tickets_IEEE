from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class University(Base):
    """Modelo de Universidad"""
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    short_name = Column(String, nullable=True)  # Nombre corto o siglas
    is_active = Column(Boolean, default=True)
    has_ieee_branch = Column(Boolean, default=False)  # Tiene rama IEEE
    ieee_contact_email = Column(String, nullable=True)  # Email de contacto de la rama IEEE
    ieee_facebook = Column(String, nullable=True)  # Facebook de la rama IEEE
    ieee_instagram = Column(String, nullable=True)  # Instagram de la rama IEEE
    ieee_twitter = Column(String, nullable=True)  # Twitter de la rama IEEE
    ieee_tiktok = Column(String, nullable=True)  # TikTok de la rama IEEE
    ieee_website = Column(String, nullable=True)  # Sitio web de la rama IEEE
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="university")


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Contraseña hasheada
    phone = Column(String, nullable=True)
    identification = Column(String, nullable=True)  # Cédula
    birthday = Column(DateTime, nullable=True)  # Fecha de cumpleaños
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)  # Universidad (FK)
    is_ieee_member = Column(Boolean, default=False)  # Miembro activo de IEEE
    password_reset_token = Column(String, nullable=True)  # Token para recuperar contraseña
    password_reset_expires = Column(DateTime, nullable=True)  # Expiración del token
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tickets = relationship("Ticket", back_populates="user")
    university = relationship("University", back_populates="users")


class Event(Base):
    """Modelo de Evento"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relación con tickets
    tickets = relationship("Ticket", back_populates="event")


class Ticket(Base):
    """Modelo de Ticket"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    companions = Column(Integer, default=0)  # Cantidad de acompañantes (0-4)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    qr_path = Column(String, nullable=True)  # Ruta del archivo QR generado

    # URL única y PIN para acceso del usuario
    unique_url = Column(String, unique=True, index=True, nullable=True)  # URL única del ticket
    access_pin = Column(String, nullable=True)  # PIN de 6 dígitos para acceso

    # Relaciones
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")


class RoleEnum(enum.Enum):
    """Roles de sistema"""
    ADMIN = "admin"
    VALIDATOR = "validator"


class AdminUser(Base):
    """Modelo de Usuario Administrador y Validador"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Campos específicos para validadores
    access_start = Column(DateTime, nullable=True)  # Inicio de acceso temporal
    access_end = Column(DateTime, nullable=True)  # Fin de acceso temporal

    # Relación con validaciones
    validations = relationship("ValidationLog", back_populates="validator")


class ValidationLog(Base):
    """Registro de validaciones realizadas"""
    __tablename__ = "validation_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    validator_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    validated_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relaciones
    ticket = relationship("Ticket")
    validator = relationship("AdminUser", back_populates="validations")
