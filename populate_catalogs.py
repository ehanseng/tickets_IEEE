"""Script para poblar todos los catálogos del sistema"""
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine('sqlite:///tickets.db')

with engine.connect() as conn:
    # ========== PROGRAMAS ACADÉMICOS ==========
    programs = [
        # Ingenierías
        ('Ingeniería de Sistemas', 'ISI', 'Ingeniería', 1),
        ('Ingeniería Industrial', 'IIN', 'Ingeniería', 2),
        ('Ingeniería Electrónica', 'IEL', 'Ingeniería', 3),
        ('Ingeniería Ambiental', 'IAM', 'Ingeniería', 4),
        ('Ingeniería Química', 'IQU', 'Ingeniería', 5),
        # Diseño y Artes
        ('Diseño Gráfico', 'DGR', 'Diseño', 10),
        ('Diseño Industrial', 'DIN', 'Diseño', 11),
        ('Diseño de Espacios y Escenarios', 'DEE', 'Diseño', 12),
        ('Diseño de Modas', 'DMO', 'Diseño', 13),
        ('Artes Plásticas', 'APL', 'Artes', 14),
        ('Cine y Televisión', 'CTV', 'Artes', 15),
        # Comunicación
        ('Publicidad', 'PUB', 'Comunicación', 20),
        ('Comunicación Social - Periodismo', 'CSP', 'Comunicación', 21),
        # Ciencias Económicas
        ('Administración de Empresas', 'ADE', 'Ciencias Económicas', 30),
        ('Economía', 'ECO', 'Ciencias Económicas', 31),
        ('Contaduría Pública', 'CON', 'Ciencias Económicas', 32),
        ('Comercio Internacional', 'COI', 'Ciencias Económicas', 33),
        ('Mercadeo', 'MER', 'Ciencias Económicas', 34),
        ('Finanzas y Comercio Internacional', 'FCI', 'Ciencias Económicas', 35),
        # Ciencias Naturales
        ('Biología Marina', 'BMA', 'Ciencias Naturales', 40),
        ('Biología Ambiental', 'BAM', 'Ciencias Naturales', 41),
        # Derecho y Relaciones Internacionales
        ('Derecho', 'DER', 'Ciencias Sociales', 50),
        ('Relaciones Internacionales', 'RIN', 'Ciencias Sociales', 51),
        ('Ciencia Política y Gobierno', 'CPG', 'Ciencias Sociales', 52),
        # Otros
        ('Gastronomía', 'GAS', 'Otros', 60),
        ('Arquitectura', 'ARQ', 'Otros', 61),
        ('Otro', 'OTR', 'Otros', 99),
    ]

    for name, short, cat, order in programs:
        conn.execute(text('''
            INSERT INTO academic_programs (name, short_name, category, is_active, display_order, created_at)
            VALUES (:name, :short, :cat, 1, :order, :now)
        '''), {'name': name, 'short': short, 'cat': cat, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(programs)} programas académicos')

    # ========== HABILIDADES TÉCNICAS ==========
    skills = [
        # Técnicas
        ('Python', 'programming', 'Lenguaje de programación', 'code', '#3776AB'),
        ('JavaScript', 'programming', 'Lenguaje de programación', 'code', '#F7DF1E'),
        ('Java', 'programming', 'Lenguaje de programación', 'code', '#007396'),
        ('C/C++', 'programming', 'Lenguaje de programación', 'code', '#00599C'),
        ('React', 'frontend', 'Framework frontend', 'layers', '#61DAFB'),
        ('Node.js', 'backend', 'Runtime backend', 'server', '#339933'),
        ('SQL', 'database', 'Bases de datos', 'database', '#4479A1'),
        ('Machine Learning', 'ai', 'Inteligencia Artificial', 'brain', '#FF6F00'),
        ('Arduino', 'hardware', 'Electrónica', 'cpu', '#00979D'),
        ('Raspberry Pi', 'hardware', 'Electrónica', 'cpu', '#C51A4A'),
        ('Git', 'tools', 'Control de versiones', 'git-branch', '#F05032'),
        ('Docker', 'devops', 'Contenedores', 'box', '#2496ED'),
        ('Linux', 'systems', 'Sistemas operativos', 'terminal', '#FCC624'),
        ('Diseño UI/UX', 'design', 'Diseño de interfaces', 'palette', '#FF7262'),
        ('Robótica', 'robotics', 'Robótica', 'robot', '#FF4081'),
        ('IoT', 'iot', 'Internet de las cosas', 'wifi', '#00C7B7'),
        # Blandas
        ('Comunicación', 'soft', 'Comunicación efectiva', 'comments', '#9333EA'),
        ('Trabajo en equipo', 'soft', 'Colaboración en equipos', 'users', '#EC4899'),
        ('Liderazgo', 'soft', 'Liderazgo de proyectos', 'crown', '#F59E0B'),
        ('Resolución de problemas', 'soft', 'Pensamiento crítico', 'lightbulb', '#10B981'),
        ('Creatividad', 'soft', 'Pensamiento creativo', 'palette', '#8B5CF6'),
        ('Gestión del tiempo', 'soft', 'Organización y planificación', 'clock', '#EF4444'),
        ('Adaptabilidad', 'soft', 'Flexibilidad al cambio', 'sync-alt', '#06B6D4'),
        ('Presentaciones', 'soft', 'Hablar en público', 'chalkboard-teacher', '#6366F1'),
    ]

    for name, cat, desc, icon, color in skills:
        conn.execute(text('''
            INSERT INTO skills (name, category, description, icon, color, is_active, display_order, created_at)
            VALUES (:name, :cat, :desc, :icon, :color, 1, 0, :now)
        '''), {'name': name, 'cat': cat, 'desc': desc, 'icon': icon, 'color': color, 'now': datetime.now()})
    print(f'Insertadas {len(skills)} habilidades')

    # ========== ÁREAS DE INTERÉS ==========
    interests = [
        ('Inteligencia Artificial', 'Desarrollo de sistemas inteligentes'),
        ('Robótica', 'Diseño y construcción de robots'),
        ('IoT', 'Internet de las cosas'),
        ('Desarrollo Web', 'Aplicaciones web frontend y backend'),
        ('Desarrollo Móvil', 'Aplicaciones para dispositivos móviles'),
        ('Ciberseguridad', 'Seguridad informática'),
        ('Cloud Computing', 'Computación en la nube'),
        ('Data Science', 'Ciencia de datos'),
        ('Blockchain', 'Tecnología blockchain'),
        ('Realidad Virtual/Aumentada', 'VR y AR'),
        ('Energías Renovables', 'Tecnologías sostenibles'),
        ('Automatización', 'Automatización de procesos'),
    ]

    for name, desc in interests:
        conn.execute(text('''
            INSERT INTO interest_areas (name, description, is_active, display_order, created_at)
            VALUES (:name, :desc, 1, 0, :now)
        '''), {'name': name, 'desc': desc, 'now': datetime.now()})
    print(f'Insertadas {len(interests)} áreas de interés')

    # ========== NIVELES DE INGLÉS ==========
    english = [
        ('A1', 'Principiante', 1),
        ('A2', 'Básico', 2),
        ('B1', 'Intermedio', 3),
        ('B2', 'Intermedio Alto', 4),
        ('C1', 'Avanzado', 5),
        ('C2', 'Nativo/Bilingüe', 6),
    ]

    for code, name, order in english:
        conn.execute(text('''
            INSERT INTO english_levels (code, name, display_order, is_active, created_at)
            VALUES (:code, :name, :order, 1, :now)
        '''), {'code': code, 'name': name, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(english)} niveles de inglés')

    # ========== RANGOS DE SEMESTRE ==========
    semesters = [
        ('1-2', 1, 2, 1),
        ('3-4', 3, 4, 2),
        ('5-6', 5, 6, 3),
        ('7-8', 7, 8, 4),
        ('9-10', 9, 10, 5),
        ('Egresado', None, None, 6),
    ]

    for name, min_sem, max_sem, order in semesters:
        conn.execute(text('''
            INSERT INTO semester_ranges (name, min_semester, max_semester, display_order, is_active, created_at)
            VALUES (:name, :min_sem, :max_sem, :order, 1, :now)
        '''), {'name': name, 'min_sem': min_sem, 'max_sem': max_sem, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(semesters)} rangos de semestre')

    # ========== NIVELES DE DISPONIBILIDAD ==========
    availability = [
        ('Baja', '1-5 horas/semana', 1, 5, 1),
        ('Media', '5-10 horas/semana', 5, 10, 2),
        ('Alta', '10-20 horas/semana', 10, 20, 3),
        ('Muy Alta', 'Más de 20 horas/semana', 20, 40, 4),
    ]

    for name, hours_desc, min_h, max_h, order in availability:
        conn.execute(text('''
            INSERT INTO availability_levels (name, hours_description, min_hours, max_hours, display_order, is_active, created_at)
            VALUES (:name, :hours_desc, :min_h, :max_h, :order, 1, :now)
        '''), {'name': name, 'hours_desc': hours_desc, 'min_h': min_h, 'max_h': max_h, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(availability)} niveles de disponibilidad')

    # ========== CANALES DE COMUNICACIÓN ==========
    channels = [
        ('WhatsApp', 'whatsapp', 1),
        ('Email', 'email', 2),
        ('Telegram', 'telegram', 3),
        ('Discord', 'discord', 4),
    ]

    for name, icon, order in channels:
        conn.execute(text('''
            INSERT INTO communication_channels (name, icon, display_order, is_active, created_at)
            VALUES (:name, :icon, :order, 1, :now)
        '''), {'name': name, 'icon': icon, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(channels)} canales de comunicación')

    # ========== SOCIEDADES IEEE ==========
    societies = [
        ('CS', 'Computer Society', 'Computación e informática'),
        ('RAS', 'Robotics and Automation Society', 'Robótica y automatización'),
        ('PES', 'Power & Energy Society', 'Energía y potencia'),
        ('ComSoc', 'Communications Society', 'Comunicaciones'),
        ('SPS', 'Signal Processing Society', 'Procesamiento de señales'),
        ('WIE', 'Women in Engineering', 'Mujeres en ingeniería'),
        ('YP', 'Young Professionals', 'Jóvenes profesionales'),
        ('CAS', 'Circuits and Systems Society', 'Circuitos y sistemas'),
    ]

    for code, name, desc in societies:
        conn.execute(text('''
            INSERT INTO ieee_societies (code, name, description, is_active, display_order, created_at)
            VALUES (:code, :name, :desc, 1, 0, :now)
        '''), {'code': code, 'name': name, 'desc': desc, 'now': datetime.now()})
    print(f'Insertadas {len(societies)} sociedades IEEE')

    # ========== ESTADOS DE MEMBRESÍA IEEE ==========
    statuses = [
        ('No miembro', 'No es miembro IEEE', 1),
        ('Miembro estudiante', 'Student Member', 2),
        ('Miembro graduado', 'Graduate Student Member', 3),
        ('Miembro profesional', 'Professional Member', 4),
        ('Miembro senior', 'Senior Member', 5),
    ]

    for name, desc, order in statuses:
        conn.execute(text('''
            INSERT INTO ieee_membership_statuses (name, description, display_order, is_active, created_at)
            VALUES (:name, :desc, :order, 1, :now)
        '''), {'name': name, 'desc': desc, 'order': order, 'now': datetime.now()})
    print(f'Insertados {len(statuses)} estados de membresía')

    conn.commit()
    print('\n¡Todos los catálogos poblados exitosamente!')
