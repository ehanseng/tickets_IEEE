"""
Script de migración para agregar campos de contraseña y recuperación a usuarios
"""
import sqlite3
import sys
import io
import hashlib

# Configurar la salida para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def hash_password(password: str) -> str:
    """Hash password usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

print("🔄 Iniciando migración de campos de contraseña...")

# 1. Agregar columnas de contraseña
print("\n📝 Agregando columnas de contraseña y recuperación...")
columnas = [
    "hashed_password TEXT",
    "password_reset_token TEXT",
    "password_reset_expires TIMESTAMP"
]

for columna in columnas:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {columna}")
        print(f"   ✓ Agregada columna: {columna.split()[0]}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"   ℹ Columna ya existe: {columna.split()[0]}")
        else:
            raise e

conn.commit()

# 2. Generar contraseñas temporales para usuarios existentes
print("\n🔐 Generando contraseñas temporales para usuarios existentes...")
cursor.execute("SELECT id, email, hashed_password FROM users")
users = cursor.fetchall()

for user_id, email, current_password in users:
    if not current_password:
        # Generar contraseña temporal basada en los primeros 8 caracteres del email
        temp_password = email.split('@')[0][:8] + "123"
        hashed = hash_password(temp_password)

        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed, user_id)
        )
        print(f"   ✓ Usuario {email}: contraseña temporal = {temp_password}")

conn.commit()

print("\n✅ Migración completada exitosamente!")
print("\n📌 IMPORTANTE: Los usuarios existentes tienen contraseñas temporales.")
print("   Formato: primeros 8 caracteres del email + '123'")
print("   Ejemplo: usuario@example.com → usuario123")

# Cerrar conexión
conn.close()
