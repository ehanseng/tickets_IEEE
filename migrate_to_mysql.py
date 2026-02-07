"""
Script de migración de SQLite a MySQL
Ejecutar con: python migrate_to_mysql.py
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Forzar uso de MySQL para este script
os.environ["DATABASE_TYPE"] = "mysql"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "3306"
os.environ["MYSQL_USER"] = "ieeetadeo"
os.environ["MYSQL_PASSWORD"] = "IEEE_Tadeo_2025!"
os.environ["MYSQL_DATABASE"] = "ieeetadeo"

# Importar después de configurar el entorno
from database import Base, engine as mysql_engine, SessionLocal as MySQLSession
import models

# Conexión a SQLite (origen)
SQLITE_URL = "sqlite:///./tickets.db"
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)


def create_mysql_tables():
    """Crear todas las tablas en MySQL"""
    print("Creando tablas en MySQL...")
    Base.metadata.create_all(bind=mysql_engine)
    print("  [OK] Tablas creadas")


def populate_catalogs(db):
    """Poblar catálogos con datos iniciales"""
    print("\nPoblando catálogos...")

    # 1. Programas Académicos
    programs = [
        {"name": "Ingeniería de Sistemas", "short_name": "Sistemas", "category": "Ingeniería", "display_order": 1},
        {"name": "Ingeniería en Automatización y Control", "short_name": "Automatización", "category": "Ingeniería", "display_order": 2},
        {"name": "Ingeniería Industrial", "short_name": "Industrial", "category": "Ingeniería", "display_order": 3},
        {"name": "Diseño Interactivo", "short_name": "Diseño Int.", "category": "Diseño", "display_order": 4},
        {"name": "Realización en Animación", "short_name": "Animación", "category": "Diseño", "display_order": 5},
        {"name": "Modelado y Producción Digital 3D", "short_name": "3D", "category": "Diseño", "display_order": 6},
        {"name": "Publicidad", "short_name": "Publicidad", "category": "Comunicación", "display_order": 7},
        {"name": "Matemáticas / Ciencias Básicas", "short_name": "Matemáticas", "category": "Ciencias", "display_order": 8},
        {"name": "Otro / No aplica", "short_name": "Otro", "category": "Otro", "display_order": 99},
    ]
    for p in programs:
        if not db.query(models.AcademicProgram).filter_by(name=p["name"]).first():
            db.add(models.AcademicProgram(**p))
    print("  [OK] Programas académicos")

    # 2. Rangos de Semestre
    semesters = [
        {"name": "1º a 3º (Ciclo Básico)", "min_semester": 1, "max_semester": 3, "display_order": 1},
        {"name": "4º a 6º (Ciclo Profesional Temprano)", "min_semester": 4, "max_semester": 6, "display_order": 2},
        {"name": "7º a 9º (Ciclo de Profundización)", "min_semester": 7, "max_semester": 9, "display_order": 3},
        {"name": "10º / Proyecto de Grado", "min_semester": 10, "max_semester": 10, "display_order": 4},
        {"name": "Egresado / Graduado", "min_semester": None, "max_semester": None, "display_order": 5},
        {"name": "Posgrado / Maestría", "min_semester": None, "max_semester": None, "display_order": 6},
    ]
    for s in semesters:
        if not db.query(models.SemesterRange).filter_by(name=s["name"]).first():
            db.add(models.SemesterRange(**s))
    print("  [OK] Rangos de semestre")

    # 3. Niveles de Inglés
    english_levels = [
        {"code": "A1", "name": "A1 - Principiante", "display_order": 1},
        {"code": "A2", "name": "A2 - Básico", "display_order": 2},
        {"code": "B1", "name": "B1 - Umbral (Intermedio bajo)", "display_order": 3},
        {"code": "B2", "name": "B2 - Avanzado (Intermedio alto)", "display_order": 4},
        {"code": "C1", "name": "C1 - Dominio Operativo Eficaz", "display_order": 5},
        {"code": "C2", "name": "C2 - Maestría", "display_order": 6},
    ]
    for e in english_levels:
        if not db.query(models.EnglishLevel).filter_by(code=e["code"]).first():
            db.add(models.EnglishLevel(**e))
    print("  [OK] Niveles de inglés")

    # 4. Estados de Membresía IEEE
    membership_statuses = [
        {"name": "No miembro (Simpatizante)", "display_order": 1},
        {"name": "Student Member (Pregrado)", "display_order": 2},
        {"name": "Graduate Student Member (Posgrado)", "display_order": 3},
        {"name": "Young Professional (Recién graduado)", "display_order": 4},
        {"name": "Senior Member / Life Member (Mentores)", "display_order": 5},
    ]
    for m in membership_statuses:
        if not db.query(models.IEEEMembershipStatus).filter_by(name=m["name"]).first():
            db.add(models.IEEEMembershipStatus(**m))
    print("  [OK] Estados de membresía IEEE")

    # 5. Sociedades IEEE
    societies = [
        {"code": "CS", "name": "Computer Society", "full_name": "IEEE Computer Society", "society_type": "technical", "color": "#0066cc", "display_order": 1},
        {"code": "RAS", "name": "Robotics and Automation Society", "full_name": "IEEE Robotics and Automation Society", "society_type": "technical", "color": "#ff6600", "display_order": 2},
        {"code": "PES", "name": "Power & Energy Society", "full_name": "IEEE Power & Energy Society", "society_type": "technical", "color": "#009900", "display_order": 3},
        {"code": "ComSoc", "name": "Communications Society", "full_name": "IEEE Communications Society", "society_type": "technical", "color": "#9933cc", "display_order": 4},
        {"code": "IAS", "name": "Industry Applications Society", "full_name": "IEEE Industry Applications Society", "society_type": "technical", "color": "#cc6600", "display_order": 5},
        {"code": "EMBS", "name": "Engineering in Medicine and Biology", "full_name": "IEEE Engineering in Medicine and Biology Society", "society_type": "technical", "color": "#cc0066", "display_order": 6},
        {"code": "WIE", "name": "Women in Engineering", "full_name": "IEEE Women in Engineering", "society_type": "affinity", "color": "#9933ff", "display_order": 7},
        {"code": "SIGHT", "name": "SIGHT (Tecnología Humanitaria)", "full_name": "IEEE Special Interest Group on Humanitarian Technology", "society_type": "affinity", "color": "#33cccc", "display_order": 8},
    ]
    for s in societies:
        if not db.query(models.IEEESociety).filter_by(code=s["code"]).first():
            db.add(models.IEEESociety(**s))
    print("  [OK] Sociedades IEEE")

    # 6. Áreas de Interés
    interest_areas = [
        {"name": "Gestión y Liderazgo", "description": "Presidencia, tesorería, dirección de proyectos", "icon": "fa-users-cog", "display_order": 1},
        {"name": "Técnico / I+D", "description": "Desarrollo de proyectos, talleres, hackathons", "icon": "fa-code", "display_order": 2},
        {"name": "Marketing y Comunicaciones", "description": "Redes sociales, diseño, video", "icon": "fa-bullhorn", "display_order": 3},
        {"name": "Logística y Eventos", "description": "Organización, staff, protocolo", "icon": "fa-calendar-check", "display_order": 4},
        {"name": "Académico", "description": "Tutorías, redacción de papers, investigación", "icon": "fa-graduation-cap", "display_order": 5},
    ]
    for a in interest_areas:
        if not db.query(models.InterestArea).filter_by(name=a["name"]).first():
            db.add(models.InterestArea(**a))
    print("  [OK] Áreas de interés")

    # 7. Niveles de Disponibilidad
    availability_levels = [
        {"name": "Baja (Menos de 2 horas)", "hours_description": "Menos de 2 horas - Apoyo puntual", "min_hours": 0, "max_hours": 2, "display_order": 1},
        {"name": "Media (2 a 5 horas)", "hours_description": "2 a 5 horas - Miembro activo", "min_hours": 2, "max_hours": 5, "display_order": 2},
        {"name": "Alta (Más de 5 horas)", "hours_description": "Más de 5 horas - Liderazgo/Directiva", "min_hours": 5, "max_hours": None, "display_order": 3},
    ]
    for a in availability_levels:
        if not db.query(models.AvailabilityLevel).filter_by(name=a["name"]).first():
            db.add(models.AvailabilityLevel(**a))
    print("  [OK] Niveles de disponibilidad")

    # 8. Canales de Comunicación
    channels = [
        {"name": "WhatsApp", "description": "Mensajería rápida", "icon": "fa-whatsapp", "display_order": 1},
        {"name": "Correo Electrónico", "description": "Comunicación formal", "icon": "fa-envelope", "display_order": 2},
        {"name": "Discord / Slack", "description": "Trabajo colaborativo", "icon": "fa-discord", "display_order": 3},
    ]
    for c in channels:
        if not db.query(models.CommunicationChannel).filter_by(name=c["name"]).first():
            db.add(models.CommunicationChannel(**c))
    print("  [OK] Canales de comunicación")

    # 9. Habilidades
    skills = [
        # Técnicas (Hard Skills)
        {"name": "Python", "category": "technical", "icon": "fa-python", "color": "#3776ab", "display_order": 1},
        {"name": "JavaScript / Web", "category": "technical", "icon": "fa-js", "color": "#f7df1e", "display_order": 2},
        {"name": "Arduino / Electrónica", "category": "technical", "icon": "fa-microchip", "color": "#00979d", "display_order": 3},
        {"name": "Redes / Infraestructura", "category": "technical", "icon": "fa-network-wired", "color": "#666666", "display_order": 4},
        {"name": "Diseño 3D / CAD", "category": "technical", "icon": "fa-cube", "color": "#ff6600", "display_order": 5},
        {"name": "Inteligencia Artificial / ML", "category": "technical", "icon": "fa-brain", "color": "#9933cc", "display_order": 6},
        {"name": "Bases de Datos", "category": "technical", "icon": "fa-database", "color": "#336699", "display_order": 7},
        {"name": "Mobile (Android/iOS)", "category": "technical", "icon": "fa-mobile-alt", "color": "#3ddc84", "display_order": 8},
        # Blandas (Soft Skills)
        {"name": "Diseño Gráfico / Edición de Video", "category": "soft", "icon": "fa-paint-brush", "color": "#ff3366", "display_order": 20},
        {"name": "Hablar en público / Presentador", "category": "soft", "icon": "fa-microphone", "color": "#ff9900", "display_order": 21},
        {"name": "Logística y organización de eventos", "category": "soft", "icon": "fa-tasks", "color": "#33cc33", "display_order": 22},
        {"name": "Redacción y gestión de redes sociales", "category": "soft", "icon": "fa-share-alt", "color": "#0099ff", "display_order": 23},
        {"name": "Finanzas / Patrocinios", "category": "soft", "icon": "fa-dollar-sign", "color": "#339933", "display_order": 24},
        {"name": "Fotografía", "category": "soft", "icon": "fa-camera", "color": "#666699", "display_order": 25},
    ]
    for s in skills:
        if not db.query(models.Skill).filter_by(name=s["name"]).first():
            db.add(models.Skill(**s))
    print("  [OK] Habilidades")

    db.commit()
    print("\n[OK] Catálogos poblados correctamente")


def migrate_data():
    """Migrar datos de SQLite a MySQL"""
    print("\nMigrando datos de SQLite a MySQL...")

    sqlite_db = SQLiteSession()
    mysql_db = MySQLSession()

    try:
        # Orden de migración importante por las foreign keys
        tables_to_migrate = [
            ("universities", models.University),
            ("organizations", models.Organization),
            ("tags", models.Tag),
            ("users", models.User),
            ("user_tags", None),  # Tabla de asociación
            ("events", models.Event),
            ("tickets", models.Ticket),
            ("admin_users", models.AdminUser),
            ("validation_logs", models.ValidationLog),
            ("birthday_check_logs", models.BirthdayCheckLog),
            ("message_campaigns", models.MessageCampaign),
            ("message_recipients", models.MessageRecipient),
            ("whatsapp_templates", models.WhatsAppTemplate),
            ("whatsapp_messages", models.WhatsAppMessage),
            ("whatsapp_conversations", models.WhatsAppConversation),
            ("user_otps", models.UserOTP),
        ]

        for table_name, model_class in tables_to_migrate:
            try:
                # Contar registros en SQLite
                result = sqlite_db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()

                if count == 0:
                    print(f"  [-] {table_name}: 0 registros (tabla vacía)")
                    continue

                # Obtener todos los registros
                result = sqlite_db.execute(text(f"SELECT * FROM {table_name}"))
                rows = result.fetchall()
                columns = result.keys()

                # Insertar en MySQL
                for row in rows:
                    data = dict(zip(columns, row))

                    # Limpiar campos que no existen en el nuevo modelo
                    if table_name == "users":
                        # Remover columna 'university' (texto) que ya no existe
                        data.pop('university', None)

                    mysql_db.execute(
                        text(f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join([':' + k for k in data.keys()])})"),
                        data
                    )

                mysql_db.commit()
                print(f"  [OK] {table_name}: {count} registros migrados")

            except Exception as e:
                print(f"  [ERROR] {table_name}: {str(e)}")
                mysql_db.rollback()

    finally:
        sqlite_db.close()
        mysql_db.close()

    print("\n[OK] Migración de datos completada")


def main():
    print("=" * 60)
    print("MIGRACIÓN DE SQLITE A MYSQL - IEEE TADEO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Verificar conexión a MySQL
    print("Verificando conexión a MySQL...")
    try:
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print(f"  [OK] Conectado a MySQL/MariaDB: {version}")
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar a MySQL: {e}")
        sys.exit(1)

    # Verificar conexión a SQLite
    print("\nVerificando conexión a SQLite...")
    try:
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"  [OK] Conectado a SQLite - {count} usuarios encontrados")
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar a SQLite: {e}")
        sys.exit(1)

    # Crear tablas
    create_mysql_tables()

    # Poblar catálogos
    mysql_db = MySQLSession()
    try:
        populate_catalogs(mysql_db)
    finally:
        mysql_db.close()

    # Migrar datos
    migrate_data()

    print("\n" + "=" * 60)
    print("MIGRACIÓN COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Actualizar .env con DATABASE_TYPE=mysql")
    print("2. Reiniciar el servicio: sudo systemctl restart ieeetadeo")
    print("3. Verificar que todo funcione correctamente")


if __name__ == "__main__":
    main()
