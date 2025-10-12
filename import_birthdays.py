"""
Script para importar cumpleaños desde Google Sheet a la base de datos

Compara nombres y emails de usuarios y actualiza sus cumpleaños automáticamente.
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import SessionLocal
import models


# Datos del Google Sheet
GOOGLE_SHEET_DATA = [
    {"nombre": "Erick Hansen", "email": "erick@ieee.org", "cumpleanos": "24/08"},
    {"nombre": "Lina Gutierrez", "email": "rojaslaiala0@gmail.com", "cumpleanos": "11/04"},
    {"nombre": "Sofía Barriga", "email": "karensofia4019@gmail.com", "cumpleanos": "13/04"},
    {"nombre": "Salome Ramírez", "email": "salomeramirezr330@gmail.com", "cumpleanos": "30/03"},
    {"nombre": "Michelle Pabon", "email": "mspabong@gmail.com", "cumpleanos": "18/11"},
    {"nombre": "Carlos López", "email": "carloslopez1561@gmail.com", "cumpleanos": "02/05"},
    {"nombre": "Sofia Bulla", "email": "soff.bp12@gmail.com", "cumpleanos": "21/12"},
    {"nombre": "Víctoria Salazar", "email": "", "cumpleanos": "16/06"},
    {"nombre": "Karina Obando", "email": "", "cumpleanos": "01/03"},
    {"nombre": "María Alejandra Agudelo", "email": "writter.alejag@gmail.com", "cumpleanos": "13/09"},
    {"nombre": "Mariangel Lambraño", "email": "margelt03@gmail.com", "cumpleanos": "03/12"},
    {"nombre": "Nicolle García", "email": "", "cumpleanos": "04/07"},
    {"nombre": "Juan Coronado", "email": "", "cumpleanos": "30/06"},
    {"nombre": "Dana Trujillo", "email": "", "cumpleanos": "03/04"},
    {"nombre": "Sara Bernal", "email": "sarabg1316@gmail.com", "cumpleanos": "16/05"},
    {"nombre": "Andreina Mejia", "email": "josney1503@gmail.com", "cumpleanos": "15/03"},
]


def normalize_name(name):
    """Normaliza un nombre para comparación (minúsculas, sin acentos, sin espacios extra)"""
    import unicodedata
    # Convertir a minúsculas
    name = name.lower()
    # Remover acentos
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    # Remover espacios extra
    name = ' '.join(name.split())
    return name


def parse_birthday(birthday_str):
    """
    Convierte string de cumpleaños (DD/MM) a objeto datetime.
    Usa el año 2000 como año por defecto ya que solo nos importa mes/día.
    """
    try:
        day, month = birthday_str.split('/')
        # Usar año 2000 como año genérico
        return datetime(2000, int(month), int(day))
    except Exception as e:
        print(f"[ERROR] No se pudo parsear fecha '{birthday_str}': {e}")
        return None


def find_user_match(sheet_user, db_users):
    """
    Encuentra coincidencia de usuario por email o nombre similar.

    Retorna: (usuario_db, tipo_match) donde tipo_match es 'email' o 'nombre'
    """
    sheet_email = sheet_user['email'].lower().strip() if sheet_user['email'] else ""
    sheet_name_normalized = normalize_name(sheet_user['nombre'])

    # Primero intentar por email (más confiable)
    if sheet_email:
        for db_user in db_users:
            db_email = db_user.email.lower().strip() if db_user.email else ""
            if db_email and sheet_email == db_email:
                return (db_user, 'email')

    # Si no hay match por email, intentar por nombre
    for db_user in db_users:
        db_name_normalized = normalize_name(db_user.name)

        # Coincidencia exacta de nombre normalizado
        if db_name_normalized == sheet_name_normalized:
            return (db_user, 'nombre_exacto')

        # Coincidencia parcial: todos los tokens del sheet están en db
        sheet_tokens = set(sheet_name_normalized.split())
        db_tokens = set(db_name_normalized.split())

        # Si el nombre del sheet está contenido en el nombre de la DB
        if sheet_tokens.issubset(db_tokens) or db_tokens.issubset(sheet_tokens):
            return (db_user, 'nombre_parcial')

    return (None, None)


def import_birthdays():
    """Importa cumpleaños del Google Sheet a la base de datos"""
    db: Session = SessionLocal()

    try:
        print("=" * 70)
        print("IMPORTADOR DE CUMPLEAÑOS - Google Sheet a Base de Datos")
        print("=" * 70)

        # Obtener todos los usuarios de la DB
        db_users = db.query(models.User).all()
        print(f"\n[INFO] Usuarios en la base de datos: {len(db_users)}")
        print(f"[INFO] Usuarios en el Google Sheet: {len(GOOGLE_SHEET_DATA)}")
        print("\n" + "-" * 70)

        updated_count = 0
        not_found_count = 0
        skipped_count = 0

        for sheet_user in GOOGLE_SHEET_DATA:
            nombre = sheet_user['nombre']
            email = sheet_user['email']
            cumpleanos_str = sheet_user['cumpleanos']

            print(f"\n>> Procesando: {nombre}")
            print(f"   Email Sheet: {email if email else '(sin email)'}")
            print(f"   Cumpleaños: {cumpleanos_str}")

            # Buscar usuario en la DB
            db_user, match_type = find_user_match(sheet_user, db_users)

            if not db_user:
                print(f"   [NO ENCONTRADO] No se encontró coincidencia en la DB")
                not_found_count += 1
                continue

            print(f"   [MATCH] Encontrado por {match_type}: {db_user.name} ({db_user.email})")

            # Verificar si ya tiene cumpleaños
            if db_user.birthday:
                print(f"   [SKIP] Ya tiene cumpleaños configurado: {db_user.birthday.strftime('%d/%m/%Y')}")
                skipped_count += 1
                continue

            # Parsear y actualizar cumpleaños
            birthday = parse_birthday(cumpleanos_str)
            if birthday:
                db_user.birthday = birthday
                db.commit()
                print(f"   [OK] Cumpleaños actualizado: {birthday.strftime('%d de %B')}")
                updated_count += 1
            else:
                print(f"   [ERROR] No se pudo parsear el cumpleaños")
                not_found_count += 1

        # Resumen final
        print("\n" + "=" * 70)
        print("RESUMEN:")
        print(f"  Usuarios actualizados: {updated_count}")
        print(f"  Usuarios omitidos (ya tenían cumpleaños): {skipped_count}")
        print(f"  Usuarios no encontrados: {not_found_count}")
        print("=" * 70)

        if updated_count > 0:
            print(f"\n[OK] Se actualizaron {updated_count} cumpleaños exitosamente!")

    except Exception as e:
        print(f"\n[ERROR] Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import_birthdays()
