from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


# Tabla de asociación many-to-many entre Users y Tags
user_tags = Table(
    'user_tags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Tag(Base):
    """Modelo de Tag/Etiqueta para categorizar usuarios"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # Nombre del tag (ej: "IEEE Tadeo", "IEEE YP Co")
    color = Column(String, nullable=True, default="#3B82F6")  # Color hex para el badge
    description = Column(Text, nullable=True)  # Descripción del tag
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación many-to-many con usuarios
    users = relationship("User", secondary=user_tags, back_populates="tags")


class Organization(Base):
    """Modelo de Organización/Entidad Externa"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # Nombre de la organización
    short_name = Column(String, nullable=True)  # Nombre corto
    description = Column(Text, nullable=True)  # Descripción
    logo_path = Column(String, nullable=True)  # Ruta del logo

    # Templates personalizados
    email_template = Column(Text, nullable=True)  # Template de email personalizado
    whatsapp_template = Column(Text, nullable=True)  # Template de WhatsApp personalizado

    # Información de contacto
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Redes sociales
    facebook = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    twitter = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    users = relationship("User", back_populates="organization")
    events = relationship("Event", back_populates="organization")


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
    nick = Column(String, nullable=True)  # Apodo o forma corta de llamar al usuario
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Contraseña hasheada
    country_code = Column(String, nullable=True, default="+57")  # Código de país para teléfono
    phone = Column(String, nullable=True)
    identification = Column(String, nullable=True)  # Cédula
    birthday = Column(DateTime, nullable=True)  # Fecha de cumpleaños
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)  # Universidad (FK)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Organización externa (FK)
    is_ieee_member = Column(Boolean, default=False)  # Miembro activo de IEEE
    ieee_member_id = Column(String, nullable=True)  # ID de membresía IEEE
    password_reset_token = Column(String, nullable=True)  # Token para recuperar contraseña
    password_reset_expires = Column(DateTime, nullable=True)  # Expiración del token
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tickets = relationship("Ticket", back_populates="user")
    university = relationship("University", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    tags = relationship("Tag", secondary=user_tags, back_populates="users")


class Event(Base):
    """Modelo de Evento"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Organización del evento
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Templates personalizados para este evento (opcional)
    whatsapp_template = Column(Text, nullable=True)  # Template de WhatsApp para este evento
    email_template = Column(Text, nullable=True)  # Template de Email para este evento
    whatsapp_image_path = Column(String, nullable=True)  # Ruta de la imagen para WhatsApp
    send_qr_with_whatsapp = Column(Boolean, default=False)  # Enviar QR junto con mensaje de WhatsApp

    # Relaciones
    tickets = relationship("Ticket", back_populates="event")
    organization = relationship("Organization", back_populates="events")


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

    # Relaciones
    validations = relationship("ValidationLog", back_populates="validator")
    campaigns = relationship("MessageCampaign", back_populates="creator")


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


class BirthdayCheckLog(Base):
    """Registro de ejecuciones del sistema de cumpleaños"""
    __tablename__ = "birthday_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    birthdays_found = Column(Integer, default=0)  # Cantidad de cumpleaños encontrados
    emails_sent = Column(Integer, default=0)  # Emails enviados exitosamente
    emails_failed = Column(Integer, default=0)  # Emails fallidos
    whatsapp_sent = Column(Integer, default=0)  # WhatsApps enviados exitosamente
    whatsapp_failed = Column(Integer, default=0)  # WhatsApps fallidos
    whatsapp_available = Column(Boolean, default=False)  # Si WhatsApp estaba disponible
    execution_type = Column(String, default="automatic")  # "automatic" o "manual"
    notes = Column(Text, nullable=True)  # Notas adicionales


class MessageCampaign(Base):
    """Campaña de mensajes masivos"""
    __tablename__ = "message_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String, nullable=True)
    link_text = Column(String, nullable=True)
    has_image = Column(Boolean, default=False)
    image_path = Column(String, nullable=True)

    # Canales de envío
    send_email = Column(Boolean, default=True)
    send_whatsapp = Column(Boolean, default=False)

    # Estadísticas
    total_recipients = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    whatsapp_sent = Column(Integer, default=0)
    whatsapp_failed = Column(Integer, default=0)

    # Usuario que creó la campaña
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    creator = relationship("AdminUser", back_populates="campaigns")
    recipients = relationship("MessageRecipient", back_populates="campaign", cascade="all, delete-orphan")


class MessageRecipient(Base):
    """Destinatario individual de una campaña"""
    __tablename__ = "message_recipients"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("message_campaigns.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Estado de email
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    email_error = Column(String, nullable=True)

    # Estado de WhatsApp
    whatsapp_sent = Column(Boolean, default=False)
    whatsapp_sent_at = Column(DateTime, nullable=True)
    whatsapp_message_id = Column(String, nullable=True)  # ID del mensaje de WhatsApp
    whatsapp_status = Column(String, default="pending")  # pending, sent, delivered, read, failed
    whatsapp_status_updated_at = Column(DateTime, nullable=True)
    whatsapp_error = Column(String, nullable=True)

    # Relaciones
    campaign = relationship("MessageCampaign", back_populates="recipients")
    user = relationship("User")
