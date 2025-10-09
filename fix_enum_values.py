"""
Script para corregir los valores de enum en la base de datos
"""
from database import SessionLocal
from sqlalchemy import text

def fix_role_enum_values():
    """Corrige los valores de role de minúsculas a mayúsculas"""
    db = SessionLocal()
    try:
        # Actualizar 'admin' a 'ADMIN'
        db.execute(text("UPDATE admin_users SET role = 'ADMIN' WHERE role = 'admin'"))

        # Actualizar 'validator' a 'VALIDATOR'
        db.execute(text("UPDATE admin_users SET role = 'VALIDATOR' WHERE role = 'validator'"))

        db.commit()
        print("[OK] Valores de enum corregidos exitosamente")

        # Verificar
        result = db.execute(text("SELECT username, role FROM admin_users"))
        print("\nUsuarios actualizados:")
        for row in result:
            print(f"  - {row.username}: {row.role}")

    except Exception as e:
        print(f"[ERROR] Error al corregir valores: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Corrigiendo valores de enum en BD ===\n")
    fix_role_enum_values()
    print("\n=== Corrección completada ===")
