"""
Script para agregar campos 'identification' y 'university' a usuarios existentes
Ejecutar solo una vez después de actualizar el modelo
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    try:
        # Agregar columna identification
        cursor.execute("ALTER TABLE users ADD COLUMN identification TEXT")
        print("OK - Columna 'identification' agregada exitosamente")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("OK - La columna 'identification' ya existe")
        else:
            print(f"Error en identification: {e}")

    try:
        # Agregar columna university
        cursor.execute("ALTER TABLE users ADD COLUMN university TEXT")
        print("OK - Columna 'university' agregada exitosamente")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("OK - La columna 'university' ya existe")
        else:
            print(f"Error en university: {e}")

    conn.commit()
    conn.close()
    print("\nMigracion completada!")

if __name__ == "__main__":
    migrate()
