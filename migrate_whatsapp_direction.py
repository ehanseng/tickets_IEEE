"""
Migración: Agregar campos direction y to_number a whatsapp_messages
Para distinguir mensajes enviados de recibidos
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
        # Verificar si la columna direction ya existe
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_schema = :db
            AND table_name = 'whatsapp_messages'
            AND column_name = 'direction'
        """), {"db": MYSQL_DATABASE})

        row = result.fetchone()
        if row[0] == 0:
            print("Agregando columna 'direction'...")
            conn.execute(text("""
                ALTER TABLE whatsapp_messages
                ADD COLUMN direction VARCHAR(10) DEFAULT 'incoming'
            """))
            conn.commit()
            print("Columna 'direction' agregada exitosamente")
        else:
            print("Columna 'direction' ya existe")

        # Verificar si la columna to_number ya existe
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_schema = :db
            AND table_name = 'whatsapp_messages'
            AND column_name = 'to_number'
        """), {"db": MYSQL_DATABASE})

        row = result.fetchone()
        if row[0] == 0:
            print("Agregando columna 'to_number'...")
            conn.execute(text("""
                ALTER TABLE whatsapp_messages
                ADD COLUMN to_number VARCHAR(50) NULL
            """))
            conn.commit()
            print("Columna 'to_number' agregada exitosamente")
        else:
            print("Columna 'to_number' ya existe")

        print("Migración completada!")

if __name__ == "__main__":
    migrate()
