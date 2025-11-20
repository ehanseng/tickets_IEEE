"""
Script para agregar campos de templates personalizados a la tabla events
"""
import sqlite3
import sys
import io

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

try:
    # Agregar columna whatsapp_template
    try:
        cursor.execute('''
            ALTER TABLE events
            ADD COLUMN whatsapp_template TEXT
        ''')
        print("✓ Columna 'whatsapp_template' agregada a la tabla events")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("• Columna 'whatsapp_template' ya existe")
        else:
            raise

    # Agregar columna email_template
    try:
        cursor.execute('''
            ALTER TABLE events
            ADD COLUMN email_template TEXT
        ''')
        print("✓ Columna 'email_template' agregada a la tabla events")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("• Columna 'email_template' ya existe")
        else:
            raise

    conn.commit()
    print("\n✓ Migración completada exitosamente")
    print("\nAhora puedes configurar templates personalizados para cada evento.")
    print("Variables disponibles para los templates:")
    print("  - {user_name}")
    print("  - {event_name}")
    print("  - {event_date}")
    print("  - {event_location}")
    print("  - {ticket_code}")
    print("  - {ticket_url}")
    print("  - {access_pin}")
    print("  - {companions} (para email)")
    print("  - {companions_text} (para WhatsApp)")
    print("  - {companions_info} (para email)")

except Exception as e:
    print(f"✗ Error durante la migración: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
