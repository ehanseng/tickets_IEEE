"""
Cliente Python para WhatsApp Business API (Cloud API de Meta)
Migrado desde WPPconnect a la API oficial de Meta
Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import requests
import base64
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from country_codes import format_phone_number
import models
from template_service import template_service

load_dotenv()


class WhatsAppClient:
    """Cliente para la API oficial de WhatsApp Business (Meta Cloud API)"""

    def __init__(self):
        """Inicializar cliente con credenciales desde .env"""
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v18.0")

        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_status(self) -> Dict:
        """Obtiene el estado del servicio de WhatsApp API"""
        if not self.phone_number_id or not self.access_token:
            return {
                "ready": False,
                "error": "Credenciales no configuradas",
                "message": "Configura WHATSAPP_PHONE_NUMBER_ID y WHATSAPP_ACCESS_TOKEN en .env"
            }

        try:
            # Verificar conectividad con la API de Meta
            response = requests.get(
                f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}",
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "ready": True,
                    "phone_number": data.get("display_phone_number", "N/A"),
                    "verified_name": data.get("verified_name", "N/A"),
                    "quality_rating": data.get("quality_rating", "N/A"),
                    "platform_type": data.get("platform_type", "CLOUD_API"),
                    "message": "API de WhatsApp conectada correctamente"
                }
            else:
                error_data = response.json()
                return {
                    "ready": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "message": "Error al conectar con la API de WhatsApp"
                }

        except requests.exceptions.RequestException as e:
            return {
                "ready": False,
                "error": str(e),
                "message": "No se pudo conectar con la API de WhatsApp"
            }

    def is_ready(self) -> bool:
        """Verifica si WhatsApp está listo para enviar mensajes"""
        return bool(self.phone_number_id and self.access_token)

    def send_message(self, phone: str, message: str, country_code: Optional[str] = None) -> Dict:
        """
        Envía un mensaje de texto por WhatsApp

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

        # Limpiar número de teléfono (remover + y espacios)
        full_phone = full_phone.replace("+", "").replace(" ", "").replace("-", "")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": full_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "messageId": result.get("messages", [{}])[0].get("id"),
                    "response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido"),
                    "error_code": error_data.get("error", {}).get("code"),
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
                     [{"phone": "+573054497235", "message": "Hola"}]

        Returns:
            Dict con los resultados del envío masivo
        """
        results = {
            "success": True,
            "sent": 0,
            "failed": 0,
            "errors": []
        }

        for msg in messages:
            result = self.send_message(msg.get("phone"), msg.get("message"))
            if result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "phone": msg.get("phone"),
                    "error": result.get("error")
                })

        if results["failed"] > 0:
            results["success"] = False

        return results

    def restart(self) -> Dict:
        """
        Reinicia el cliente de WhatsApp.
        Nota: La API de Meta no requiere reinicio como WPPconnect.
        Este método verifica la conectividad.
        """
        status = self.get_status()
        if status.get("ready"):
            return {
                "success": True,
                "message": "API de WhatsApp funcionando correctamente"
            }
        else:
            return {
                "success": False,
                "error": status.get("error", "Error al verificar API")
            }

    def logout(self) -> Dict:
        """
        Cierra sesión.
        Nota: La API de Meta no tiene concepto de sesión como WPPconnect.
        Para cambiar credenciales, actualiza el archivo .env
        """
        return {
            "success": True,
            "message": "Para cambiar credenciales, actualiza WHATSAPP_ACCESS_TOKEN en .env"
        }

    def _upload_media(self, image_base64: str, filename: str = "image.jpg") -> Optional[str]:
        """
        Sube una imagen a WhatsApp Media API

        Args:
            image_base64: Imagen en base64 (con o sin prefijo data:image/...)
            filename: Nombre del archivo

        Returns:
            Media ID si se sube exitosamente, None en caso contrario
        """
        try:
            # Limpiar base64 (remover prefijo si existe)
            if "base64," in image_base64:
                image_base64 = image_base64.split("base64,")[1]

            # Decodificar base64 a bytes
            image_bytes = base64.b64decode(image_base64)

            # Determinar tipo MIME basado en extensión
            mime_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                mime_type = "image/png"
            elif filename.lower().endswith(".gif"):
                mime_type = "image/gif"

            # Preparar archivos para upload
            files = {
                "file": (filename, image_bytes, mime_type)
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            data = {
                "messaging_product": "whatsapp",
                "type": mime_type
            }

            response = requests.post(
                f"{self.base_url}/media",
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                media_id = result.get("id")
                print(f"[OK] Imagen subida a WhatsApp. Media ID: {media_id}")
                return media_id
            else:
                error_data = response.json()
                print(f"[ERROR] Error al subir imagen: {error_data}")
                return None

        except Exception as e:
            print(f"[ERROR] Excepción al subir imagen: {e}")
            return None

    def upload_media_for_template(self, image_base64: str, filename: str = "template_header.jpg") -> Dict:
        """
        Sube una imagen para usar como ejemplo en un template header.

        IMPORTANTE: Para templates con header de imagen, Meta requiere:
        1. Subir una imagen de ejemplo usando esta función
        2. Usar el handle devuelto al crear el template
        3. Al enviar mensajes con el template, proporcionar la imagen real

        Args:
            image_base64: Imagen en base64 (con o sin prefijo data:image/...)
            filename: Nombre del archivo

        Returns:
            Dict con success, handle (si exitoso) o error
        """
        try:
            # Limpiar base64
            clean_base64 = image_base64
            if "base64," in image_base64:
                clean_base64 = image_base64.split("base64,")[1]

            # Decodificar
            image_bytes = base64.b64decode(clean_base64)

            # Determinar MIME type
            mime_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                mime_type = "image/png"

            # Método 1: Usar el App ID para Resumable Upload (requerido para templates)
            app_id = os.getenv("META_APP_ID") or os.getenv("FACEBOOK_APP_ID")

            if app_id:
                print(f"[TEMPLATE] Usando Resumable Upload con App ID: {app_id}")
                # Paso 1: Iniciar sesión de upload con App ID
                init_response = requests.post(
                    f"https://graph.facebook.com/{self.api_version}/{app_id}/uploads",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={
                        "file_length": len(image_bytes),
                        "file_type": mime_type,
                        "file_name": filename
                    },
                    timeout=30
                )

                print(f"[TEMPLATE] Init response: {init_response.status_code} - {init_response.text[:200]}")

                if init_response.status_code == 200:
                    upload_session = init_response.json()
                    upload_id = upload_session.get("id")

                    # Paso 2: Subir el archivo
                    upload_response = requests.post(
                        f"https://graph.facebook.com/{self.api_version}/{upload_id}",
                        headers={
                            "Authorization": f"OAuth {self.access_token}",
                            "file_offset": "0"
                        },
                        data=image_bytes,
                        timeout=60
                    )

                    print(f"[TEMPLATE] Upload response: {upload_response.status_code} - {upload_response.text[:200]}")

                    if upload_response.status_code == 200:
                        result = upload_response.json()
                        handle = result.get("h")
                        print(f"[OK] Imagen subida para template. Handle: {handle}")
                        return {"success": True, "handle": handle, "method": "resumable"}

            # Método 2: Usar Media API estándar y construir el handle
            print(f"[TEMPLATE] Intentando Media API estándar...")
            media_id = self._upload_media(image_base64, filename)
            if media_id:
                print(f"[OK] Imagen subida via Media API. ID: {media_id}")
                return {"success": True, "handle": media_id, "method": "media_api"}

            return {"success": False, "error": "No se pudo subir la imagen con ningún método"}

        except Exception as e:
            print(f"[ERROR] upload_media_for_template: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def send_message_with_image(self, phone: str, message: str, image_base64: str, country_code: Optional[str] = None) -> Dict:
        """
        Envía un mensaje de WhatsApp con una imagen adjunta

        Args:
            phone: Número de teléfono (puede ser con o sin código de país)
            message: Caption de la imagen
            image_base64: Imagen en formato base64 data URL (ej: "data:image/png;base64,...")
            country_code: Código de país opcional (ej: "+57")

        Returns:
            Dict con el resultado del envío
        """
        # Si se proporciona country_code, formatear el número completo
        if country_code:
            full_phone = format_phone_number(country_code, phone)
        else:
            full_phone = phone

        # Limpiar número de teléfono
        full_phone = full_phone.replace("+", "").replace(" ", "").replace("-", "")

        try:
            # Paso 1: Subir la imagen a WhatsApp
            media_id = self._upload_media(image_base64)

            if not media_id:
                return {
                    "success": False,
                    "error": "No se pudo subir la imagen a WhatsApp"
                }

            # Paso 2: Enviar mensaje con la imagen
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": full_phone,
                "type": "image",
                "image": {
                    "id": media_id,
                    "caption": message
                }
            }

            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "messageId": result.get("messages", [{}])[0].get("id"),
                    "media_id": media_id,
                    "response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "status_code": response.status_code
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    # ============================================
    # Template Management Methods
    # ============================================

    def get_templates(self) -> Dict:
        """
        Obtiene todos los templates de la cuenta de WhatsApp Business

        Returns:
            Dict con la lista de templates
        """
        try:
            response = requests.get(
                f"https://graph.facebook.com/{self.api_version}/{self.business_account_id}/message_templates",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "templates": response.json().get("data", [])
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    def create_template(
        self,
        name: str,
        category: str,
        language: str,
        body_text: str,
        header_type: Optional[str] = None,
        header_text: Optional[str] = None,
        header_image_handle: Optional[str] = None,
        footer_text: Optional[str] = None,
        variable_examples: Optional[List[str]] = None
    ) -> Dict:
        """
        Crea un nuevo template en Meta para aprobación

        Args:
            name: Nombre del template (minúsculas, sin espacios)
            category: UTILITY, MARKETING, AUTHENTICATION
            language: Código de idioma (es, en, etc.)
            body_text: Texto del cuerpo con variables {{1}}, {{2}}, etc.
            header_type: TEXT, IMAGE, VIDEO, DOCUMENT (opcional)
            header_text: Texto del header si header_type es TEXT
            header_image_handle: Handle de imagen (de upload_media_for_template) si header_type es IMAGE
            footer_text: Texto del footer (opcional)
            variable_examples: Lista de ejemplos para las variables

        Returns:
            Dict con el resultado
        """
        # Construir componentes
        components = []

        # Header (opcional)
        if header_type == "TEXT" and header_text:
            header_component = {"type": "HEADER", "format": "TEXT", "text": header_text}
            components.append(header_component)
        elif header_type == "IMAGE":
            # Header de imagen - Meta requiere un header_handle de Resumable Upload API
            header_component = {
                "type": "HEADER",
                "format": "IMAGE",
            }
            if header_image_handle:
                # Usar header_handle (del Resumable Upload API)
                # El handle tiene formato: "4:filename:mimetype:signature..."
                header_component["example"] = {
                    "header_handle": [header_image_handle]
                }
                print(f"[TEMPLATE] Usando header_handle: {header_image_handle[:50]}...")
            else:
                # Sin imagen de ejemplo - esto puede causar error
                # Se recomienda siempre proporcionar una imagen
                print("[TEMPLATE] WARNING: No se proporcionó imagen de ejemplo para header IMAGE")
                # Intentar sin ejemplo (puede fallar)
                pass
            components.append(header_component)

        # Body (requerido)
        body_component = {"type": "BODY", "text": body_text}
        if variable_examples:
            body_component["example"] = {"body_text": [variable_examples]}
        components.append(body_component)

        # Footer (opcional)
        if footer_text:
            components.append({"type": "FOOTER", "text": footer_text})

        payload = {
            "name": name,
            "category": category,
            "language": language,
            "components": components
        }

        # Log payload for debugging
        import json
        print(f"[TEMPLATE] Creating template with payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        try:
            response = requests.post(
                f"https://graph.facebook.com/{self.api_version}/{self.business_account_id}/message_templates",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            print(f"[TEMPLATE] Response status: {response.status_code}")
            print(f"[TEMPLATE] Response body: {response.text[:500]}")

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "template_id": result.get("id"),
                    "status": result.get("status", "PENDING"),
                    "response": result
                }
            else:
                error_data = response.json()
                error_info = error_data.get("error", {})
                return {
                    "success": False,
                    "error": error_info.get("message", "Error desconocido"),
                    "error_code": error_info.get("code"),
                    "error_subcode": error_info.get("error_subcode"),
                    "error_user_title": error_info.get("error_user_title"),
                    "error_user_msg": error_info.get("error_user_msg"),
                    "fbtrace_id": error_info.get("fbtrace_id"),
                    "full_error": error_data
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    def delete_template(self, template_name: str) -> Dict:
        """
        Elimina un template de Meta

        Args:
            template_name: Nombre del template a eliminar

        Returns:
            Dict con el resultado
        """
        try:
            response = requests.delete(
                f"https://graph.facebook.com/{self.api_version}/{self.business_account_id}/message_templates",
                headers=self.headers,
                params={"name": template_name},
                timeout=30
            )

            if response.status_code == 200:
                return {"success": True, "message": f"Template '{template_name}' eliminado"}
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    def send_template_message(
        self,
        phone: str,
        template_name: str,
        language: str = "es",
        variables: Optional[List[str]] = None,
        country_code: Optional[str] = None
    ) -> Dict:
        """
        Envía un mensaje usando un template aprobado

        Args:
            phone: Número de teléfono
            template_name: Nombre del template
            language: Código de idioma
            variables: Lista de valores para las variables del template
            country_code: Código de país opcional

        Returns:
            Dict con el resultado
        """
        if country_code:
            full_phone = format_phone_number(country_code, phone)
        else:
            full_phone = phone

        full_phone = full_phone.replace("+", "").replace(" ", "").replace("-", "")

        payload = {
            "messaging_product": "whatsapp",
            "to": full_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language}
            }
        }

        # Agregar variables si existen
        if variables:
            payload["template"]["components"] = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": var} for var in variables
                    ]
                }
            ]

        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "messageId": result.get("messages", [{}])[0].get("id"),
                    "response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido"),
                    "error_code": error_data.get("error", {}).get("code")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }

    def download_media(self, media_id: str) -> Dict:
        """
        Descarga un archivo de media de WhatsApp

        Args:
            media_id: ID del media a descargar

        Returns:
            Dict con la URL y datos del media
        """
        try:
            # Primero obtener la URL del media
            response = requests.get(
                f"https://graph.facebook.com/{self.api_version}/{media_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                media_info = response.json()
                media_url = media_info.get("url")

                # Descargar el archivo
                if media_url:
                    download_response = requests.get(
                        media_url,
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        timeout=60
                    )

                    if download_response.status_code == 200:
                        return {
                            "success": True,
                            "url": media_url,
                            "mime_type": media_info.get("mime_type"),
                            "sha256": media_info.get("sha256"),
                            "file_size": media_info.get("file_size"),
                            "data": download_response.content
                        }

                return {
                    "success": True,
                    "url": media_url,
                    "mime_type": media_info.get("mime_type"),
                    "response": media_info
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Error desconocido")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}"
            }


def send_birthday_whatsapp(phone: str, country_code: str, user_name: str, nick: Optional[str] = None) -> bool:
    """
    Envía un mensaje de cumpleaños por WhatsApp

    Args:
        phone: Número de teléfono
        country_code: Código de país (ej: "+57")
        user_name: Nombre completo del usuario
        nick: Apodo o nombre corto (opcional, si no se proporciona usa el primer nombre)

    Returns:
        True si se envió correctamente, False en caso contrario
    """
    client = WhatsAppClient()

    # Verificar que WhatsApp esté listo
    if not client.is_ready():
        print("[ERROR] WhatsApp no esta listo. Verifica el servicio.")
        return False

    # Determinar el nombre a usar: nick, o primer nombre del nombre completo
    display_name = nick if nick else user_name.split()[0]

    # Mensaje de cumpleaños
    message = f"""🎉 ¡Feliz Cumpleaños {display_name}! 🎂

