"""
Script para importar usuarios desde CSV con soporte para tags
Detecta duplicados por email y agrega tags sin eliminar los existentes
"""
import csv
import sys
import io
from datetime import datetime
from database import SessionLocal
import models

# Configurar salida UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def import_users_from_csv(csv_file_path: str, tag_name: str, create_tag_if_not_exists: bool = True):
    """
    Importa usuarios desde un archivo CSV y les asigna un tag específico.
    Si el usuario ya existe (por email), agrega el tag sin eliminar los existentes.

    Args:
        csv_file_path: Ruta al archivo CSV
        tag_name: Nombre del tag a asignar (ej: "IEEE YP Co")
        create_tag_if_not_exists: Crear el tag si no existe

    Formato CSV esperado:
        name,email,phone,country_code,identification,university_name,is_ieee_member,ieee_member_id
    """
    db = SessionLocal()

    try:
        print("=" * 80)
        print(f"IMPORTACIÓN DE USUARIOS CON TAG: {tag_name}")
        print("=" * 80)
        print()

        # 1. Verificar/crear el tag
        print(f"1. Verificando tag '{tag_name}'...")
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()

        if not tag:
            if create_tag_if_not_exists:
                tag = models.Tag(
                    name=tag_name,
                    color="#10B981",  # Verde por defecto
                    description=f"Usuarios importados con tag {tag_name}",
                    is_active=True
                )
                db.add(tag)
                db.commit()
                db.refresh(tag)
                print(f"   ✓ Tag '{tag_name}' creado (ID: {tag.id})")
            else:
                print(f"   ✗ Error: Tag '{tag_name}' no existe")
                return
        else:
            print(f"   ✓ Tag '{tag_name}' encontrado (ID: {tag.id})")

        print()

        # 2. Leer el archivo CSV
        print(f"2. Leyendo archivo CSV: {csv_file_path}")

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            print(f"   ✓ {len(rows)} filas leídas del CSV")

        print()

        # 3. Procesar cada usuario
        print("3. Procesando usuarios...")
        print()

        stats = {
            'created': 0,
            'duplicates': 0,
            'tag_added': 0,
            'tag_already_exists': 0,
            'errors': 0
        }

        for i, row in enumerate(rows, start=1):
            try:
                email = row.get('email', '').strip().lower()
                name = row.get('name', '').strip()

                if not email or not name:
                    print(f"   [{i}] ⚠ Fila {i}: Email o nombre vacío - OMITIDO")
                    stats['errors'] += 1
                    continue

                # Buscar usuario existente por email
                existing_user = db.query(models.User).filter(models.User.email == email).first()

                if existing_user:
                    # Usuario duplicado - agregar tag si no lo tiene
                    stats['duplicates'] += 1

                    if tag in existing_user.tags:
                        print(f"   [{i}] ⟳ {name} ({email}): Ya existe y ya tiene el tag '{tag_name}'")
                        stats['tag_already_exists'] += 1
                    else:
                        existing_user.tags.append(tag)
                        db.commit()
                        print(f"   [{i}] ⟳ {name} ({email}): Ya existe - Tag '{tag_name}' AGREGADO")
                        stats['tag_added'] += 1
                else:
                    # Usuario nuevo - crear con el tag
                    phone = row.get('phone', '').strip() or None
                    country_code = row.get('country_code', '').strip() or '+57'
                    identification = row.get('identification', '').strip() or None
                    university_name = row.get('university_name', '').strip()
                    is_ieee_member = row.get('is_ieee_member', '').strip().lower() in ['true', '1', 'yes', 'sí', 'si']
                    ieee_member_id = row.get('ieee_member_id', '').strip() or None

                    # Buscar universidad
                    university_id = None
                    if university_name:
                        university = db.query(models.University).filter(
                            models.University.name == university_name
                        ).first()
                        if university:
                            university_id = university.id

                    # Crear usuario
                    new_user = models.User(
                        name=name,
                        email=email,
                        phone=phone,
                        country_code=country_code,
                        identification=identification,
                        university_id=university_id,
                        is_ieee_member=is_ieee_member,
                        ieee_member_id=ieee_member_id,
                        created_at=datetime.utcnow()
                    )

                    db.add(new_user)
                    db.flush()  # Para obtener el ID

                    # Agregar el tag
                    new_user.tags.append(tag)
                    db.commit()
                    db.refresh(new_user)

                    stats['created'] += 1
                    print(f"   [{i}] ✓ {name} ({email}): Usuario CREADO con tag '{tag_name}'")

            except Exception as e:
                print(f"   [{i}] ✗ Error procesando fila {i}: {e}")
                stats['errors'] += 1
                db.rollback()
                continue

        print()
        print("=" * 80)
        print("RESUMEN DE IMPORTACIÓN")
        print("=" * 80)
        print(f"Usuarios nuevos creados:          {stats['created']}")
        print(f"Usuarios duplicados encontrados:  {stats['duplicates']}")
        print(f"  - Tag agregado a duplicados:    {stats['tag_added']}")
        print(f"  - Tag ya existía en duplicados: {stats['tag_already_exists']}")
        print(f"Errores:                          {stats['errors']}")
        print(f"\nTotal procesado:                  {len(rows)}")
        print()

        # 4. Estadísticas finales del tag
        user_count = db.query(models.User).join(models.user_tags).filter(
            models.user_tags.c.tag_id == tag.id
        ).count()

        print(f"Total de usuarios con tag '{tag_name}': {user_count}")
        print()
        print("✓ Importación completada exitosamente")

    except FileNotFoundError:
        print(f"✗ Error: Archivo '{csv_file_path}' no encontrado")
    except Exception as e:
        print(f"✗ Error durante la importación: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Ejemplo de uso:
    # python import_users_with_tags.py usuarios_yp.csv "IEEE YP Co"

    if len(sys.argv) < 3:
        print("Uso: python import_users_with_tags.py <archivo.csv> <nombre_tag>")
        print()
        print("Ejemplo:")
        print('  python import_users_with_tags.py usuarios_yp.csv "IEEE YP Co"')
        print()
        print("Formato CSV esperado:")
        print("  name,email,phone,country_code,identification,university_name,is_ieee_member,ieee_member_id")
        print()
        print("Notas:")
        print("  - El tag será creado automáticamente si no existe")
        print("  - Si el usuario ya existe (por email), se le agrega el tag sin eliminar los existentes")
        print("  - Los usuarios duplicados NO se modifican, solo se les agrega el nuevo tag")
        sys.exit(1)

    csv_file = sys.argv[1]
    tag_name = sys.argv[2]

    import_users_from_csv(csv_file, tag_name)
