"""
Script de migración para agregar columna whatsapp_image_path a la tabla events
"""
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

try:
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'whatsapp_image_path' not in columns:
        print("Agregando columna whatsapp_image_path a la tabla events...")
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN whatsapp_image_path VARCHAR
        """)
        conn.commit()
        print("✓ Columna whatsapp_image_path agregada exitosamente")
    else:
        print("✓ La columna whatsapp_image_path ya existe en la tabla events")

except sqlite3.Error as e:
    print(f"Error durante la migración: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n¡Migración completada!")
