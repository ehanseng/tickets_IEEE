"""Script para corregir las tildes en los proyectos de la base de datos"""
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///tickets.db')

# Actualizaciones de proyectos con tildes correctas
updates = [
    {
        "old_name": "IEEE Tadeo Control System",
        "new_name": "IEEE Tadeo Control System",
        "short_description": "Sistema integral de gestión para la rama estudiantil IEEE Tadeo. Automatización de eventos, tickets y comunicaciones."
    },
    {
        "old_name": "Reutilizacion de Equipos de Computo",
        "new_name": "Reutilización de Equipos de Cómputo",
        "short_description": "Programa de recolección, reparación y donación de equipos tecnológicos a comunidades vulnerables."
    },
    {
        "old_name": "Animatronicos IEEE",
        "new_name": "Animatrónicos IEEE",
        "short_description": "Desarrollo de personajes animatrónicos con robótica e inteligencia artificial para eventos educativos."
    }
]

with engine.connect() as conn:
    for update in updates:
        # Intentar actualizar por nombre viejo o nuevo (por si ya estaba correcto)
        result = conn.execute(text("""
            UPDATE projects
            SET name = :new_name, short_description = :short_description
            WHERE name = :old_name OR name = :new_name
        """), {
            "new_name": update["new_name"],
            "short_description": update["short_description"],
            "old_name": update["old_name"]
        })
        conn.commit()
        print(f"Actualizado: {update['new_name']} - Filas afectadas: {result.rowcount}")

print("\n¡Tildes corregidas exitosamente!")
