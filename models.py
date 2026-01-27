from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class StudyType(enum.Enum):
    """Tipos de estudio"""
    pregrado = "pregrado"
    posgrado = "posgrado"
    otro = "otro"


# Tabla de asociación many-to-many entre Users y Tags
user_tags = Table(
    'user_tags',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

# Tabla de asociación many-to-many entre Users y IEEESocieties
user_societies = Table(
    'user_societies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('society_id', Integer, ForeignKey('ieee_societies.id'), primary_key=True),
    Column('is_primary', Boolean, default=False),  # Sociedad principal
    Column('created_at', DateTime, default=datetime.utcnow)
)

# Tabla de asociación many-to-many entre Users y Skills
user_skills = Table(
    'user_skills',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Tag(Base):
    """Modelo de Tag/Etiqueta para categorizar usuarios"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Nombre del tag (ej: "IEEE Tadeo", "IEEE YP Co")
    color = Column(String(20), nullable=True, default="#3B82F6")  # Color hex para el badge
    description = Column(Text, nullable=True)  # Descripción del tag
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación many-to-many con usuarios
    users = relationship("User", secondary=user_tags, back_populates="tags")


# ============================================================
# CATÁLOGOS PARA PERFILAMIENTO AVANZADO
# ============================================================

class AcademicProgram(Base):
    """Programas académicos disponibles"""
    __tablename__ = "academic_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    short_name = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)  # Ingeniería, Diseño, etc.
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="academic_program")


class SemesterRange(Base):
    """Rangos de semestre"""
    __tablename__ = "semester_ranges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "1º a 3º (Ciclo Básico)"
    min_semester = Column(Integer, nullable=True)
    max_semester = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="semester_range")


class EnglishLevel(Base):
    """Niveles de inglés (Marco Común Europeo)"""
    __tablename__ = "english_levels"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), nullable=False, unique=True)  # A1, A2, B1, etc.
    name = Column(String(100), nullable=False)  # "A1 - Principiante"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="english_level")


class IEEEMembershipStatus(Base):
    """Estados de membresía IEEE"""
    __tablename__ = "ieee_membership_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "Student Member"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="ieee_membership_status")


class IEEESociety(Base):
    """Sociedades técnicas IEEE"""
    __tablename__ = "ieee_societies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, unique=True)  # CS, RAS, PES, etc.
    name = Column(String(200), nullable=False)  # "Computer Society"
    full_name = Column(String(200), nullable=True)  # Nombre completo
    description = Column(Text, nullable=True)
    society_type = Column(String(50), default="technical")  # technical, affinity
    color = Column(String(20), nullable=True, default="#0066cc")
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación many-to-many con usuarios
    users = relationship("User", secondary=user_societies, back_populates="ieee_societies")


class InterestArea(Base):
    """Áreas de interés / Roles en la Rama"""
    __tablename__ = "interest_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "Gestión y Liderazgo"
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Nombre del icono (Font Awesome)
    color = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="interest_area")


class AvailabilityLevel(Base):
    """Niveles de disponibilidad de tiempo"""
    __tablename__ = "availability_levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "Baja (Menos de 2 horas)"
    hours_description = Column(String(100), nullable=True)  # "Menos de 2 horas"
    min_hours = Column(Integer, nullable=True)
    max_hours = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="availability_level")


class CommunicationChannel(Base):
    """Canales de comunicación preferidos"""
    __tablename__ = "communication_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "WhatsApp"
    description = Column(String(200), nullable=True)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="preferred_channel")


class Skill(Base):
    """Habilidades (técnicas y blandas)"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # "technical" o "soft"
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación many-to-many con usuarios
    users = relationship("User", secondary=user_skills, back_populates="skills")


class Organization(Base):
    """Modelo de Organización/Entidad Externa"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)  # Nombre de la organización
    short_name = Column(String(50), nullable=True)  # Nombre corto
    description = Column(Text, nullable=True)  # Descripción
    logo_path = Column(String(500), nullable=True)  # Ruta del logo

    # Templates personalizados
    email_template = Column(Text, nullable=True)  # Template de email personalizado
    whatsapp_template = Column(Text, nullable=True)  # Template de WhatsApp personalizado

    # Información de contacto
    contact_email = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)

    # Redes sociales
    facebook = Column(String(500), nullable=True)
    instagram = Column(String(500), nullable=True)
    twitter = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    users = relationship("User", back_populates="organization")
    events = relationship("Event", back_populates="organization")


class University(Base):
    """Modelo de Universidad"""
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    short_name = Column(String(50), nullable=True)  # Nombre corto o siglas
    is_active = Column(Boolean, default=True)
    has_ieee_branch = Column(Boolean, default=False)  # Tiene rama IEEE
    ieee_contact_email = Column(String(200), nullable=True)  # Email de contacto de la rama IEEE
    ieee_facebook = Column(String(500), nullable=True)  # Facebook de la rama IEEE
    ieee_instagram = Column(String(500), nullable=True)  # Instagram de la rama IEEE
    ieee_twitter = Column(String(500), nullable=True)  # Twitter de la rama IEEE
    ieee_tiktok = Column(String(500), nullable=True)  # TikTok de la rama IEEE
    ieee_website = Column(String(500), nullable=True)  # Sitio web de la rama IEEE
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuarios
    users = relationship("User", back_populates="university")


class User(Base):
    """Modelo de Usuario/Contacto"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ============================================================
    # INFORMACIÓN BÁSICA
    # ============================================================
    name = Column(String(200), nullable=False)
    nick = Column(String(100), nullable=True)  # Apodo o forma corta de llamar al usuario
    photo_path = Column(String(500), nullable=True)  # Ruta de la foto de perfil
    email = Column(String(200), unique=True, index=True, nullable=False)  # Email principal (para OTP)
    email_personal = Column(String(200), nullable=True)  # Email personal
    email_institutional = Column(String(200), nullable=True)  # Email institucional (universidad)
    email_ieee = Column(String(200), nullable=True)  # Email IEEE
    primary_email_type = Column(String(20), default='email')  # 'email', 'personal', 'institutional', 'ieee'
    hashed_password = Column(String(255), nullable=True)  # Contraseña hasheada
    country_code = Column(String(10), nullable=True, default="+57")  # Código de país para teléfono
    phone = Column(String(20), nullable=True)
    identification = Column(String(50), nullable=True)  # Cédula
    birthday = Column(DateTime, nullable=True)  # Fecha de cumpleaños

    # ============================================================
    # INFORMACIÓN ACADÉMICA
    # ============================================================
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    academic_program_id = Column(Integer, ForeignKey("academic_programs.id"), nullable=True)
    semester_range_id = Column(Integer, ForeignKey("semester_ranges.id"), nullable=True)
    expected_graduation = Column(DateTime, nullable=True)  # Fecha estimada de grado
    english_level_id = Column(Integer, ForeignKey("english_levels.id"), nullable=True)

    # ============================================================
    # INFORMACIÓN IEEE
    # ============================================================
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Organización externa
    is_ieee_member = Column(Boolean, default=False)  # Calculado: True si tiene ieee_member_id
    ieee_member_id = Column(String(50), nullable=True)  # Número de membresía IEEE
    ieee_membership_status_id = Column(Integer, ForeignKey("ieee_membership_statuses.id"), nullable=True)
    ieee_roles_history = Column(Text, nullable=True)  # Roles previos en IEEE (texto libre o JSON)
    branch_role = Column(String(50), nullable=True)  # Rol interno en la rama (presidente, vicepresidente, etc.)

    # ============================================================
    # PERFILAMIENTO Y DISPONIBILIDAD
    # ============================================================
    interest_area_id = Column(Integer, ForeignKey("interest_areas.id"), nullable=True)  # Área de interés principal
    availability_level_id = Column(Integer, ForeignKey("availability_levels.id"), nullable=True)
    preferred_channel_id = Column(Integer, ForeignKey("communication_channels.id"), nullable=True)
    goals_in_branch = Column(Text, nullable=True)  # Qué busca en la rama (texto libre)

    # ============================================================
    # METADATOS
    # ============================================================
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    profile_completed = Column(Boolean, default=False)  # Ha completado el perfil
    profile_completed_at = Column(DateTime, nullable=True)
    last_profile_update = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ============================================================
    # SEGUIMIENTO DE ACCESO AL PORTAL
    # ============================================================
    last_login = Column(DateTime, nullable=True)  # Ultimo inicio de sesion
    login_count = Column(Integer, default=0)  # Cantidad de inicios de sesion
    first_login = Column(DateTime, nullable=True)  # Primer inicio de sesion

    # ============================================================
    # RELACIONES
    # ============================================================
    tickets = relationship("Ticket", back_populates="user")
    university = relationship("University", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    tags = relationship("Tag", secondary=user_tags, back_populates="users")

    # Nuevas relaciones de perfilamiento
    academic_program = relationship("AcademicProgram", back_populates="users")
    semester_range = relationship("SemesterRange", back_populates="users")
    english_level = relationship("EnglishLevel", back_populates="users")
    ieee_membership_status = relationship("IEEEMembershipStatus", back_populates="users")
    ieee_societies = relationship("IEEESociety", secondary=user_societies, back_populates="users")
    interest_area = relationship("InterestArea", back_populates="users")
    availability_level = relationship("AvailabilityLevel", back_populates="users")
    preferred_channel = relationship("CommunicationChannel", back_populates="users")
    skills = relationship("Skill", secondary=user_skills, back_populates="users")
    studies = relationship("UserStudy", back_populates="user", cascade="all, delete-orphan")


class UserStudy(Base):
    """Estudios adicionales del usuario (pregrado, posgrado, etc.)"""
    __tablename__ = "user_studies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    study_type = Column(Enum(StudyType), nullable=False)  # pregrado/posgrado/otro
    program_name = Column(String(200), nullable=False)     # Nombre de la carrera/programa
    institution = Column(String(200), nullable=True)       # Institución (si es externa a UTadeo)
    is_primary = Column(Boolean, default=False)            # Estudio principal para mostrar
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    user = relationship("User", back_populates="studies")


class Event(Base):
    """Modelo de Evento"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=False)
    event_date = Column(DateTime, nullable=False)
    event_end_date = Column(DateTime, nullable=True)  # Fecha de finalización del evento
    event_duration_days = Column(Integer, default=1)  # Duración del evento en días
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Organización del evento
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Tipo de evento: 'organized' = Organizamos (con tickets), 'participation' = Participamos (solo galería)
    event_type = Column(String(20), default='organized')

    # Templates personalizados para este evento (opcional)
    whatsapp_template = Column(Text, nullable=True)  # Template de WhatsApp para este evento
    email_template = Column(Text, nullable=True)  # Template de Email para este evento
    whatsapp_image_path = Column(String(500), nullable=True)  # Ruta de la imagen para WhatsApp
    send_qr_with_whatsapp = Column(Boolean, default=False)  # Enviar QR junto con mensaje de WhatsApp

    # Relaciones
    tickets = relationship("Ticket", back_populates="event")
    organization = relationship("Organization", back_populates="events")
    gallery_images = relationship("EventGalleryImage", back_populates="event", cascade="all, delete-orphan")


class EventGalleryImage(Base):
    """Imágenes de galería para eventos"""
    __tablename__ = "event_gallery_images"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(500), nullable=False)
    caption = Column(String(300), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    event = relationship("Event", back_populates="gallery_images")


class Ticket(Base):
    """Modelo de Ticket"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    companions = Column(Integer, default=0)  # Cantidad de acompañantes (0-4)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)  # Deprecated: usar validation_logs para verificar estado
    used_at = Column(DateTime, nullable=True)  # Deprecated: usar validation_logs para ver última validación
    qr_path = Column(String(500), nullable=True)  # Ruta del archivo QR generado

    # Configuración de validaciones
    validation_mode = Column(String(20), default='once')  # 'once' = 1 vez total, 'daily' = 1 vez por día

    # URL única y PIN para acceso del usuario
    unique_url = Column(String(100), unique=True, index=True, nullable=True)  # URL única del ticket
    access_pin = Column(String(10), nullable=True)  # PIN de 6 dígitos para acceso

    # Relaciones
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    validations = relationship("ValidationLog", back_populates="ticket")


class BranchRoleEnum(enum.Enum):
    """Roles internos de la rama estudiantil IEEE"""
    PRESIDENTE = "presidente"
    VICEPRESIDENTE = "vicepresidente"
    SECRETARIO = "secretario"
    TESORERO = "tesorero"
    WEBMASTER = "webmaster"
    CONSEJERO = "consejero"
    MENTOR = "mentor"


class RoleEnum(enum.Enum):
    """Roles de sistema"""
    ADMIN = "admin"
    VALIDATOR = "validator"
    META_REVIEWER = "meta_reviewer"  # Solo lectura limitada para revisión de Meta


class AdminUser(Base):
    """Modelo de Usuario Administrador y Validador"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(Enum(RoleEnum, values_callable=lambda x: [e.value for e in x]), nullable=False, default=RoleEnum.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Campos específicos para validadores
    access_start = Column(DateTime, nullable=True)  # Inicio de acceso temporal
    access_end = Column(DateTime, nullable=True)  # Fin de acceso temporal

    # Vinculacion con contacto del portal (opcional)
    linked_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Permisos por seccion (JSON) - null = acceso completo segun rol
    # Ejemplo: {"events": true, "tickets": true, "users": false, "messages": false}
    permissions = Column(Text, nullable=True)  # JSON string

    # Relaciones
    validations = relationship("ValidationLog", back_populates="validator")
    campaigns = relationship("MessageCampaign", back_populates="creator")
    linked_user = relationship("User", backref="admin_account", foreign_keys=[linked_user_id])


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
    execution_type = Column(String(20), default="automatic")  # "automatic" o "manual"
    notes = Column(Text, nullable=True)  # Notas adicionales


class MessageCampaign(Base):
    """Campaña de mensajes masivos"""
    __tablename__ = "message_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    link_text = Column(String(200), nullable=True)
    has_image = Column(Boolean, default=False)
    image_path = Column(String(500), nullable=True)

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
    email_error = Column(String(500), nullable=True)

    # Estado de WhatsApp
    whatsapp_sent = Column(Boolean, default=False)
    whatsapp_sent_at = Column(DateTime, nullable=True)
    whatsapp_message_id = Column(String(100), nullable=True)  # ID del mensaje de WhatsApp
    whatsapp_status = Column(String(20), default="pending")  # pending, sent, delivered, read, failed
    whatsapp_status_updated_at = Column(DateTime, nullable=True)
    whatsapp_error = Column(String(500), nullable=True)

    # Relaciones
    campaign = relationship("MessageCampaign", back_populates="recipients")
    user = relationship("User")


class WhatsAppTemplate(Base):
    """Templates de WhatsApp para Meta Cloud API"""
    __tablename__ = "whatsapp_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Nombre del template (sin espacios, minúsculas)
    display_name = Column(String(200), nullable=False)  # Nombre para mostrar
    category = Column(String(50), default="UTILITY")  # UTILITY, MARKETING, AUTHENTICATION
    language = Column(String(10), default="es")  # es, en, etc.

    # Componentes del template
    header_type = Column(String(20), nullable=True)  # TEXT, IMAGE, VIDEO, DOCUMENT, NONE
    header_text = Column(String(500), nullable=True)  # Texto del header (si es TEXT)
    body_text = Column(Text, nullable=False)  # Cuerpo del mensaje (requerido)
    footer_text = Column(String(200), nullable=True)  # Texto del footer

    # Variables (ejemplo: {{1}}, {{2}})
    variables_count = Column(Integer, default=0)  # Cantidad de variables en el body
    variable_examples = Column(Text, nullable=True)  # JSON con ejemplos de variables

    # Estado en Meta
    meta_template_id = Column(String(100), nullable=True)  # ID del template en Meta
    meta_status = Column(String(20), default="LOCAL")  # LOCAL, PENDING, APPROVED, REJECTED
    meta_rejection_reason = Column(Text, nullable=True)

    # Metadatos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)  # Cuando se envió a Meta


class WhatsAppMessage(Base):
    """Mensajes de WhatsApp recibidos"""
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    wa_message_id = Column(String(100), unique=True, nullable=False)  # ID del mensaje de WhatsApp

    # Información del remitente
    from_number = Column(String(50), nullable=False)  # Número que envió el mensaje
    from_name = Column(String(200), nullable=True)  # Nombre del contacto (si está disponible)

    # Contenido del mensaje
    message_type = Column(String(20), nullable=False)  # text, image, audio, video, document, location, contacts, sticker
    text_body = Column(Text, nullable=True)  # Texto del mensaje (si es tipo text)
    media_id = Column(String(200), nullable=True)  # ID del media (si aplica)
    media_url = Column(String(500), nullable=True)  # URL del media descargado
    media_mime_type = Column(String(100), nullable=True)
    caption = Column(Text, nullable=True)  # Caption del media

    # Contexto (si es respuesta a otro mensaje)
    context_message_id = Column(String(100), nullable=True)  # ID del mensaje al que responde
    is_forwarded = Column(Boolean, default=False)

    # Estado
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    replied = Column(Boolean, default=False)
    replied_at = Column(DateTime, nullable=True)
    reply_message_id = Column(String(100), nullable=True)

    # Metadatos
    timestamp = Column(DateTime, nullable=False)  # Timestamp del mensaje original
    received_at = Column(DateTime, default=datetime.utcnow)  # Cuando lo recibimos
    raw_payload = Column(Text, nullable=True)  # JSON completo del webhook


class WhatsAppConversation(Base):
    """Conversaciones de WhatsApp (agrupación de mensajes por número)"""
    __tablename__ = "whatsapp_conversations"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, nullable=False)  # Número de teléfono
    contact_name = Column(String(200), nullable=True)  # Nombre del contacto

    # Vinculación con usuario del sistema (si existe)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Estado de la conversación
    is_active = Column(Boolean, default=True)  # Ventana de 24h activa
    last_message_at = Column(DateTime, nullable=True)
    last_user_message_at = Column(DateTime, nullable=True)  # Último mensaje del usuario (para ventana 24h)
    unread_count = Column(Integer, default=0)

    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    user = relationship("User", backref="whatsapp_conversation")


class UserOTP(Base):
    """Códigos OTP para autenticación de usuarios del portal"""
    __tablename__ = "user_otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)  # Código de 6 dígitos
    method = Column(String(20), nullable=False)  # 'email' o 'whatsapp'
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    user = relationship("User", backref="otp_codes")


class ProjectStatus(enum.Enum):
    """Estados de un proyecto"""
    active = "active"
    paused = "paused"
    completed = "completed"
    planning = "planning"


class Project(Base):
    """Modelo de Proyectos de la rama IEEE"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    short_description = Column(String(500), nullable=True)  # Para mostrar en cards
    description = Column(Text, nullable=True)  # Descripción completa
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)
    icon = Column(String(50), nullable=True)  # Nombre del icono (ej: "laptop", "recycle", "robot")
    color = Column(String(20), nullable=True, default="#006699")  # Color del proyecto
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_public = Column(Boolean, default=True)  # Si se muestra en la página pública
    display_order = Column(Integer, default=0)  # Orden de visualización
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
