"""
Migración: Agregar tabla birthday_check_logs para registrar ejecuciones del sistema de cumpleaños
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BirthdayCheckLog(Base):
    """Registro de ejecuciones del sistema de cumpleaños"""
    __tablename__ = "birthday_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    birthdays_found = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    whatsapp_sent = Column(Integer, default=0)
    whatsapp_failed = Column(Integer, default=0)
    whatsapp_available = Column(Boolean, default=False)
    execution_type = Column(String, default="automatic")
    notes = Column(Text, nullable=True)


def migrate():
    """Ejecutar migración"""
    print("=" * 60)
    print("Migración: Agregar tabla birthday_check_logs")
    print("=" * 60)

    # Crear conexión a la base de datos
    engine = create_engine('sqlite:///./tickets.db')

    try:
        # Crear la tabla
        print("\n[1/2] Creando tabla birthday_check_logs...")
        Base.metadata.create_all(engine, tables=[BirthdayCheckLog.__table__])
        print("      [OK] Tabla creada exitosamente")

        print("\n[2/2] Verificando estructura...")
        from sqlalchemy import inspect
        inspector = inspect(engine)

        if 'birthday_check_logs' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('birthday_check_logs')]
            print(f"      [OK] Tabla verificada con {len(columns)} columnas:")
            for col in columns:
                print(f"           - {col}")
        else:
            print("      [ERROR] La tabla no se creó correctamente")
            return False

        print("\n" + "=" * 60)
        print("✓ Migración completada exitosamente")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERROR] Error durante la migración: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    migrate()
