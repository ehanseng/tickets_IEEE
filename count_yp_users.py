"""
Script para contar usuarios con el tag IEEE YP Co
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

    print(f"Tag: {tag.name} (ID: {tag.id})")

    # Obtener usuarios con ese tag
    users = db.query(models.User).join(models.user_tags).filter(
        models.user_tags.c.tag_id == tag.id
    ).all()

    print(f"Total de usuarios con esta etiqueta: {len(users)}")
    print(f"\nUsuarios:")
    for u in users:
        # Obtener todos los tags del usuario
        all_tags = [t.name for t in u.tags]
        print(f"  - {u.name} ({u.email}) - Tags: {', '.join(all_tags)}")

except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
