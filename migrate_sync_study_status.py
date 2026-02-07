"""
Migración para sincronizar el estado de estudios primarios
con el rango de semestre del usuario.

Si el usuario tiene "Egresado / Graduado" como semestre,
su estudio principal debe tener status = 'egresado'
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
        # Buscar el ID de "Egresado / Graduado"
        cursor.execute("""
            SELECT id FROM semester_ranges
            WHERE name LIKE '%Egresado%' OR name LIKE '%Graduado%'
        """)
        egresado_row = cursor.fetchone()

        if not egresado_row:
            print("No se encontró el rango de semestre 'Egresado / Graduado'")
            return False

        egresado_id = egresado_row[0]
        print(f"ID de 'Egresado / Graduado': {egresado_id}")

        # Actualizar estudios primarios de usuarios egresados
        cursor.execute("""
            UPDATE user_studies
            SET status = 'egresado'
            WHERE is_primary = 1
            AND user_id IN (
                SELECT id FROM users WHERE semester_range_id = ?
            )
            AND status != 'egresado'
        """, (egresado_id,))

        updated_count = cursor.rowcount
        print(f"\nEstudios primarios actualizados a 'egresado': {updated_count}")

        # Mostrar estadísticas
        cursor.execute("""
            SELECT us.status, COUNT(*)
            FROM user_studies us
            WHERE us.is_primary = 1
            GROUP BY us.status
        """)
        status_counts = cursor.fetchall()

        print("\nEstadísticas de estudios primarios:")
        for status, count in status_counts:
            print(f"  - {status}: {count}")

        conn.commit()
        return True

    except Exception as e:
        print(f"Error durante la migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Migración: Sincronizar status con semestre ===\n")
    success = migrate()
    if success:
        print("\nMigración completada exitosamente")
    else:
        print("\nMigración fallida")
