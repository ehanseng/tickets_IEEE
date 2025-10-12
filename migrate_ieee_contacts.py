"""
Script de migración para agregar campos de contacto IEEE a universidades
"""
import sqlite3
import sys
import io

# Configurar la salida para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

print("🔄 Iniciando migración de campos de contacto IEEE...")

# 1. Agregar columnas de contacto IEEE
print("\n📝 Agregando columnas de contacto IEEE...")
columnas = [
    "ieee_contact_email TEXT",
    "ieee_facebook TEXT",
    "ieee_instagram TEXT",
    "ieee_twitter TEXT",
    "ieee_website TEXT"
]

for columna in columnas:
    try:
        cursor.execute(f"ALTER TABLE universities ADD COLUMN {columna}")
        print(f"   ✓ Agregada columna: {columna.split()[0]}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"   ℹ Columna ya existe: {columna.split()[0]}")
        else:
            raise e

conn.commit()

# 2. Actualizar universidades con información de ramas IEEE
print("\n📚 Actualizando información de universidades con ramas IEEE...")

universidades_ieee = [
    {
        'name': 'Universidad Jorge Tadeo Lozano',
        'has_ieee_branch': 1,
        'ieee_contact_email': 'ocho.elaee@utadeo.edu.co',
        'ieee_website': 'https://www.utadeo.edu.co/es/comunidad/ingenieria-de-sistemas/83/la-rama-estudiantil-ieee-utadeo'
    },
    {
        'name': 'Universidad Nacional de Colombia',
        'has_ieee_branch': 1,
        'ieee_website': 'https://edu.ieee.org/co-unemb/',
        'ieee_instagram': 'ieeeunal'
    },
    {
        'name': 'Pontificia Universidad Javeriana',
        'has_ieee_branch': 1,
        'ieee_website': 'https://edu.ieee.org/co-javeriana/',
        'ieee_facebook': 'ieeejaveriana',
        'ieee_twitter': 'IEEEPUJ',
        'ieee_instagram': 'ieeepujoficial'
    },
    {
        'name': 'Universidad de los Andes',
        'has_ieee_branch': 1,
        'ieee_website': 'https://ias.uniandes.edu.co/'
    },
    {
        'name': 'Universidad Distrital Francisco José de Caldas',
        'has_ieee_branch': 1,
        'ieee_contact_email': 'pesud@udistrital.edu.co',
        'ieee_website': 'http://ieee.udistrital.edu.co/'
    }
]

for uni in universidades_ieee:
    # Actualizar la universidad
    update_query = """
        UPDATE universities
        SET has_ieee_branch = ?,
            ieee_contact_email = ?,
            ieee_facebook = ?,
            ieee_instagram = ?,
            ieee_twitter = ?,
            ieee_website = ?
        WHERE name = ?
    """

    cursor.execute(update_query, (
        uni.get('has_ieee_branch', 0),
        uni.get('ieee_contact_email'),
        uni.get('ieee_facebook'),
        uni.get('ieee_instagram'),
        uni.get('ieee_twitter'),
        uni.get('ieee_website'),
        uni['name']
    ))

    if cursor.rowcount > 0:
        print(f"   ✓ {uni['name']}")
    else:
        print(f"   ✗ No se encontró: {uni['name']}")

conn.commit()

# 3. Mostrar resumen
print("\n📊 Resumen de universidades con rama IEEE:")
cursor.execute("""
    SELECT name, short_name, ieee_contact_email, ieee_website
    FROM universities
    WHERE has_ieee_branch = 1
    ORDER BY name
""")

for row in cursor.fetchall():
    name, short_name, email, website = row
    print(f"\n   🏛️ {name} ({short_name or 'N/A'})")
    if email:
        print(f"      📧 {email}")
    if website:
        print(f"      🌐 {website}")

print("\n✅ Migración completada exitosamente!")

# Cerrar conexión
conn.close()
