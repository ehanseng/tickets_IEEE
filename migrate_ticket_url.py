"""
Script para agregar campos de URL única y PIN a tickets existentes
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL
import secrets
import string

def generate_unique_url():
    """Genera una URL única usando tokens seguros"""
    return secrets.token_urlsafe(32)

def generate_pin():
    """Genera un PIN de 6 dígitos"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # Agregar columnas si no existen
        try:
            conn.execute(text("ALTER TABLE tickets ADD COLUMN unique_url TEXT"))
            conn.execute(text("ALTER TABLE tickets ADD COLUMN access_pin TEXT"))
            print("OK - Columnas agregadas exitosamente")
        except Exception as e:
            print(f"Columnas ya existen o error: {e}")

        # Crear índices únicos
        try:
            conn.execute(text("CREATE UNIQUE INDEX idx_tickets_unique_url ON tickets(unique_url)"))
            print("OK - Indice creado exitosamente")
        except Exception as e:
            print(f"Indice ya existe o error: {e}")

        # Generar URLs y PINs para tickets existentes que no los tienen
        result = conn.execute(text("SELECT id FROM tickets WHERE unique_url IS NULL"))
        ticket_ids = [row[0] for row in result]

        for ticket_id in ticket_ids:
            unique_url = generate_unique_url()
            access_pin = generate_pin()
            conn.execute(
                text("UPDATE tickets SET unique_url = :url, access_pin = :pin WHERE id = :id"),
                {"url": unique_url, "pin": access_pin, "id": ticket_id}
            )

        conn.commit()
        print(f"OK - Generadas URLs y PINs para {len(ticket_ids)} tickets")

if __name__ == "__main__":
    migrate()
    print("\nOK - Migracion completada exitosamente")
