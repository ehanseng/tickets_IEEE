"""
Migracion para agregar campo description a academic_programs
"""
import sqlite3
import os

def migrate():
    db_path = "tickets.db"

    if not os.path.exists(db_path):
        print("Error: No se encontro la base de datos tickets.db")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(academic_programs)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'description' in columns:
            print("[INFO] La columna 'description' ya existe en academic_programs")
            return True

        # Agregar la columna description
        cursor.execute("""
            ALTER TABLE academic_programs
            ADD COLUMN description VARCHAR(500)
        """)
        print("[OK] Columna 'description' agregada a academic_programs")

        conn.commit()
        print("\n========================================")
        print("Migracion completada exitosamente!")
        print("========================================")
        return True

    except Exception as e:
        print(f"Error durante la migracion: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Migracion: Agregar description a academic_programs ===\n")
    success = migrate()
    if success:
        print("\nMigracion completada")
    else:
        print("\nMigracion fallida")
