"""
Migracion para crear tabla de empresas aliadas
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
        # 1. Crear tabla allied_companies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allied_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                alliance_type VARCHAR(200) NOT NULL,
                logo_path VARCHAR(500),
                website VARCHAR(500),
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Tabla allied_companies creada/verificada")

        # 2. Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM allied_companies")
        count = cursor.fetchone()[0]

        if count == 0:
            # 3. Insertar datos iniciales
            initial_companies = [
                ("Elaborando Futuro", "Aliado tecnologico", None, None, None, 1, 1),
                ("Lesiga", "Apoyo ante emergencias", None, None, None, 1, 2),
            ]

            cursor.executemany("""
                INSERT INTO allied_companies (name, alliance_type, logo_path, website, description, is_active, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, initial_companies)
            print(f"[OK] {len(initial_companies)} empresas aliadas iniciales agregadas")
        else:
            print(f"[INFO] Ya existen {count} empresas aliadas, no se agregan datos iniciales")

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
    print("=== Migracion: Crear tabla empresas aliadas ===\n")
    success = migrate()
    if success:
        print("\nMigracion completada")
    else:
        print("\nMigracion fallida")
