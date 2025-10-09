"""
Script para agregar la columna 'companions' a tickets existentes
Ejecutar solo una vez después de actualizar el modelo
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    try:
        # Intentar agregar la columna companions
        cursor.execute("ALTER TABLE tickets ADD COLUMN companions INTEGER DEFAULT 0")
        conn.commit()
        print("OK - Columna 'companions' agregada exitosamente")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("OK - La columna 'companions' ya existe")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
