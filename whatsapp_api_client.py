"""
Cliente para WhatsApp Business API (Cloud API de Meta)
Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import requests
import base64
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class WhatsAppAPIClient:
    """Cliente para la API oficial de WhatsApp Business"""

    def __init__(self):
        """Inicializar cliente con credenciales desde .env"""
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v18.0")

        if not all([self.phone_number_id, self.access_token]):
            raise ValueError(
                "Faltan credenciales de WhatsApp API. "
                "Asegúrate de configurar WHATSAPP_PHONE_NUMBER_ID y WHATSAPP_ACCESS_TOKEN en .env"
            )

        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def is_ready(self) -> bool:
        """Verificar si el cliente está configurado correctamente"""
        return bool(self.phone_number_id and self.access_token)

    def send_message(
        self,
        to: str,
        message: str,
        preview_url: bool = True
    ) -> Dict:
        """
        Enviar mensaje de texto

        Args:
            to: Número de teléfono en formato internacional (ej: 573001234567)
            message: Texto del mensaje
            preview_url: Mostrar preview de URLs en el mensaje

        Returns:
            Dict con la respuesta de la API
        """
        # Limpiar número de teléfono (remover + y espacios)
        to = to.replace("+", "").replace(" ", "").replace("-", "")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
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
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Unknown error"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "status_code": response.status_code
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_message_with_image(
        self,
        to: str,
        message: str,
        image_base64: str,
        filename: str = "image.jpg"
    ) -> Dict:
        """
        Enviar mensaje con imagen

        Args:
            to: Número de teléfono en formato internacional
            message: Caption de la imagen
            image_base64: Imagen en base64 (con o sin prefijo data:image/...)
            filename: Nombre del archivo

        Returns:
            Dict con la respuesta de la API
        """
        # Limpiar número de teléfono
        to = to.replace("+", "").replace(" ", "").replace("-", "")

        # Limpiar base64 (remover prefijo si existe)
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]

        try:
            # Paso 1: Subir la imagen a WhatsApp
            media_id = self._upload_media(image_base64, filename)

            if not media_id:
                return {
                    "success": False,
                    "error": "No se pudo subir la imagen a WhatsApp"
                }

            # Paso 2: Enviar mensaje con la imagen
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
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
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "media_id": media_id,
                    "response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Unknown error"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "status_code": response.status_code
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _upload_media(self, image_base64: str, filename: str) -> Optional[str]:
        """
        Subir imagen a WhatsApp Media API

        Args:
            image_base64: Imagen en base64
            filename: Nombre del archivo

        Returns:
            Media ID si se sube exitosamente, None en caso contrario
        """
        try:
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

    def get_media_url(self, media_id: str) -> Optional[str]:
        """
        Obtener URL de un medio previamente subido

        Args:
            media_id: ID del medio

        Returns:
            URL del medio si se obtiene exitosamente
        """
        try:
            response = requests.get(
                f"https://graph.facebook.com/{self.api_version}/{media_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("url")
            else:
                return None

        except Exception as e:
            print(f"[ERROR] Error al obtener URL del medio: {e}")
            return None
