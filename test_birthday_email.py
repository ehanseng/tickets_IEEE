"""
Script para enviar un correo de cumpleaños de prueba

Uso:
    python test_birthday_email.py email@ejemplo.com
    python test_birthday_email.py  # Envía a todos los usuarios con cumpleaños configurado
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import SessionLocal
import models
from email_service import email_service


def send_test_birthday_email(email: str = None):
    """
    Envía un correo de cumpleaños de prueba

    Args:
        email: Email del usuario (opcional). Si no se proporciona, muestra lista de usuarios.
    """
    db: Session = SessionLocal()

    try:
        print("=" * 60)
        print("ENVÍO DE CORREO DE CUMPLEAÑOS DE PRUEBA")
        print("=" * 60)

        if not email:
            # Mostrar usuarios con cumpleaños configurado
            users = db.query(models.User).filter(
                models.User.birthday.isnot(None)
            ).all()

            if not users:
                print("\n[ERROR] No hay usuarios con cumpleaños configurado en la base de datos.")
                print("\nPara agregar un cumpleaños:")
                print("1. Ingresa al portal: https://ticket.ieeetadeo.org/portal/login")
                print("2. Ve a 'Mi Perfil'")
                print("3. Ingresa la fecha de nacimiento")
                return

            print("\nUsuarios con cumpleaños configurado:")
            print("-" * 60)
            for user in users:
                print(f"  {user.name}")
                print(f"  Email: {user.email}")
                print(f"  Cumpleaños: {user.birthday.strftime('%d/%m/%Y')}")
                print("-" * 60)

            print("\nPara enviar un correo de prueba, ejecuta:")
            print(f"  uv run python test_birthday_email.py {users[0].email}")
            return

        # Buscar usuario por email
        user = db.query(models.User).filter(
            models.User.email == email
        ).first()

        if not user:
            print(f"\n[ERROR] No se encontró un usuario con el email: {email}")
            return

        if not user.birthday:
            print(f"\n[ERROR] El usuario {user.name} no tiene cumpleaños configurado.")
            print("\nPara agregar un cumpleaños:")
            print("1. Ingresa al portal: https://ticket.ieeetadeo.org/portal/login")
            print("2. Ve a 'Mi Perfil'")
            print("3. Ingresa la fecha de nacimiento")
            return

        print(f"\n>> Enviando correo de prueba a:")
        print(f"   Nombre: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Cumpleaños: {user.birthday.strftime('%d/%m/%Y')}")
        print("\n>> Enviando...")

        # Enviar correo
        success = email_service.send_birthday_email(
            to_email=user.email,
            user_name=user.name
        )

        print("\n" + "=" * 60)
        if success:
            print("[OK] CORREO ENVIADO EXITOSAMENTE")
            print("=" * 60)
            print(f"\n>> Revisa la bandeja de entrada de: {user.email}")
            print("   Si no lo ves, revisa también la carpeta de SPAM/Correo no deseado")
        else:
            print("[ERROR] ERROR AL ENVIAR EL CORREO")
            print("=" * 60)
            print("\nPosibles causas:")
            print("1. SMTP no configurado correctamente en el archivo .env")
            print("2. Credenciales incorrectas")
            print("3. Problemas de conexión")
            print("\nRevisa el archivo .env y verifica:")
            print("  SMTP_HOST=smtp.gmail.com")
            print("  SMTP_PORT=587")
            print("  SMTP_USER=tu-email@gmail.com")
            print("  SMTP_PASSWORD=tu-contraseña-de-aplicación")

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        send_test_birthday_email(email)
    else:
        send_test_birthday_email()
