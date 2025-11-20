"""
Script de migración para agregar columna send_qr_with_whatsapp a la tabla events
"""
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

try:
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'send_qr_with_whatsapp' not in columns:
        print("Agregando columna send_qr_with_whatsapp a la tabla events...")
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN send_qr_with_whatsapp BOOLEAN DEFAULT 0
        """)
        conn.commit()
        print("Columna send_qr_with_whatsapp agregada exitosamente")
    else:
        print("La columna send_qr_with_whatsapp ya existe en la tabla events")

except sqlite3.Error as e:
    print(f"Error durante la migracion: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nMigracion completada!")
