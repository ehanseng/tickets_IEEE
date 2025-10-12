"""
Migración: Agregar campo country_code a la tabla users
"""
import sqlite3
import re

def parse_existing_phone(phone: str):
    """
    Intenta extraer el código de país de un número existente
    """
    if not phone:
        return "+57", phone

    # Limpiar el teléfono
    phone = phone.strip()

    # Si empieza con +, intentar extraer el código
    if phone.startswith("+"):
        # Buscar códigos de país comunes
        if phone.startswith("+57"):
            return "+57", phone[3:].strip()
        elif phone.startswith("+1"):
            return "+1", phone[2:].strip()
        elif phone.startswith("+52"):
            return "+52", phone[3:].strip()
        elif phone.startswith("+54"):
            return "+54", phone[3:].strip()
        elif phone.startswith("+55"):
            return "+55", phone[3:].strip()
        elif phone.startswith("+56"):
            return "+56", phone[3:].strip()
        elif phone.startswith("+593"):
            return "+593", phone[4:].strip()
        elif phone.startswith("+591"):
            return "+591", phone[4:].strip()

    # Si no tiene +, asumir que es Colombia
    return "+57", phone

def migrate():
    """Ejecuta la migración"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'country_code' in columns:
        print("[INFO] La columna 'country_code' ya existe en la tabla users")
        conn.close()
        return

    print("[INFO] Agregando columna 'country_code' a la tabla users...")

    # Agregar la columna
    cursor.execute("""
        ALTER TABLE users ADD COLUMN country_code TEXT DEFAULT '+57'
    """)

    print("[OK] Columna 'country_code' agregada exitosamente")

    # Actualizar códigos de país basados en números existentes
    print("[INFO] Analizando números telefónicos existentes...")
    cursor.execute("SELECT id, phone FROM users WHERE phone IS NOT NULL AND phone != ''")
    users = cursor.fetchall()

    updated_count = 0
    for user_id, phone in users:
        country_code, new_phone = parse_existing_phone(phone)

        # Actualizar el registro
        cursor.execute("""
            UPDATE users
            SET country_code = ?, phone = ?
            WHERE id = ?
        """, (country_code, new_phone, user_id))
        updated_count += 1
        print(f"  Usuario {user_id}: {phone} -> {country_code} + {new_phone}")

    conn.commit()
    conn.close()

    print(f"[OK] Migración completada. {updated_count} números actualizados.")

if __name__ == "__main__":
    migrate()
