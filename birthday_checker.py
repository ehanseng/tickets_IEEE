"""
Script para verificar cumpleaños y enviar correos de felicitación

Este script debe ejecutarse diariamente (por ejemplo, a las 8:00 AM)
usando un cron job o similar.
"""
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import SessionLocal
import models
from email_service import email_service


def check_and_send_birthday_emails():
    """
    Verifica los cumpleaños del día actual y envía correos de felicitación
    """
    db: Session = SessionLocal()

    try:
        # Obtener la fecha de hoy (solo mes y día, ignorar año)
        today = datetime.now()
        today_month = today.month
        today_day = today.day

        print(f"=== Verificador de Cumpleaños - {today.strftime('%Y-%m-%d')} ===")
        print(f"Buscando usuarios con cumpleaños en {today.strftime('%d/%m')}...")

        # Buscar usuarios que cumplan años hoy
        # Filtramos por mes y día, sin importar el año
        users = db.query(models.User).filter(
            models.User.birthday.isnot(None)
        ).all()

        birthday_users = []
        for user in users:
            if user.birthday and user.birthday.month == today_month and user.birthday.day == today_day:
                birthday_users.append(user)

        if not birthday_users:
            print("No hay cumpleaños hoy.")
            print("=" * 60)
            return

        print(f"\nEncontrados {len(birthday_users)} cumpleaños hoy:")
        print("-" * 60)

        # Enviar correos de cumpleaños
        sent_count = 0
        failed_count = 0

        for user in birthday_users:
            # Calcular la edad si tenemos el año de nacimiento
            age = today.year - user.birthday.year if user.birthday else None
            age_str = f" ({age} años)" if age else ""

            print(f"\n>> Enviando correo a:")
            print(f"   Nombre: {user.name}{age_str}")
            print(f"   Email: {user.email}")

            try:
                success = email_service.send_birthday_email(
                    to_email=user.email,
                    user_name=user.name
                )

                if success:
                    print(f"   [OK] Correo enviado exitosamente")
                    sent_count += 1
                else:
                    print(f"   [ERROR] Error al enviar correo")
                    failed_count += 1

            except Exception as e:
                print(f"   [ERROR] Error: {str(e)}")
                failed_count += 1

        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN:")
        print(f"  Total de cumpleaños: {len(birthday_users)}")
        print(f"  Correos enviados: {sent_count}")
        print(f"  Errores: {failed_count}")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Error general: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    check_and_send_birthday_emails()
