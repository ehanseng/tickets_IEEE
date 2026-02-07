"""
Script para verificar los emails de un usuario específico.
Ejecutar con: python check_user_emails.py
"""
from database import SessionLocal
import models


def main():
    db = SessionLocal()

    try:
        # Buscar el usuario de erick
        user = db.query(models.User).filter(
            models.User.email.like('%erick%')
        ).first()

        if not user:
            # Buscar cualquier usuario con emails asignados
            user = db.query(models.User).filter(
                models.User.email_personal.isnot(None)
            ).first()

        if user:
            print(f"Usuario ID: {user.id}")
            print(f"Nombre: {user.name}")
            print(f"Email principal (legacy): {user.email}")
            print(f"Email personal: '{user.email_personal}'")
            print(f"Email institucional: '{user.email_institutional}'")
            print(f"Email IEEE: '{user.email_ieee}'")
            print(f"Primary email type: '{user.primary_email_type}'")
        else:
            print("No se encontró ningún usuario")

        # También mostrar conteo de usuarios con emails asignados
        print("\n--- Estadísticas ---")
        total = db.query(models.User).count()
        with_personal = db.query(models.User).filter(
            models.User.email_personal.isnot(None),
            models.User.email_personal != ''
        ).count()
        with_institutional = db.query(models.User).filter(
            models.User.email_institutional.isnot(None),
            models.User.email_institutional != ''
        ).count()
        with_ieee = db.query(models.User).filter(
            models.User.email_ieee.isnot(None),
            models.User.email_ieee != ''
        ).count()

        print(f"Total usuarios: {total}")
        print(f"Con email personal: {with_personal}")
        print(f"Con email institucional: {with_institutional}")
        print(f"Con email IEEE: {with_ieee}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
