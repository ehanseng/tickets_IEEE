"""
Script para agregar los programas académicos de UTADEO al catálogo
Ejecutar con: python add_utadeo_programs.py
"""
import os
import sys

# Usar configuración de .env (no forzar nada)

from database import SessionLocal
import models

# Programas de UTADEO organizados por facultad
UTADEO_PROGRAMS = [
    # Ciencias Naturales e Ingeniería
    {"name": "Biología Ambiental", "short_name": "Biología Amb.", "category": "Ciencias Naturales e Ingeniería", "display_order": 10},
    {"name": "Biología Marina", "short_name": "Biología Mar.", "category": "Ciencias Naturales e Ingeniería", "display_order": 11},
    {"name": "Ingeniería Ambiental", "short_name": "Ing. Ambiental", "category": "Ciencias Naturales e Ingeniería", "display_order": 12},
    {"name": "Ingeniería de Alimentos", "short_name": "Ing. Alimentos", "category": "Ciencias Naturales e Ingeniería", "display_order": 13},
    {"name": "Ingeniería de Sistemas", "short_name": "Ing. Sistemas", "category": "Ciencias Naturales e Ingeniería", "display_order": 14},
    {"name": "Ingeniería en Energía", "short_name": "Ing. Energía", "category": "Ciencias Naturales e Ingeniería", "display_order": 15},
    {"name": "Ingeniería Industrial", "short_name": "Ing. Industrial", "category": "Ciencias Naturales e Ingeniería", "display_order": 16},
    {"name": "Ingeniería Química", "short_name": "Ing. Química", "category": "Ciencias Naturales e Ingeniería", "display_order": 17},

    # Ciencias Sociales
    {"name": "Ciencia Política e Innovación Pública", "short_name": "Ciencia Política", "category": "Ciencias Sociales", "display_order": 20},
    {"name": "Cine y Televisión", "short_name": "Cine y TV", "category": "Ciencias Sociales", "display_order": 21},
    {"name": "Comunicación Social-Periodismo", "short_name": "Comunicación", "category": "Ciencias Sociales", "display_order": 22},
    {"name": "Derecho", "short_name": "Derecho", "category": "Ciencias Sociales", "display_order": 23},
    {"name": "Historia del Arte", "short_name": "Historia Arte", "category": "Ciencias Sociales", "display_order": 24},
    {"name": "Relaciones Internacionales", "short_name": "Rel. Internac.", "category": "Ciencias Sociales", "display_order": 25},

    # Ciencias Económicas y Administrativas
    {"name": "Administración de Empresas", "short_name": "Administración", "category": "Ciencias Económicas y Administrativas", "display_order": 30},
    {"name": "Comercio Internacional y Finanzas", "short_name": "Comercio Int.", "category": "Ciencias Económicas y Administrativas", "display_order": 31},
    {"name": "Contaduría Pública", "short_name": "Contaduría", "category": "Ciencias Económicas y Administrativas", "display_order": 32},
    {"name": "Economía", "short_name": "Economía", "category": "Ciencias Económicas y Administrativas", "display_order": 33},
    {"name": "Mercadeo", "short_name": "Mercadeo", "category": "Ciencias Económicas y Administrativas", "display_order": 34},
    {"name": "Publicidad", "short_name": "Publicidad", "category": "Ciencias Económicas y Administrativas", "display_order": 35},

    # Artes y Diseño
    {"name": "Arquitectura", "short_name": "Arquitectura", "category": "Artes y Diseño", "display_order": 40},
    {"name": "Artes Plásticas", "short_name": "Artes Plást.", "category": "Artes y Diseño", "display_order": 41},
    {"name": "Diseño Gráfico", "short_name": "Diseño Gráfico", "category": "Artes y Diseño", "display_order": 42},
    {"name": "Diseño Industrial", "short_name": "Diseño Indust.", "category": "Artes y Diseño", "display_order": 43},
    {"name": "Diseño Interactivo", "short_name": "Diseño Int.", "category": "Artes y Diseño", "display_order": 44},
    {"name": "Diseño y Gestión de la Moda", "short_name": "Diseño Moda", "category": "Artes y Diseño", "display_order": 45},
    {"name": "Fotografía", "short_name": "Fotografía", "category": "Artes y Diseño", "display_order": 46},
    {"name": "Realización en Animación", "short_name": "Animación", "category": "Artes y Diseño", "display_order": 47},
]


def main():
    print("=" * 60)
    print("AGREGANDO PROGRAMAS DE UTADEO AL CATÁLOGO")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Verificar programas existentes
        existing = db.query(models.AcademicProgram).all()
        existing_names = {p.name for p in existing}

        print(f"\nProgramas existentes: {len(existing)}")
        for p in existing:
            print(f"  - {p.name}")

        # Agregar nuevos programas
        added = 0
        skipped = 0

        print(f"\n\nAgregando programas de UTADEO...")
        for program in UTADEO_PROGRAMS:
            if program["name"] in existing_names:
                print(f"  [SKIP] {program['name']} (ya existe)")
                skipped += 1
            else:
                new_program = models.AcademicProgram(**program)
                db.add(new_program)
                print(f"  [ADD] {program['name']}")
                added += 1

        db.commit()

        print(f"\n" + "=" * 60)
        print(f"RESUMEN")
        print(f"=" * 60)
        print(f"Programas agregados: {added}")
        print(f"Programas omitidos (ya existían): {skipped}")
        print(f"Total de programas ahora: {len(existing) + added}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
