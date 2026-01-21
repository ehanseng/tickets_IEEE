"""
Script de migracion para:
1. Agregar campo event_type a la tabla events
2. Crear tabla event_gallery_images

Ejecutar: python migrate_event_gallery.py
"""
import sqlite3
import os

# Crear directorio para galeria si no existe
os.makedirs('static/event_gallery', exist_ok=True)
print("[OK] Directorio static/event_gallery creado/verificado")

conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

try:
    # 1. Agregar campo event_type a events
    cursor.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'event_type' not in columns:
        print("Agregando columna event_type a la tabla events...")
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN event_type VARCHAR(20) DEFAULT 'organized'
        """)
        print("[OK] Columna event_type agregada")
    else:
        print("[OK] La columna event_type ya existe")

    # 2. Crear tabla event_gallery_images
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_gallery_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            image_path VARCHAR(500) NOT NULL,
            caption VARCHAR(300),
            display_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    """)
    print("[OK] Tabla event_gallery_images creada/verificada")

    # 3. Crear indice para event_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_event_gallery_images_event_id
        ON event_gallery_images(event_id)
    """)
    print("[OK] Indice creado/verificado")

    conn.commit()
    print("\n========================================")
    print("Migracion completada exitosamente!")
    print("========================================")

except sqlite3.Error as e:
    print(f"[ERROR] Error durante la migracion: {e}")
    conn.rollback()
finally:
    conn.close()
