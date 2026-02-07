"""
Migración: Agregar campo is_professor a users
Para identificar si un usuario es profesor/docente
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ieeetadeo")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

def migrate():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Verificar si la columna is_professor ya existe
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_schema = :db
            AND table_name = 'users'
            AND column_name = 'is_professor'
        """), {"db": MYSQL_DATABASE})

        row = result.fetchone()
        if row[0] == 0:
            print("Agregando columna 'is_professor'...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN is_professor BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            print("Columna 'is_professor' agregada exitosamente")
        else:
            print("Columna 'is_professor' ya existe")

        print("Migración completada!")

if __name__ == "__main__":
    migrate()
