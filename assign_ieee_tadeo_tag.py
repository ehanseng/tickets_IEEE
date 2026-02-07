"""
Script para asignar el tag IEEE Tadeo a todos los usuarios que no lo tienen
"""
import sys
import io
from database import SessionLocal
import models

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

try:
    # Buscar el tag IEEE Tadeo
    tag = db.query(models.Tag).filter(models.Tag.name == 'IEEE Tadeo').first()

    if not tag:
        print("X Tag 'IEEE Tadeo' no encontrado")
        exit(1)

    print(f"OK Tag 'IEEE Tadeo' encontrado (ID: {tag.id})")

    # Obtener todos los usuarios
    all_users = db.query(models.User).all()
    print(f"\nTotal de usuarios: {len(all_users)}")

    # Contar cuántos usuarios ya tienen el tag
    users_with_tag = 0
    users_without_tag = 0

    for user in all_users:
        if tag in user.tags:
            users_with_tag += 1
        else:
            user.tags.append(tag)
            users_without_tag += 1
            print(f"  + Tag agregado a: {user.name} ({user.email})")

    db.commit()

    print(f"\n{'='*60}")
    print("RESUMEN")
    print(f"{'='*60}")
    print(f"Usuarios que ya tenian el tag: {users_with_tag}")
    print(f"Usuarios a los que se agrego el tag: {users_without_tag}")
    print(f"\nOK Proceso completado exitosamente")

except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
