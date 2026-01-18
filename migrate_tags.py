"""
Script de migración para agregar sistema de tags/etiquetas a usuarios
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

print("Iniciando migración de sistema de tags...")

# 1. Crear tabla de tags
print("\n1. Creando tabla 'tags'...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL UNIQUE,
        color VARCHAR DEFAULT '#3B82F6',
        description TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
print("  ✓ Tabla 'tags' creada")

# 2. Crear tabla de asociación user_tags
print("\n2. Creando tabla de asociación 'user_tags'...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_tags (
        user_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, tag_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id)
    )
""")
conn.commit()
print("  ✓ Tabla 'user_tags' creada")

# 3. Crear tags predeterminados
print("\n3. Creando tags predeterminados...")
tags_data = [
    ("IEEE Tadeo", "#3B82F6", "Usuarios de IEEE Tadeo Student Branch"),
    ("IEEE YP Co", "#10B981", "Usuarios de IEEE Young Professionals Colombia"),
]

for name, color, description in tags_data:
    try:
        cursor.execute(
            "INSERT INTO tags (name, color, description, is_active) VALUES (?, ?, ?, 1)",
            (name, color, description)
        )
        print(f"  ✓ Tag '{name}' creado")
    except sqlite3.IntegrityError:
        print(f"  - Tag '{name}' ya existe")

conn.commit()

# 4. Obtener ID del tag "IEEE Tadeo"
cursor.execute("SELECT id FROM tags WHERE name = 'IEEE Tadeo'")
ieee_tadeo_tag_id = cursor.fetchone()

if ieee_tadeo_tag_id:
    ieee_tadeo_tag_id = ieee_tadeo_tag_id[0]
    print(f"\n4. ID del tag 'IEEE Tadeo': {ieee_tadeo_tag_id}")

    # 5. Asignar tag "IEEE Tadeo" a todos los usuarios existentes
    print("\n5. Asignando tag 'IEEE Tadeo' a usuarios existentes...")

    # Obtener todos los usuarios
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()

    tagged_count = 0
    already_tagged = 0

    for (user_id,) in users:
        try:
            cursor.execute(
                "INSERT INTO user_tags (user_id, tag_id) VALUES (?, ?)",
                (user_id, ieee_tadeo_tag_id)
            )
            tagged_count += 1
        except sqlite3.IntegrityError:
            # El usuario ya tiene este tag
            already_tagged += 1

    conn.commit()
    print(f"  ✓ {tagged_count} usuarios etiquetados con 'IEEE Tadeo'")
    if already_tagged > 0:
        print(f"  - {already_tagged} usuarios ya tenían la etiqueta")

# 6. Resumen final
print("\n" + "="*60)
print("RESUMEN DE MIGRACIÓN")
print("="*60)

cursor.execute("SELECT COUNT(*) FROM tags WHERE is_active = 1")
print(f"Tags activos: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_tags")
print(f"Usuarios con tags: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT t.name, COUNT(ut.user_id) as user_count
    FROM tags t
    LEFT JOIN user_tags ut ON t.id = ut.tag_id
    GROUP BY t.id, t.name
    ORDER BY user_count DESC
""")
print("\nDistribución de tags:")
for tag_name, user_count in cursor.fetchall():
    print(f"  - {tag_name}: {user_count} usuarios")

print("\n✓ Migración completada exitosamente")
print("\nNOTAS:")
print("  - Todos los usuarios existentes tienen el tag 'IEEE Tadeo'")
print("  - Los nuevos usuarios pueden tener múltiples tags")
print("  - Al importar usuarios, se pueden asignar tags automáticamente")
print("  - Los usuarios duplicados mantendrán sus tags existentes y recibirán nuevos")

# Cerrar conexión
conn.close()
