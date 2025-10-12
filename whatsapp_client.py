"""
Cliente Python para comunicarse con el servicio de WhatsApp
"""
import requests
from typing import Optional, List, Dict
from country_codes import format_phone_number


class WhatsAppClient:
    """Cliente para enviar mensajes de WhatsApp"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url

    def get_status(self) -> Dict:
        """Obtiene el estado del servicio de WhatsApp"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "ready": False,
                "error": str(e),
                "message": "No se pudo conectar al servicio de WhatsApp"
            }

    def is_ready(self) -> bool:
        """Verifica si WhatsApp está listo para enviar mensajes"""
        status = self.get_status()
        return status.get("ready", False)

    def send_message(self, phone: str, message: str, country_code: Optional[str] = None) -> Dict:
        """
        Envía un mensaje de WhatsApp

        Args:
            phone: Número de teléfono (puede ser con o sin código de país)
            message: Mensaje a enviar
            country_code: Código de país opcional (ej: "+57")

        Returns:
            Dict con el resultado del envío
        """
        # Si se proporciona country_code, formatear el número completo
        if country_code:
            full_phone = format_phone_number(country_code, phone)
        else:
            full_phone = phone

        try:
            response = requests.post(
                f"{self.base_url}/send",
                json={"phone": full_phone, "message": message},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", "Error desconocido"),
                    "status_code": response.status_code
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    def send_bulk_messages(self, messages: List[Dict]) -> Dict:
        """
        Envía múltiples mensajes de WhatsApp

        Args:
            messages: Lista de diccionarios con formato:
                     [{"phone": "+573001234567", "message": "Hola"}]

        Returns:
            Dict con los resultados del envío masivo
        """
        try:
            response = requests.post(
                f"{self.base_url}/send-bulk",
                json={"messages": messages},
                timeout=300  # 5 minutos para mensajes masivos
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error en envío masivo: {str(e)}"
            }

    def restart(self) -> Dict:
        """Reinicia el cliente de WhatsApp"""
        try:
            response = requests.post(f"{self.base_url}/restart", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error al reiniciar: {str(e)}"
            }


def send_birthday_whatsapp(phone: str, country_code: str, user_name: str) -> bool:
    """
    Envía un mensaje de cumpleaños por WhatsApp

    Args:
        phone: Número de teléfono
        country_code: Código de país (ej: "+57")
        user_name: Nombre del usuario

    Returns:
        True si se envió correctamente, False en caso contrario
    """
    client = WhatsAppClient()

    # Verificar que WhatsApp esté listo
    if not client.is_ready():
        print("[ERROR] WhatsApp no está listo. Verifica el servicio.")
        return False

    # Mensaje de cumpleaños
    message = f"""🎉 ¡Feliz Cumpleaños {user_name}! 🎂

Desde IEEE UTADEO queremos desearte un día lleno de alegría y éxito.

¡Que cumplas muchos más! 🎈✨

---
IEEE Student Branch UTADEO"""

    # Enviar mensaje
    result = client.send_message(phone, message, country_code)

    if result.get("success"):
        print(f"[OK] Mensaje de cumpleaños enviado a {user_name} ({country_code}{phone})")
        return True
    else:
        print(f"[ERROR] No se pudo enviar mensaje a {user_name}: {result.get('error')}")
        return False


def send_ticket_whatsapp(
    phone: str,
    country_code: str,
    user_name: str,
    event_name: str,
    ticket_url: str
) -> bool:
    """
    Envía un mensaje con el ticket de evento por WhatsApp

    Args:
        phone: Número de teléfono
        country_code: Código de país
        user_name: Nombre del usuario
        event_name: Nombre del evento
        ticket_url: URL del ticket

    Returns:
        True si se envió correctamente
    """
    client = WhatsAppClient()

    if not client.is_ready():
        print("[ERROR] WhatsApp no está listo")
        return False

    message = f"""🎟️ ¡Tu Ticket está listo!

Hola {user_name},

Tu registro para *{event_name}* ha sido confirmado.

🔗 Accede a tu ticket aquí:
{ticket_url}

*Importante:*
• Presenta este ticket en el evento
• El código QR será escaneado en la entrada
• Guarda este enlace para acceder cuando lo necesites

¡Nos vemos en el evento! 🎉

---
IEEE Student Branch UTADEO"""

    result = client.send_message(phone, message, country_code)

    if result.get("success"):
        print(f"[OK] Ticket enviado a {user_name}")
        return True
    else:
        print(f"[ERROR] No se pudo enviar ticket: {result.get('error')}")
        return False
