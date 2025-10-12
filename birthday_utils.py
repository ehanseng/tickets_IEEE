"""
Utilidades para manejo de cumpleaños
"""
from datetime import datetime, date
from typing import Optional


def calculate_days_until_birthday(birthday: Optional[datetime]) -> Optional[int]:
    """
    Calcula los días que faltan hasta el próximo cumpleaños.

    Args:
        birthday: Fecha de cumpleaños del usuario (puede ser solo mes/día o con año)

    Returns:
        int: Número de días hasta el próximo cumpleaños, o None si no hay cumpleaños

    Ejemplos:
        - Si hoy es 10 de octubre y el cumpleaños es 15 de octubre: retorna 5
        - Si hoy es 10 de octubre y el cumpleaños es 5 de enero: retorna días hasta 5 de enero del próximo año
        - Si hoy es el cumpleaños: retorna 0
    """
    if not birthday:
        return None

    today = date.today()

    # Crear fecha del cumpleaños para este año
    birthday_this_year = date(today.year, birthday.month, birthday.day)

    # Si el cumpleaños ya pasó este año, calcular para el próximo año
    if birthday_this_year < today:
        birthday_next = date(today.year + 1, birthday.month, birthday.day)
    else:
        birthday_next = birthday_this_year

    # Calcular diferencia en días
    days_until = (birthday_next - today).days

    return days_until


def get_birthday_status(birthday: Optional[datetime]) -> dict:
    """
    Obtiene el estado completo del cumpleaños de un usuario.

    Args:
        birthday: Fecha de cumpleaños del usuario

    Returns:
        dict: Diccionario con información del cumpleaños:
            - days_until: Días hasta el cumpleaños
            - is_today: Si es hoy
            - is_this_week: Si es esta semana (próximos 7 días)
            - is_this_month: Si es este mes
            - date_str: Fecha formateada (ej: "15 de octubre")
    """
    if not birthday:
        return {
            "days_until": None,
            "is_today": False,
            "is_this_week": False,
            "is_this_month": False,
            "date_str": None
        }

    days_until = calculate_days_until_birthday(birthday)

    # Formatear fecha en español
    months_es = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    date_str = f"{birthday.day} de {months_es[birthday.month - 1]}"

    return {
        "days_until": days_until,
        "is_today": days_until == 0,
        "is_this_week": days_until is not None and 0 <= days_until <= 7,
        "is_this_month": days_until is not None and 0 <= days_until <= 30,
        "date_str": date_str
    }