Desde IEEE Tadeo queremos desearte un día lleno de alegría y éxito.

¡Que cumplas muchos más! 🎈✨

---
IEEE Tadeo Student Branch"""

    # Enviar mensaje
    result = client.send_message(phone, message, country_code)

    if result.get("success"):
        print(f"[OK] Mensaje de cumpleanos enviado a {user_name} ({country_code}{phone})")
        return True
    else:
        print(f"[ERROR] No se pudo enviar mensaje a {user_name}: {result.get('error')}")
        return False


def send_ticket_whatsapp(
    phone: str,
    country_code: str,
    user_name: str,
    event_name: str,
    event_location: str,
    event_date: str,
    ticket_code: str,
    ticket_url: str,
    access_pin: str,
    companions: int = 0,
    organization: Optional[models.Organization] = None,
    event: Optional[models.Event] = None
) -> bool:
    """
    Envía un mensaje con el ticket de evento por WhatsApp usando templates personalizados

    Args:
        phone: Número de teléfono
        country_code: Código de país
        user_name: Nombre del usuario
        event_name: Nombre del evento
        event_location: Ubicación del evento
        event_date: Fecha y hora del evento (formateada)
        ticket_code: Código del ticket
        ticket_url: URL del ticket
        access_pin: PIN de acceso al ticket
        companions: Número de acompañantes
        organization: Organización del evento (None = IEEE Tadeo)
        event: Evento (opcional, para usar template específico del evento)

    Returns:
        True si se envió correctamente
    """
    client = WhatsAppClient()

    if not client.is_ready():
        print("[ERROR] WhatsApp no esta listo")
        return False

    # Generar mensaje usando template service
    message = template_service.render_whatsapp_template(
        organization=organization,
        user_name=user_name,
        event_name=event_name,
        event_date=event_date,
        event_location=event_location,
        ticket_code=ticket_code,
        ticket_url=ticket_url,
        access_pin=access_pin,
        companions=companions,
        event=event
    )

    # Preparar QR si está habilitado
    qr_base64 = None
    if event and hasattr(event, 'send_qr_with_whatsapp') and event.send_qr_with_whatsapp:
        try:
            from ticket_service import ticket_service
            qr_base64 = ticket_service.generate_qr_base64(
                ticket_code=ticket_code,
                user_name=user_name,
                event_name=event_name,
                event_date=event_date
            )
            print(f"[INFO] QR code generado para envío")
        except Exception as e:
            print(f"[WARNING] No se pudo generar el QR: {e}")

    # Preparar imagen promocional si existe
    promo_image = None
    if event and hasattr(event, 'whatsapp_image_path') and event.whatsapp_image_path:
        import os
        import base64
        if os.path.exists(event.whatsapp_image_path):
            try:
                with open(event.whatsapp_image_path, 'rb') as f:
                    image_data = f.read()
                    ext = os.path.splitext(event.whatsapp_image_path)[1].lower()
                    mime_types = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif'
                    }
                    mime_type = mime_types.get(ext, 'image/jpeg')
                    promo_image = f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}"
                    print(f"[INFO] Imagen promocional cargada")
            except Exception as e:
                print(f"[WARNING] No se pudo cargar la imagen del evento: {e}")

    # Nueva lógica: Mensaje de texto con QR (si está habilitado), luego banner promocional
    import time

    result = None

    # 1. Enviar mensaje principal: texto + QR (si está habilitado)
    if qr_base64:
        # Enviar mensaje de texto con el QR como imagen
        max_retries = 2
        msg_sent = False

        for attempt in range(max_retries):
            msg_result = client.send_message_with_image(phone, message, qr_base64, country_code)
            if msg_result.get("success"):
                print(f"[OK] Mensaje de texto con QR enviado a {user_name}")
                msg_sent = True
                result = msg_result
                break
            else:
                print(f"[WARNING] Intento {attempt + 1}/{max_retries} fallido al enviar mensaje con QR: {msg_result.get('error')}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Esperar antes de reintentar

        if not msg_sent:
            print(f"[ERROR] No se pudo enviar el mensaje con QR después de {max_retries} intentos, enviando solo texto")
            # Fallback: enviar solo texto sin QR
            result = client.send_message(phone, message, country_code)
            if result.get("success"):
                print(f"[OK] Mensaje de texto enviado (sin QR) a {user_name}")
            else:
                print(f"[ERROR] No se pudo enviar ni siquiera el mensaje de texto")
                return False
    else:
        # Si no hay QR habilitado, enviar solo mensaje de texto
        result = client.send_message(phone, message, country_code)
        if result.get("success"):
            print(f"[OK] Mensaje de texto enviado a {user_name}")
        else:
            print(f"[ERROR] No se pudo enviar el mensaje de texto: {result.get('error')}")
            return False

    # 2. Si hay imagen promocional, enviarla después (opcional)
    if promo_image:
        time.sleep(3)  # Esperar 3 segundos antes de enviar el banner

        banner_result = client.send_message_with_image(phone, "📢 *Información del evento:*", promo_image, country_code)
        if banner_result.get("success"):
            print(f"[OK] Banner promocional enviado a {user_name}")
        else:
            print(f"[WARNING] No se pudo enviar el banner promocional (pero el mensaje principal sí llegó): {banner_result.get('error')}")
            # No retornamos False porque el mensaje principal ya se envió

    return True


def send_bulk_whatsapp(
    phone: str,
    country_code: str,
    user_name: str,
    subject: str,
    message: str,
    link: Optional[str] = None,
    image_base64: Optional[str] = None
) -> Dict:
    """
    Envía un mensaje masivo personalizado por WhatsApp

    Args:
        phone: Número de teléfono
        country_code: Código de país (ej: "+57")
        user_name: Nombre del usuario (ya personalizado con nick o primer nombre)
        subject: Asunto/título del mensaje
        message: Contenido del mensaje
        link: URL opcional para incluir
        image_base64: Imagen en formato base64 data URL (opcional)

    Returns:
        Dict con el resultado: {"success": bool, "message_id": str, "error": str}
    """
    client = WhatsAppClient()

    if not client.is_ready():
        print("[ERROR] WhatsApp no esta listo")
        return {"success": False, "error": "WhatsApp no esta listo"}

    # Construir mensaje de WhatsApp
    wa_message = f"""*{subject}*

