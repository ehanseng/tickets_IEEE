"""
Migración: Agregar campo birthday a la tabla users

Este script agrega el campo birthday (fecha de cumpleaños) a la tabla users.
"""
import sqlite3
from pathlib import Path

def migrate():
    """Ejecuta la migración"""
    db_path = Path("tickets.db")

    if not db_path.exists():
        print("❌ Error: No se encontró la base de datos tickets.db")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'birthday' in columns:
            print("✓ La columna 'birthday' ya existe en la tabla users")
            return

        # Agregar la columna birthday
        print("Agregando columna 'birthday' a la tabla users...")
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN birthday DATETIME
        """)

        conn.commit()
        print("✓ Migración completada exitosamente")
        print("  - Columna 'birthday' agregada a la tabla users")

    except sqlite3.Error as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Migración: Agregar campo birthday a users")
    print("=" * 60)
    migrate()
    print("=" * 60)
