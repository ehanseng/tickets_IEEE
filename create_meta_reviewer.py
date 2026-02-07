"""
Script para crear el usuario revisor de Meta con permisos muy limitados.
Este usuario solo puede ver la estructura del sistema, NO datos de usuarios reales.
"""
import sqlite3
import hashlib
import os

def hash_password(password: str) -> str:
    """Hash para contraseña (mismo método que usa el sistema con salt)"""
    salt = "ieee-tadeo-salt-2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_meta_reviewer():
    db_path = "tickets.db"

    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    username = "revisor_meta"
    email = "meta-reviewer@ieeetadeo.org"
    full_name = "Meta App Reviewer"
    password = "MetaReview2025!"
    password_hash = hash_password(password)

    # Verificar si ya existe
    cursor.execute("SELECT id FROM admin_users WHERE username = ?", (username,))
    existing = cursor.fetchone()

    if existing:
        print(f"El usuario '{username}' ya existe. Actualizando...")
        cursor.execute("""
            UPDATE admin_users
            SET hashed_password = ?, role = ?, is_active = 1
            WHERE username = ?
        """, (password_hash, "meta_reviewer", username))
    else:
        print(f"Creando usuario '{username}'...")
        cursor.execute("""
            INSERT INTO admin_users (username, email, full_name, hashed_password, role, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (username, email, full_name, password_hash, "meta_reviewer"))

    conn.commit()
    conn.close()

    print(f"\n{'='*50}")
    print("Usuario creado/actualizado exitosamente:")
    print(f"{'='*50}")
    print(f"  Usuario: {username}")
    print(f"  Contraseña: {password}")
    print(f"  Rol: meta_reviewer")
    print(f"\nEste usuario tiene acceso MUY LIMITADO:")
    print("  - Ver lista de eventos (sin datos de asistentes)")
    print("  - Ver templates de WhatsApp")
    print("  - Ver estadísticas agregadas")
    print("  - NO puede ver datos de usuarios (nombre, email, teléfono)")
    print("  - NO puede enviar mensajes por WhatsApp ni Email")
    print("  - NO puede modificar nada")
    print(f"{'='*50}")

    return True

if __name__ == "__main__":
    create_meta_reviewer()
