"""
Script para crear la tabla de concursos y cargar datos iniciales.
Ejecutar en el servidor: python seed_contests.py
"""
from database import engine, SessionLocal, Base
from models import Contest

# Crear tabla si no existe
Contest.__table__.create(bind=engine, checkfirst=True)
print("Tabla 'contests' creada/verificada.")

# Datos iniciales
contests_data = [
    {
        "name": "IEEE Region 9 Website Contest",
        "description": "Diseno del mejor sitio web para Ramas Estudiantiles o Capitulos de Latinoamerica.",
        "category": "IEEE",
        "modality": "Virtual",
        "prizes": "Certificacion Regional y Membresia IEEE 2027 paga.",
        "deadline": "Cierre: Marzo 2026",
        "display_order": 1
    },
    {
        "name": "IEEE CASS Student Design",
        "description": "Solucion a problemas reales usando circuitos y sistemas (Fase R9).",
        "category": "IEEE",
        "modality": "Hibrida",
        "prizes": "$3,000 USD + Viaje pagado a Shanghai para la final.",
        "deadline": "Fase Regional: Ene-Mar 2026",
        "display_order": 2
    },
    {
        "name": "AP-S Student Design Contest",
        "description": "Antenas compactas para aplicaciones automotrices (V2X, Radar, 5G).",
        "category": "IEEE",
        "modality": "Hibrida",
        "prizes": "$1,500 USD para prototipo + hasta $6,000 para viaje.",
        "deadline": "Entrega Final: 18 de mayo",
        "display_order": 3
    },
    {
        "name": "IEEE SP Cup (Signal Processing)",
        "description": "Algoritmos de Zoom Audiovisual en tiempo real para Smartphones.",
        "category": "IEEE",
        "modality": "Virtual",
        "prizes": "$1,000 a $3,000 USD + Licencias MATLAB.",
        "deadline": "Cierre: Marzo 2026",
        "display_order": 4
    },
    {
        "name": "International IMS Contest",
        "description": "Diseno de sistemas de instrumentacion y medicion innovadores.",
        "category": "IEEE",
        "modality": "Presencial",
        "prizes": "$3,000 USD (1er lugar) y $2,000 (2do lugar).",
        "deadline": "Aplicacion: Feb 2026 / Final: Mayo 2026",
        "display_order": 5
    },
    {
        "name": "IEEE Conference on Games (CoG)",
        "description": "Desarrollo de IA para juegos y diseno de niveles procedurales.",
        "category": "IEEE",
        "modality": "Presencial",
        "prizes": "Publicacion en IEEE Xplore y premios por patrocinadores.",
        "deadline": "Cierre Papers: 17 de marzo",
        "display_order": 6
    },
    {
        "name": "IEEEXtreme 20.0",
        "description": "Competencia global de programacion competitiva (24 horas).",
        "category": "IEEE",
        "modality": "Virtual",
        "prizes": "Viaje a conferencia IEEE a eleccion y dispositivos.",
        "deadline": "Evento: Octubre 2026",
        "display_order": 7
    },
    {
        "name": "IEEE PES T&D Student Poster",
        "description": "Investigacion en Transmision y Distribucion de Energia.",
        "category": "IEEE",
        "modality": "Presencial",
        "prizes": "Apoyo para viaje (Stipends) y premios en efectivo.",
        "deadline": "Evento: 4-7 de mayo",
        "display_order": 8
    },
]

db = SessionLocal()
try:
    existing = db.query(Contest).count()
    if existing > 0:
        print(f"Ya hay {existing} concursos en la base de datos. No se insertaron duplicados.")
    else:
        for data in contests_data:
            contest = Contest(**data)
            db.add(contest)
        db.commit()
        print(f"Se insertaron {len(contests_data)} concursos exitosamente.")
finally:
    db.close()
