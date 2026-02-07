"""
Migración para agregar columna 'status' a user_studies
y actualizar los tipos de estudio permitidos
"""
import sqlite3
import os

def migrate():
    db_path = "tickets.db"

    if not os.path.exists(db_path):
        print("Error: No se encontró la base de datos tickets.db")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la tabla user_studies existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_studies'")
        if not cursor.fetchone():
            print("Error: La tabla user_studies no existe. Ejecuta primero migrate_add_user_studies.py")
            return False

        # Verificar si la columna status ya existe
        cursor.execute("PRAGMA table_info(user_studies)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'status' in columns:
            print("La columna 'status' ya existe en user_studies")
        else:
            # Agregar columna status con valor por defecto 'cursando'
            print("Agregando columna 'status' a user_studies...")
            cursor.execute("""
                ALTER TABLE user_studies
                ADD COLUMN status VARCHAR(20) DEFAULT 'cursando'
            """)

            # Actualizar registros existentes
            cursor.execute("UPDATE user_studies SET status = 'cursando' WHERE status IS NULL")
            print("Columna 'status' agregada exitosamente")

        conn.commit()

        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM user_studies")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT status, COUNT(*) FROM user_studies GROUP BY status")
        status_counts = cursor.fetchall()

        print(f"\nEstadísticas de estudios ({total} total):")
        for status, count in status_counts:
            print(f"  - {status or 'sin status'}: {count}")

        return True

    except Exception as e:
        print(f"Error durante la migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Migración: Agregar status a user_studies ===\n")
    success = migrate()
    if success:
        print("\nMigración completada exitosamente")
    else:
        print("\nMigración fallida")
