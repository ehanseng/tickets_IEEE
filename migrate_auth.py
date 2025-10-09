"""
Script para crear las tablas de autenticación y el usuario admin inicial
"""
from database import engine, SessionLocal
from models import Base, AdminUser, RoleEnum, ValidationLog
from auth import get_password_hash

def migrate_database():
    """Crea las nuevas tablas en la base de datos"""
    print("Creando tablas de autenticacion...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tablas creadas exitosamente")


def create_admin_user():
    """Crea el usuario administrador inicial"""
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(AdminUser).filter(
            AdminUser.username == "admin"
        ).first()

        if existing_admin:
            print("[OK] Usuario admin ya existe")
            return

        # Crear usuario admin
        admin = AdminUser(
            username="admin",
            email="admin@ieee.tadeo.edu.co",
            hashed_password=get_password_hash("admin123"),
            full_name="Administrador IEEE Tadeo",
            role=RoleEnum.ADMIN,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("[OK] Usuario administrador creado exitosamente")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  [IMPORTANTE] Cambia esta contrasena despues del primer login")

    except Exception as e:
        print(f"[ERROR] Error al crear usuario admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Migración de Base de Datos - Sistema de Autenticación ===\n")
    migrate_database()
    print()
    create_admin_user()
    print("\n=== Migración completada ===")
