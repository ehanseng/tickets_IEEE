from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    identification = Column(String, nullable=True)  # Cédula
    university = Column(String, nullable=True)  # Universidad
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con tickets
    tickets = relationship("Ticket", back_populates="user")


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

    # Relaciones
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
