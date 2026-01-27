"""
Script de migracion para:
1. Crear tabla user_studies para almacenar multiples estudios por usuario
2. Migrar datos existentes de academic_program_id a la nueva tabla

Ejecutar: python migrate_add_user_studies.py
"""
import sqlite3

conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

try:
    # 1. Crear tabla user_studies
    print("Creando tabla user_studies...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            study_type VARCHAR(20) NOT NULL,
            program_name VARCHAR(200) NOT NULL,
            institution VARCHAR(200),
            is_primary BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("[OK] Tabla user_studies creada/verificada")

    # 2. Crear indice para user_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_user_studies_user_id
        ON user_studies(user_id)
    """)
    print("[OK] Indice ix_user_studies_user_id creado/verificado")

    # 3. Migrar datos existentes de academic_program_id (si existe la tabla)
    print("\nMigrando datos existentes...")

    # Verificar si existe la tabla academic_programs
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='academic_programs'")
    has_academic_programs = cursor.fetchone() is not None

    migrated_count = 0
    if has_academic_programs:
        # Obtener usuarios con academic_program_id
        cursor.execute("""
            SELECT u.id, ap.name
            FROM users u
            JOIN academic_programs ap ON u.academic_program_id = ap.id
            WHERE u.academic_program_id IS NOT NULL
        """)
        users_with_programs = cursor.fetchall()

        for user_id, program_name in users_with_programs:
            # Verificar si ya existe un estudio para este usuario
            cursor.execute("""
                SELECT COUNT(*) FROM user_studies
                WHERE user_id = ? AND program_name = ?
            """, (user_id, program_name))
            exists = cursor.fetchone()[0] > 0

            if not exists:
                cursor.execute("""
                    INSERT INTO user_studies (user_id, study_type, program_name, institution, is_primary)
                    VALUES (?, 'pregrado', ?, 'Universidad de Bogota Jorge Tadeo Lozano', 1)
                """, (user_id, program_name))
                migrated_count += 1
        print(f"[OK] {migrated_count} estudios migrados desde academic_program_id")
    else:
        print("[INFO] Tabla academic_programs no existe, no hay datos para migrar")

    conn.commit()
    print("\n========================================")
    print("Migracion completada exitosamente!")
    print("========================================")
    print(f"\nResumen:")
    print(f"  - Tabla user_studies: CREADA")
    print(f"  - Estudios migrados: {migrated_count}")
    print(f"\nNota: El campo academic_program_id en users NO fue eliminado")
    print("      para mantener compatibilidad hacia atras.")

except sqlite3.Error as e:
    print(f"[ERROR] Error durante la migracion: {e}")
    conn.rollback()
finally:
    conn.close()
