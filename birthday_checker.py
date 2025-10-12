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
from whatsapp_client import send_birthday_whatsapp, WhatsAppClient


def check_and_send_birthday_emails():
    """
    Verifica los cumpleaños del día actual y envía correos y WhatsApp de felicitación
    """
    db: Session = SessionLocal()

    # Verificar si WhatsApp está disponible
    whatsapp_client = WhatsAppClient()
    whatsapp_available = whatsapp_client.is_ready()

    try:
        # Obtener la fecha de hoy (solo mes y día, ignorar año)
        today = datetime.now()
        today_month = today.month
        today_day = today.day

        print(f"=== Verificador de Cumpleaños - {today.strftime('%Y-%m-%d')} ===")
        print(f"WhatsApp: {'✓ Disponible' if whatsapp_available else '✗ No disponible'}")
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

        # Enviar correos y WhatsApp de cumpleaños
        email_sent_count = 0
        email_failed_count = 0
        whatsapp_sent_count = 0
        whatsapp_failed_count = 0

        for user in birthday_users:
            # Calcular la edad si tenemos el año de nacimiento
            age = today.year - user.birthday.year if user.birthday else None
            age_str = f" ({age} años)" if age else ""

            print(f"\n>> Enviando felicitaciones a:")
            print(f"   Nombre: {user.name}{age_str}")
            print(f"   Email: {user.email}")
            if user.phone and user.country_code:
                print(f"   WhatsApp: {user.country_code}{user.phone}")

            # 1. Enviar correo
            try:
                success = email_service.send_birthday_email(
                    to_email=user.email,
                    user_name=user.name
                )

                if success:
                    print(f"   [OK] Correo enviado exitosamente")
                    email_sent_count += 1
                else:
                    print(f"   [ERROR] Error al enviar correo")
                    email_failed_count += 1

            except Exception as e:
                print(f"   [ERROR] Error en correo: {str(e)}")
                email_failed_count += 1

            # 2. Enviar WhatsApp (solo si está disponible y el usuario tiene teléfono)
            if whatsapp_available and user.phone and user.country_code:
                try:
                    success = send_birthday_whatsapp(
                        phone=user.phone,
                        country_code=user.country_code,
                        user_name=user.name
                    )

                    if success:
                        whatsapp_sent_count += 1
                    else:
                        whatsapp_failed_count += 1

                except Exception as e:
                    print(f"   [ERROR] Error en WhatsApp: {str(e)}")
                    whatsapp_failed_count += 1
            elif not user.phone or not user.country_code:
                print(f"   [SKIP] Usuario sin número de teléfono")
            elif not whatsapp_available:
                print(f"   [SKIP] WhatsApp no disponible")

        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN:")
        print(f"  Total de cumpleaños: {len(birthday_users)}")
        print(f"\n  CORREOS:")
        print(f"    Enviados: {email_sent_count}")
        print(f"    Errores: {email_failed_count}")
        print(f"\n  WHATSAPP:")
        print(f"    Enviados: {whatsapp_sent_count}")
        print(f"    Errores: {whatsapp_failed_count}")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Error general: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    check_and_send_birthday_emails()
