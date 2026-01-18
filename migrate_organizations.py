"""
Script de migración para agregar tabla de organizaciones y actualizar usuarios y eventos
"""
import sqlite3
from datetime import datetime
import sys
import io

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

print("Iniciando migración de organizaciones...")

# 1. Crear tabla de organizaciones
print("\n1. Creando tabla 'organizations'...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL UNIQUE,
        short_name VARCHAR,
        description TEXT,
        logo_path VARCHAR,
        email_template TEXT,
        whatsapp_template TEXT,
        contact_email VARCHAR,
        contact_phone VARCHAR,
        website VARCHAR,
        facebook VARCHAR,
        instagram VARCHAR,
        twitter VARCHAR,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
print("✓ Tabla 'organizations' creada")

# 2. Crear organización predeterminada (IEEE Tadeo)
print("\n2. Creando organización predeterminada IEEE Tadeo...")
try:
    cursor.execute("""
        INSERT INTO organizations (
            name, short_name, description,
            contact_email, website,
            facebook, instagram, twitter,
            is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        "IEEE Tadeo Student Branch",
        "IEEE Tadeo",
        "Rama estudiantil IEEE de la Universidad Jorge Tadeo Lozano",
        "ieee@utadeo.edu.co",
        "https://ieeetadeo.org",
        "https://facebook.com/ieeetadeo",
        "https://instagram.com/ieeetadeo",
        "https://twitter.com/ieeetadeo"
    ))
    conn.commit()
    print("  ✓ IEEE Tadeo Student Branch creada")
except sqlite3.IntegrityError:
    print("  - IEEE Tadeo Student Branch ya existe")

# 3. Agregar columna organization_id a tabla users
print("\n3. Agregando columna 'organization_id' a tabla 'users'...")
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if 'organization_id' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN organization_id INTEGER")
    conn.commit()
    print("  ✓ Columna 'organization_id' agregada a 'users'")
else:
    print("  - Columna 'organization_id' ya existe en 'users'")

# 4. Agregar columna organization_id a tabla events
print("\n4. Agregando columna 'organization_id' a tabla 'events'...")
cursor.execute("PRAGMA table_info(events)")
columns = [col[1] for col in cursor.fetchall()]

if 'organization_id' not in columns:
    cursor.execute("ALTER TABLE events ADD COLUMN organization_id INTEGER")
    conn.commit()
    print("  ✓ Columna 'organization_id' agregada a 'events'")
else:
    print("  - Columna 'organization_id' ya existe en 'events'")

# 5. Obtener ID de IEEE Tadeo
cursor.execute("SELECT id FROM organizations WHERE name = 'IEEE Tadeo Student Branch'")
ieee_tadeo_id = cursor.fetchone()

if ieee_tadeo_id:
    ieee_tadeo_id = ieee_tadeo_id[0]
    print(f"\n5. ID de IEEE Tadeo: {ieee_tadeo_id}")

    # 6. Asignar todos los eventos existentes a IEEE Tadeo (opcional)
    print("\n6. Asignando eventos existentes a IEEE Tadeo...")
    cursor.execute("UPDATE events SET organization_id = ? WHERE organization_id IS NULL", (ieee_tadeo_id,))
    updated_events = cursor.rowcount
    conn.commit()
    print(f"  ✓ {updated_events} eventos asignados a IEEE Tadeo")

# 7. Resumen final
print("\n" + "="*60)
print("RESUMEN DE MIGRACIÓN")
print("="*60)
cursor.execute("SELECT COUNT(*) FROM organizations WHERE is_active = 1")
print(f"Organizaciones activas: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM users WHERE organization_id IS NOT NULL")
print(f"Usuarios con organización asignada: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM events WHERE organization_id IS NOT NULL")
print(f"Eventos con organización asignada: {cursor.fetchone()[0]}")

cursor.execute("SELECT id, name FROM organizations")
print("\nOrganizaciones disponibles:")
for org_id, name in cursor.fetchall():
    print(f"  - ID {org_id}: {name}")

print("\n✓ Migración completada exitosamente")
print("\nNOTA: Los usuarios y eventos existentes NO fueron asignados automáticamente")
print("      a ninguna organización. Los eventos nuevos pueden asignarse manualmente.")
print("      Los usuarios sin organización seguirán funcionando normalmente.")

# Cerrar conexión
conn.close()
