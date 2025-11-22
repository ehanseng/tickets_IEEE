"""
Utilidades para manejo de zona horaria de Bogotá, Colombia (UTC-5)
"""

from datetime import datetime, timedelta
from pytz import timezone

# Zona horaria de Bogotá, Colombia
BOGOTA_TZ = timezone('America/Bogota')


def get_bogota_now() -> datetime:
    """
    Obtiene la fecha y hora actual en zona horaria de Bogotá.

    Returns:
        datetime: Fecha y hora actual en Bogotá (timezone-aware)
    """
    return datetime.now(BOGOTA_TZ)


def get_bogota_now_naive() -> datetime:
    """
    Obtiene la fecha y hora actual en zona horaria de Bogotá sin timezone info.
    Útil para almacenar en base de datos SQLite.

    Returns:
        datetime: Fecha y hora actual en Bogotá (naive datetime)
    """
    return datetime.now(BOGOTA_TZ).replace(tzinfo=None)


def utc_to_bogota(dt_utc: datetime) -> datetime:
    """
    Convierte una fecha UTC a zona horaria de Bogotá.

    Args:
        dt_utc: datetime en UTC

    Returns:
        datetime: datetime en zona horaria de Bogotá
    """
    if dt_utc.tzinfo is None:
        # Asumir que es UTC
        from pytz import utc
        dt_utc = utc.localize(dt_utc)

    return dt_utc.astimezone(BOGOTA_TZ)


def bogota_to_utc(dt_bogota: datetime) -> datetime:
    """
    Convierte una fecha de Bogotá a UTC.

    Args:
        dt_bogota: datetime en zona horaria de Bogotá

    Returns:
        datetime: datetime en UTC
    """
    if dt_bogota.tzinfo is None:
        # Asumir que es Bogotá
        dt_bogota = BOGOTA_TZ.localize(dt_bogota)

    from pytz import utc
    return dt_bogota.astimezone(utc)


def get_date_only_bogota(dt: datetime = None) -> str:
    """
    Obtiene solo la fecha (sin hora) en formato YYYY-MM-DD para Bogotá.
    Útil para comparar días sin importar la hora.

    Args:
        dt: datetime a convertir (si es None, usa la fecha actual de Bogotá)

    Returns:
        str: Fecha en formato YYYY-MM-DD
    """
    if dt is None:
        dt = get_bogota_now()
    elif dt.tzinfo is None:
        # Asumir que ya está en Bogotá
        dt = BOGOTA_TZ.localize(dt)
    else:
        dt = dt.astimezone(BOGOTA_TZ)

    return dt.strftime('%Y-%m-%d')


def format_datetime_bogota(dt: datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Formatea un datetime en zona horaria de Bogotá.

    Args:
        dt: datetime a formatear
        format: string de formato (default: '%Y-%m-%d %H:%M:%S')

    Returns:
        str: Fecha formateada
    """
    if dt.tzinfo is None:
        # Asumir que ya está en Bogotá
        dt_bogota = dt
    else:
        dt_bogota = dt.astimezone(BOGOTA_TZ)

    return dt_bogota.strftime(format)


def is_same_day_bogota(dt1: datetime, dt2: datetime) -> bool:
    """
    Verifica si dos datetimes corresponden al mismo día en zona horaria de Bogotá.

    Args:
        dt1: primer datetime
        dt2: segundo datetime

    Returns:
        bool: True si son el mismo día en Bogotá
    """
    date1 = get_date_only_bogota(dt1)
    date2 = get_date_only_bogota(dt2)
    return date1 == date2


def get_day_start_bogota(dt: datetime = None) -> datetime:
    """
    Obtiene el inicio del día (00:00:00) para una fecha en Bogotá.

    Args:
        dt: datetime (si es None, usa la fecha actual)

    Returns:
        datetime: Inicio del día en Bogotá (naive)
    """
    if dt is None:
        dt = get_bogota_now()
    elif dt.tzinfo is None:
        dt = BOGOTA_TZ.localize(dt)
    else:
        dt = dt.astimezone(BOGOTA_TZ)

    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def get_day_end_bogota(dt: datetime = None) -> datetime:
    """
    Obtiene el fin del día (23:59:59) para una fecha en Bogotá.

    Args:
        dt: datetime (si es None, usa la fecha actual)

    Returns:
        datetime: Fin del día en Bogotá (naive)
    """
    if dt is None:
        dt = get_bogota_now()
    elif dt.tzinfo is None:
        dt = BOGOTA_TZ.localize(dt)
    else:
        dt = dt.astimezone(BOGOTA_TZ)

    return dt.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=None)
