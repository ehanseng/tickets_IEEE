"""
Script de migración para agregar campo TikTok a universidades
"""
import sqlite3
import sys
import io

# Configurar la salida para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a la base de datos
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

print("🔄 Iniciando migración para agregar TikTok...")

# Agregar columna ieee_tiktok
try:
    cursor.execute("ALTER TABLE universities ADD COLUMN ieee_tiktok TEXT")
    print("   ✓ Agregada columna: ieee_tiktok")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("   ℹ Columna ieee_tiktok ya existe")
    else:
        raise e

conn.commit()

print("\n✅ Migración completada exitosamente!")

# Cerrar conexión
conn.close()
