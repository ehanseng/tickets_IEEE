"""
Script para crear usuario Diana Salavarrieta Sanabria
"""
import sys
import io
from database import SessionLocal
import models

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

try:
    # Verificar que el tag IEEE YP Co existe
    tag = db.query(models.Tag).filter(models.Tag.name == 'IEEE YP Co').first()

    if not tag:
        print("X Tag 'IEEE YP Co' no encontrado")
        exit(1)

    print(f"✓ Tag 'IEEE YP Co' encontrado (ID: {tag.id})")

    # Verificar que el correo no esté en uso
    existing_user = db.query(models.User).filter(
        models.User.email == 'temporal1@ieeetadeo.org'
    ).first()

    if existing_user:
        print(f"X El correo temporal1@ieeetadeo.org ya está en uso por: {existing_user.name}")
        exit(1)

    # Verificar que el teléfono no esté en uso
    existing_phone = db.query(models.User).filter(
        models.User.phone == '3155381037'
    ).first()

    if existing_phone:
        print(f"X El teléfono 3155381037 ya está en uso por: {existing_phone.name}")
        exit(1)

    print("✓ Email y teléfono disponibles")

    # Crear el nuevo usuario (sin password_hash - puede iniciar sesión vía WhatsApp)
    new_user = models.User(
        name="Diana Salavarrieta Sanabria",
        email="temporal1@ieeetadeo.org",
        phone="3155381037",
        country_code="+57",
        university_id=None  # No especificada
    )

    # Asignar el tag IEEE YP Co
    new_user.tags.append(tag)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"\n{'='*70}")
    print(f"✓ USUARIO CREADO EXITOSAMENTE")
    print(f"{'='*70}")
    print(f"ID: {new_user.id}")
    print(f"Nombre: {new_user.name}")
    print(f"Email: {new_user.email}")
    print(f"Teléfono: {new_user.country_code}{new_user.phone}")
    print(f"Inicio de sesión: Vía WhatsApp (sin contraseña)")
    print(f"Tags: {', '.join([t.name for t in new_user.tags])}")
    print(f"{'='*70}")

except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
