"""
Script de migración: Agregar campo 'nick' a la tabla users
"""
import sqlite3

def migrate():
    """Agregar campo nick a la tabla users"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'nick' in columns:
            print("[OK] La columna 'nick' ya existe en la tabla users")
            return

        # Agregar la columna nick
        cursor.execute("ALTER TABLE users ADD COLUMN nick TEXT")
        conn.commit()
        print("[OK] Columna 'nick' agregada exitosamente a la tabla users")

    except sqlite3.Error as e:
        print(f"[ERROR] Error durante la migracion: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando migración: Agregar campo 'nick' a users...")
    migrate()
    print("Migración completada.")
