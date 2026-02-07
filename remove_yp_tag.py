"""
Script para remover el tag IEEE YP Co de los primeros dos usuarios
"""
import sys
import io
from database import SessionLocal
import models

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = SessionLocal()

try:
    # Buscar el tag IEEE YP Co
    tag = db.query(models.Tag).filter(models.Tag.name == 'IEEE YP Co').first()

    if not tag:
        print("X Tag 'IEEE YP Co' no encontrado")
        exit(1)

    print(f"OK Tag 'IEEE YP Co' encontrado (ID: {tag.id})")

    # Obtener los usuarios con IDs 1 y 3
    user_ids = [1, 3]
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()

    print(f"\nUsuarios a procesar: {len(users)}")

    for user in users:
        if tag in user.tags:
            user.tags.remove(tag)
            print(f"  - Tag removido de: {user.name} ({user.email})")
        else:
            print(f"  - {user.name} ({user.email}) no tenia el tag")

    db.commit()

    print(f"\nOK Proceso completado exitosamente")

except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
