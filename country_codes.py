# -*- coding: utf-8 -*-
"""
Códigos de país para números telefónicos
"""

COUNTRY_CODES = [
    {"code": "+57", "name": "Colombia", "flag": "🇨🇴"},
    {"code": "+1", "name": "Estados Unidos/Canadá", "flag": "🇺🇸"},
    {"code": "+52", "name": "México", "flag": "🇲🇽"},
    {"code": "+54", "name": "Argentina", "flag": "🇦🇷"},
    {"code": "+55", "name": "Brasil", "flag": "🇧🇷"},
    {"code": "+56", "name": "Chile", "flag": "🇨🇱"},
    {"code": "+51", "name": "Perú", "flag": "🇵🇪"},
    {"code": "+58", "name": "Venezuela", "flag": "🇻🇪"},
    {"code": "+593", "name": "Ecuador", "flag": "🇪🇨"},
    {"code": "+591", "name": "Bolivia", "flag": "🇧🇴"},
    {"code": "+595", "name": "Paraguay", "flag": "🇵🇾"},
    {"code": "+598", "name": "Uruguay", "flag": "🇺🇾"},
    {"code": "+507", "name": "Panamá", "flag": "🇵🇦"},
    {"code": "+506", "name": "Costa Rica", "flag": "🇨🇷"},
    {"code": "+503", "name": "El Salvador", "flag": "🇸🇻"},
    {"code": "+502", "name": "Guatemala", "flag": "🇬🇹"},
    {"code": "+504", "name": "Honduras", "flag": "🇭🇳"},
    {"code": "+505", "name": "Nicaragua", "flag": "🇳🇮"},
    {"code": "+53", "name": "Cuba", "flag": "🇨🇺"},
    {"code": "+34", "name": "España", "flag": "🇪🇸"},
    {"code": "+44", "name": "Reino Unido", "flag": "🇬🇧"},
    {"code": "+33", "name": "Francia", "flag": "🇫🇷"},
    {"code": "+49", "name": "Alemania", "flag": "🇩🇪"},
    {"code": "+39", "name": "Italia", "flag": "🇮🇹"},
]

# Colombia por defecto
DEFAULT_COUNTRY_CODE = "+57"

def get_country_name(code: str) -> str:
    """Obtiene el nombre del país dado un código"""
    for country in COUNTRY_CODES:
        if country["code"] == code:
            return country["name"]
    return "Desconocido"

def format_phone_number(country_code: str, phone: str) -> str:
    """Formatea un número telefónico completo"""
    if not phone:
        return ""
    # Remover espacios y caracteres especiales del teléfono
    phone_clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return f"{country_code}{phone_clean}"
