"""
Script para agregar el campo photo_path al modelo User
Ejecutar con: python migrate_add_photo.py
"""
import os
import sys

from sqlalchemy import text
from database import SessionLocal, engine


def main():
    print("=" * 60)
    print("MIGRACIÓN: Agregar campo photo_path a usuarios")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Detectar tipo de base de datos
        db_url = str(engine.url)
        is_mysql = 'mysql' in db_url.lower()
        is_sqlite = 'sqlite' in db_url.lower()

        print(f"\nTipo de base de datos: {'MySQL' if is_mysql else 'SQLite' if is_sqlite else 'Otro'}")

        # Verificar si la columna ya existe
        if is_mysql:
            result = db.execute(text("DESCRIBE users"))
            existing_columns = [row[0] for row in result.fetchall()]
        else:
            # SQLite
            result = db.execute(text("PRAGMA table_info(users)"))
            existing_columns = [row[1] for row in result.fetchall()]

        print(f"Columnas existentes en 'users': {len(existing_columns)}")

        if 'photo_path' in existing_columns:
            print("\n[OK] La columna photo_path ya existe. No hay cambios que realizar.")
            return

        # Ejecutar la migración
        print("\nAgregando columna photo_path...")

        if is_mysql:
            # MySQL: agregar después de nick
            alter_sql = "ALTER TABLE users ADD COLUMN photo_path VARCHAR(500) NULL AFTER nick"
        else:
            # SQLite: no soporta AFTER, agregar al final
            alter_sql = "ALTER TABLE users ADD COLUMN photo_path VARCHAR(500) NULL"

        print(f"SQL: {alter_sql}")
        db.execute(text(alter_sql))
        db.commit()

        print("\n" + "=" * 60)
        print("[OK] MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)

        # Verificar columnas después de la migración
        if is_mysql:
            result = db.execute(text("DESCRIBE users"))
            new_columns = [row[0] for row in result.fetchall()]
        else:
            result = db.execute(text("PRAGMA table_info(users)"))
            new_columns = [row[1] for row in result.fetchall()]

        if 'photo_path' in new_columns:
            print("\n[OK] Columna photo_path agregada correctamente")
        else:
            print("\n[ERROR] La columna no se agregó correctamente")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
