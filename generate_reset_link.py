"""
Script para generar un enlace de recuperación de contraseña manualmente
"""
import sqlite3
import secrets
from datetime import datetime, timedelta
import sys
import io

# Configurar salida UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_reset_link(email: str):
    """Genera un enlace de recuperación para un usuario"""

    # Conectar a la base de datos
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Buscar usuario
    cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if not result:
        print(f"❌ Usuario no encontrado: {email}")
        conn.close()
        return

    user_id, name = result

    # Generar token
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)

    # Guardar token en la base de datos
    cursor.execute(
        "UPDATE users SET password_reset_token = ?, password_reset_expires = ? WHERE id = ?",
        (token, expires, user_id)
    )
    conn.commit()
    conn.close()

    # Generar enlaces
    local_link = f"http://127.0.0.1:8000/portal/reset-password?token={token}"
    prod_link = f"https://ticket.ieeetadeo.org/portal/reset-password?token={token}"

    print(f"\n✅ Enlace de recuperación generado para: {name} ({email})")
    print(f"\n🔗 Enlace local:")
    print(f"   {local_link}")
    print(f"\n🔗 Enlace producción:")
    print(f"   {prod_link}")
    print(f"\n⏰ El enlace expira en 1 hora")
    print(f"\n📋 Token: {token}\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python generate_reset_link.py <email>")
        print("Ejemplo: python generate_reset_link.py usuario@example.com")
        sys.exit(1)

    email = sys.argv[1]
    generate_reset_link(email)
