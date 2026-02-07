"""
Script para migrar los emails existentes a los nuevos campos.
Ejecutar con: python migrate_assign_emails.py
"""
import sys
from database import SessionLocal
import models


def get_email_type(email):
    """Determina el tipo de email según el dominio"""
    if not email:
        return None

    email_lower = email.lower()

    # IEEE emails
    if 'ieee.org' in email_lower:
        return 'ieee'

    # Institutional emails
    if '.edu.co' in email_lower or email_lower.endswith('.edu'):
        return 'institutional'

    # Personal emails (default)
    return 'personal'


def main():
    print("=" * 60)
    print("MIGRACIÓN: Asignar emails a campos específicos")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Obtener todos los usuarios
        users = db.query(models.User).all()
        print(f"\nTotal usuarios: {len(users)}")

        updated_count = 0
        for user in users:
            # Solo procesar si no tiene emails asignados
            if user.email_personal or user.email_institutional or user.email_ieee:
                continue

            if not user.email:
                continue

            email_type = get_email_type(user.email)

            if email_type == 'personal':
                user.email_personal = user.email
                user.primary_email_type = 'email_personal'
            elif email_type == 'institutional':
                user.email_institutional = user.email
                user.primary_email_type = 'email_institutional'
            elif email_type == 'ieee':
                user.email_ieee = user.email
                user.primary_email_type = 'email_ieee'

            updated_count += 1
            print(f"  Usuario {user.id}: {user.email} → {email_type}")

        db.commit()

        print("\n" + "=" * 60)
        print(f"[OK] MIGRACIÓN COMPLETADA: {updated_count} usuarios actualizados")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
