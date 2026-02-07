"""
Script para agregar los nuevos campos de email al modelo User
Ejecutar con: python migrate_add_emails.py
"""
import os
import sys

from sqlalchemy import text
from database import SessionLocal, engine


def main():
    print("=" * 60)
    print("MIGRACIÓN: Agregar campos de email múltiples")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Verificar si las columnas ya existen
        result = db.execute(text("DESCRIBE users"))
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"\nColumnas existentes en 'users': {len(existing_columns)}")

        columns_to_add = []

        # Verificar cada columna nueva
        if 'email_personal' not in existing_columns:
            columns_to_add.append(
                "ADD COLUMN email_personal VARCHAR(200) NULL AFTER email"
            )
            print("  [+] Agregando: email_personal")

        if 'email_institutional' not in existing_columns:
            columns_to_add.append(
                "ADD COLUMN email_institutional VARCHAR(200) NULL AFTER email_personal"
            )
            print("  [+] Agregando: email_institutional")

        if 'email_ieee' not in existing_columns:
            columns_to_add.append(
                "ADD COLUMN email_ieee VARCHAR(200) NULL AFTER email_institutional"
            )
            print("  [+] Agregando: email_ieee")

        if 'primary_email_type' not in existing_columns:
            columns_to_add.append(
                "ADD COLUMN primary_email_type VARCHAR(20) DEFAULT 'email_personal' AFTER email_ieee"
            )
            print("  [+] Agregando: primary_email_type")

        if not columns_to_add:
            print("\n[OK] Todas las columnas ya existen. No hay cambios que realizar.")
            return

        # Ejecutar la migración
        print(f"\n\nEjecutando {len(columns_to_add)} modificaciones...")
        alter_sql = f"ALTER TABLE users {', '.join(columns_to_add)}"
        print(f"SQL: {alter_sql}")

        db.execute(text(alter_sql))
        db.commit()

        print("\n" + "=" * 60)
        print("[OK] MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)

        # Verificar columnas después de la migración
        result = db.execute(text("DESCRIBE users"))
        new_columns = [row[0] for row in result.fetchall()]
        print(f"\nColumnas después de la migración: {len(new_columns)}")

        # Mostrar las nuevas columnas de email
        email_cols = [c for c in new_columns if 'email' in c.lower()]
        print(f"Columnas de email: {email_cols}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
