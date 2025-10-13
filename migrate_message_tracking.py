"""
Migración: Agregar tablas para seguimiento de campañas de mensajes
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    """Ejecutar migración"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        print("Creando tabla message_campaigns...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS message_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject VARCHAR NOT NULL,
                message TEXT NOT NULL,
                link VARCHAR,
                link_text VARCHAR,
                has_image BOOLEAN DEFAULT 0,
                image_path VARCHAR,
                send_email BOOLEAN DEFAULT 1,
                send_whatsapp BOOLEAN DEFAULT 0,
                total_recipients INTEGER DEFAULT 0,
                emails_sent INTEGER DEFAULT 0,
                emails_failed INTEGER DEFAULT 0,
                whatsapp_sent INTEGER DEFAULT 0,
                whatsapp_failed INTEGER DEFAULT 0,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES admin_users(id)
            )
        """))
        print("[OK] Tabla message_campaigns creada")

        print("Creando tabla message_recipients...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS message_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                email_sent BOOLEAN DEFAULT 0,
                email_sent_at DATETIME,
                email_error VARCHAR,
                whatsapp_sent BOOLEAN DEFAULT 0,
                whatsapp_sent_at DATETIME,
                whatsapp_message_id VARCHAR,
                whatsapp_status VARCHAR DEFAULT 'pending',
                whatsapp_status_updated_at DATETIME,
                whatsapp_error VARCHAR,
                FOREIGN KEY(campaign_id) REFERENCES message_campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """))
        print("[OK] Tabla message_recipients creada")

        # Crear índices para mejorar rendimiento
        print("Creando índices...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_campaigns_created_by
            ON message_campaigns(created_by)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_campaigns_created_at
            ON message_campaigns(created_at)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_recipients_campaign
            ON message_recipients(campaign_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_recipients_user
            ON message_recipients(user_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_recipients_whatsapp_message
            ON message_recipients(whatsapp_message_id)
        """))
        print("[OK] Índices creados")

        conn.commit()
        print("\n[OK] Migracion completada exitosamente!")

if __name__ == "__main__":
    migrate()