Hola {user_name},

{message}"""

    if link:
        wa_message += f"\n\n🔗 {link}"

    wa_message += "\n\n---\nIEEE Tadeo Student Branch"

    # Si hay imagen, usar el endpoint /send-media
    if image_base64:
        full_phone = format_phone_number(country_code, phone)

        try:
            response = requests.post(
                f"{client.base_url}/send-media",
                json={
                    "phone": full_phone,
                    "message": wa_message,
                    "imageBase64": image_base64
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    message_id = result.get("messageId")
                    print(f"[OK] Mensaje con imagen enviado a {user_name} ({country_code}{phone})")
                    if "imageCompression" in result:
                        print(f"     Compresion: {result['imageCompression']['originalSize']} -> {result['imageCompression']['compressedSize']}")
                    return {"success": True, "message_id": message_id}
                else:
                    error_msg = result.get('error', 'Error desconocido')
                    print(f"[ERROR] No se pudo enviar mensaje con imagen a {user_name}: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', 'Error desconocido')
                print(f"[ERROR] No se pudo enviar mensaje con imagen a {user_name}: {error_msg}")
                return {"success": False, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            print(f"[ERROR] {error_msg} al enviar imagen a {user_name}")
            return {"success": False, "error": error_msg}

    # Si no hay imagen, usar el método normal
    result = client.send_message(phone, wa_message, country_code)

    if result.get("success"):
        message_id = result.get("messageId")
        print(f"[OK] Mensaje masivo enviado a {user_name} ({country_code}{phone})")
        return {"success": True, "message_id": message_id}
    else:
        error_msg = result.get('error', 'Error desconocido')
        print(f"[ERROR] No se pudo enviar mensaje a {user_name}: {error_msg}")
        return {"success": False, "error": error_msg}
