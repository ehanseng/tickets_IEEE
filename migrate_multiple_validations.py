"""
Migración para implementar validaciones múltiples y zona horaria de Bogotá

Cambios:
1. Agregar campo validation_mode a tickets: 'once' (1 vez) o 'daily' (1 vez por día)
2. Agregar campo event_duration_days a events: duración del evento en días
3. Actualizar tabla validation_logs para registrar todas las validaciones
4. Ajustar todas las fechas existentes a zona horaria de Bogotá (UTC-5)
"""

import sqlite3
from datetime import datetime, timedelta
from pytz import timezone

# Zona horaria de Bogotá
BOGOTA_TZ = timezone('America/Bogota')

def migrate():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    print("=== Iniciando migración de validaciones múltiples ===\n")

    # 1. Agregar campos a tabla tickets
    print("1. Agregando campo validation_mode a tickets...")
    try:
        cursor.execute("""
            ALTER TABLE tickets
            ADD COLUMN validation_mode TEXT DEFAULT 'once'
        """)
        print("   [OK] Campo validation_mode agregado")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   [AVISO] Campo validation_mode ya existe")
        else:
            raise

    # 2. Agregar campos a tabla events
    print("2. Agregando campo event_duration_days a events...")
    try:
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN event_duration_days INTEGER DEFAULT 1
        """)
        print("   [OK] Campo event_duration_days agregado")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   [AVISO] Campo event_duration_days ya existe")
        else:
            raise

    try:
        cursor.execute("""
            ALTER TABLE events
            ADD COLUMN event_end_date DATETIME
        """)
        print("   [OK] Campo event_end_date agregado")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   [AVISO] Campo event_end_date ya existe")
        else:
            raise

    # 3. Migrar datos de validation_logs si la tabla ya tiene registros
    print("3. Verificando estructura de validation_logs...")
    cursor.execute("SELECT COUNT(*) FROM validation_logs")
    validation_count = cursor.fetchone()[0]

    if validation_count > 0:
        print(f"   [AVISO] Se encontraron {validation_count} registros en validation_logs")
        print("   Estos registros se mantendrán para referencia histórica")

    # 4. Migrar tickets con is_used=True a validation_logs
    print("4. Migrando tickets validados a validation_logs...")
    cursor.execute("""
        SELECT id, used_at
        FROM tickets
        WHERE is_used = 1 AND used_at IS NOT NULL
    """)
    used_tickets = cursor.fetchall()

    if used_tickets:
        print(f"   Encontrados {len(used_tickets)} tickets validados")
        # Obtener el primer admin/validator para asignar las validaciones antiguas
        cursor.execute("SELECT id FROM admin_users ORDER BY id LIMIT 1")
        admin_result = cursor.fetchone()

        if admin_result:
            default_validator_id = admin_result[0]
            for ticket_id, used_at in used_tickets:
                # Verificar si ya existe un registro para este ticket
                cursor.execute("""
                    SELECT COUNT(*) FROM validation_logs
                    WHERE ticket_id = ?
                """, (ticket_id,))

                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO validation_logs
                        (ticket_id, validator_id, validated_at, success, notes)
                        VALUES (?, ?, ?, 1, 'Migracion automatica de validacion anterior')
                    """, (ticket_id, default_validator_id, used_at))

            print(f"   [OK] Migrados {len(used_tickets)} tickets a validation_logs")
        else:
            print("   [AVISO] No se encontro un validador. Se omite la migracion de registros antiguos")
    else:
        print("   [INFO] No hay tickets validados para migrar")

    # 5. Ajustar fechas a zona horaria de Bogotá
    print("\n5. Ajustando fechas a zona horaria de Bogotá (UTC-5)...")

    # Ajustar tickets.used_at
    cursor.execute("SELECT id, used_at FROM tickets WHERE used_at IS NOT NULL")
    tickets_with_dates = cursor.fetchall()

    if tickets_with_dates:
        print(f"   Ajustando {len(tickets_with_dates)} fechas en tickets...")
        for ticket_id, used_at in tickets_with_dates:
            try:
                # Parsear la fecha (asumiendo que está en UTC)
                if isinstance(used_at, str):
                    dt_utc = datetime.fromisoformat(used_at.replace('Z', '+00:00'))
                else:
                    dt_utc = datetime.strptime(used_at, '%Y-%m-%d %H:%M:%S.%f')

                # Convertir a Bogotá (restar 5 horas)
                dt_bogota = dt_utc - timedelta(hours=5)

                cursor.execute("""
                    UPDATE tickets
                    SET used_at = ?
                    WHERE id = ?
                """, (dt_bogota.strftime('%Y-%m-%d %H:%M:%S'), ticket_id))
            except Exception as e:
                print(f"   [AVISO] Error ajustando fecha del ticket {ticket_id}: {e}")

        print("   [OK] Fechas de tickets ajustadas")

    # Ajustar validation_logs.validated_at
    cursor.execute("SELECT id, validated_at FROM validation_logs")
    validations_with_dates = cursor.fetchall()

    if validations_with_dates:
        print(f"   Ajustando {len(validations_with_dates)} fechas en validation_logs...")
        for val_id, validated_at in validations_with_dates:
            try:
                # Parsear la fecha
                if isinstance(validated_at, str):
                    dt_utc = datetime.fromisoformat(validated_at.replace('Z', '+00:00'))
                else:
                    dt_utc = datetime.strptime(validated_at, '%Y-%m-%d %H:%M:%S.%f')

                # Convertir a Bogotá
                dt_bogota = dt_utc - timedelta(hours=5)

                cursor.execute("""
                    UPDATE validation_logs
                    SET validated_at = ?
                    WHERE id = ?
                """, (dt_bogota.strftime('%Y-%m-%d %H:%M:%S'), val_id))
            except Exception as e:
                print(f"   [AVISO] Error ajustando fecha de validacion {val_id}: {e}")

        print("   [OK] Fechas de validation_logs ajustadas")

    # Confirmar cambios
    conn.commit()

    # Verificar cambios
    print("\n6. Verificando cambios...")
    cursor.execute("PRAGMA table_info(tickets)")
    tickets_columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columnas de tickets: {', '.join(tickets_columns)}")

    cursor.execute("PRAGMA table_info(events)")
    events_columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columnas de events: {', '.join(events_columns)}")

    cursor.execute("SELECT COUNT(*) FROM validation_logs")
    total_validations = cursor.fetchone()[0]
    print(f"   Total de validaciones registradas: {total_validations}")

    conn.close()

    print("\n=== Migración completada exitosamente ===")
    print("\nNotas importantes:")
    print("- Todos los tickets existentes tienen validation_mode='once' (1 validación)")
    print("- Todos los eventos tienen event_duration_days=1 (1 día de duración)")
    print("- Las fechas de validación se ajustaron a zona horaria de Bogotá (UTC-5)")
    print("- Puedes cambiar estos valores desde la interfaz de administración")

if __name__ == "__main__":
    migrate()
