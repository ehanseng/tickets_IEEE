"""
Script de migración para agregar tabla de universidades y actualizar usuarios
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

print("Iniciando migración de universidades...")

# 1. Crear tabla de universidades
print("\n1. Creando tabla 'universities'...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL UNIQUE,
        short_name VARCHAR,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
print("✓ Tabla 'universities' creada")

# 2. Poblar con universidades iniciales de Colombia
print("\n2. Poblando universidades iniciales...")
universities = [
    ("Universidad Jorge Tadeo Lozano", "Tadeo"),
    ("Universidad Nacional de Colombia", "UNAL"),
    ("Universidad de los Andes", "Uniandes"),
    ("Pontificia Universidad Javeriana", "Javeriana"),
    ("Universidad de La Salle", "La Salle"),
    ("Universidad del Rosario", "Rosario"),
    ("Universidad Externado de Colombia", "Externado"),
    ("Universidad Sergio Arboleda", "Sergio Arboleda"),
    ("Universidad EAN", "EAN"),
    ("Universidad El Bosque", "El Bosque"),
    ("Universidad Piloto de Colombia", "Piloto"),
    ("Universidad Antonio Nariño", "UAN"),
    ("Universidad Distrital Francisco José de Caldas", "Distrital"),
    ("Universidad Pedagógica Nacional", "Pedagógica"),
    ("Universidad Militar Nueva Granada", "Militar"),
    ("Universidad Santo Tomás", "Santo Tomás"),
    ("Universidad Central", "Central"),
    ("Universidad Libre", "Libre"),
    ("Universidad Católica de Colombia", "Católica"),
    ("Universidad ECCI", "ECCI"),
    ("Universidad Autónoma de Colombia", "Autónoma"),
    ("Universidad Minuto de Dios", "Uniminuto"),
    ("Universidad Manuela Beltrán", "UMB"),
    ("Universidad Incca de Colombia", "Incca"),
    ("Universidad Cooperativa de Colombia", "Cooperativa"),
    ("Fundación Universidad de América", "América"),
    ("Escuela Colombiana de Ingeniería Julio Garavito", "Escuela"),
    ("Otra Universidad", None),
]

for name, short_name in universities:
    try:
        cursor.execute(
            "INSERT INTO universities (name, short_name, is_active) VALUES (?, ?, 1)",
            (name, short_name)
        )
        print(f"  ✓ {name}")
    except sqlite3.IntegrityError:
        print(f"  - {name} (ya existe)")

conn.commit()
print(f"\n✓ {len(universities)} universidades procesadas")

# 3. Obtener universidades existentes en tabla users (texto)
print("\n3. Obteniendo universidades existentes en users...")
cursor.execute("SELECT DISTINCT university FROM users WHERE university IS NOT NULL AND university != ''")
existing_universities = cursor.fetchall()
print(f"Encontradas {len(existing_universities)} universidades únicas en users")

# Crear un mapeo de universidades
university_mapping = {}
cursor.execute("SELECT id, name, short_name FROM universities")
for row in cursor.fetchall():
    uni_id, name, short_name = row
    university_mapping[name.lower()] = uni_id
    if short_name:
        university_mapping[short_name.lower()] = uni_id

# 4. Agregar nuevas columnas a users
print("\n4. Agregando nuevas columnas a tabla 'users'...")

# Verificar si las columnas ya existen
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if 'university_id' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN university_id INTEGER")
    print("  ✓ Columna 'university_id' agregada")
else:
    print("  - Columna 'university_id' ya existe")

if 'is_ieee_member' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN is_ieee_member BOOLEAN DEFAULT 0")
    print("  ✓ Columna 'is_ieee_member' agregada")
else:
    print("  - Columna 'is_ieee_member' ya existe")

conn.commit()

# 5. Migrar datos existentes
print("\n5. Migrando datos de universidad (texto) a university_id...")
cursor.execute("SELECT id, university FROM users WHERE university IS NOT NULL AND university != ''")
users_with_uni = cursor.fetchall()

migrated = 0
not_migrated = 0

for user_id, uni_text in users_with_uni:
    # Buscar coincidencia en el mapeo
    uni_text_lower = uni_text.lower().strip()

    matched_id = None
    # Intento 1: Coincidencia exacta
    if uni_text_lower in university_mapping:
        matched_id = university_mapping[uni_text_lower]
    else:
        # Intento 2: Coincidencia parcial
        for key, value in university_mapping.items():
            if key in uni_text_lower or uni_text_lower in key:
                matched_id = value
                break

    if matched_id:
        cursor.execute("UPDATE users SET university_id = ? WHERE id = ?", (matched_id, user_id))
        migrated += 1
        print(f"  ✓ Usuario {user_id}: '{uni_text}' → ID {matched_id}")
    else:
        # Si no hay coincidencia, asignar a "Otra Universidad"
        other_id = university_mapping.get("otra universidad")
        if other_id:
            cursor.execute("UPDATE users SET university_id = ? WHERE id = ?", (other_id, user_id))
            migrated += 1
            print(f"  ⚠ Usuario {user_id}: '{uni_text}' → 'Otra Universidad' (ID {other_id})")
        else:
            not_migrated += 1
            print(f"  ✗ Usuario {user_id}: '{uni_text}' no pudo migrarse")

conn.commit()
print(f"\n✓ Migración completada: {migrated} usuarios migrados, {not_migrated} sin migrar")

# 6. Resumen final
print("\n" + "="*60)
print("RESUMEN DE MIGRACIÓN")
print("="*60)
cursor.execute("SELECT COUNT(*) FROM universities WHERE is_active = 1")
print(f"Universidades activas: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM users WHERE university_id IS NOT NULL")
print(f"Usuarios con universidad asignada: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM users WHERE is_ieee_member = 1")
print(f"Usuarios miembros IEEE: {cursor.fetchone()[0]}")

print("\n✓ Migración completada exitosamente")

# Cerrar conexión
conn.close()
