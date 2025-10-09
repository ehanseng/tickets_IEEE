import qrcode
import hashlib
import secrets
import json
import string
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from io import BytesIO
import base64


class TicketService:
    """Servicio para generación y validación de tickets"""

    def __init__(self, secret_key: str = None):
        # Generar o usar clave secreta para encriptar datos del QR
        if secret_key is None:
            secret_key = Fernet.generate_key()
        elif isinstance(secret_key, str):
            secret_key = secret_key.encode()

        self.cipher = Fernet(secret_key)
        self.qr_directory = Path("qr_codes")
        self.qr_directory.mkdir(exist_ok=True)

    def generate_ticket_code(self, user_id: int, event_id: int) -> str:
        """Genera un código único de ticket"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{user_id}-{event_id}-{timestamp}-{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_unique_url(self) -> str:
        """Genera una URL única usando tokens seguros"""
        return secrets.token_urlsafe(32)

    def generate_pin(self) -> str:
        """Genera un PIN de 6 dígitos"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    def create_qr_data(self, ticket_code: str, user_name: str, event_name: str, event_date: str) -> str:
        """Crea y encripta los datos que irán en el QR"""
        data = {
            "ticket_code": ticket_code,
            "user_name": user_name,
            "event_name": event_name,
            "event_date": event_date,
            "generated_at": datetime.utcnow().isoformat()
        }
        json_data = json.dumps(data)
        encrypted_data = self.cipher.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_qr_data(self, encrypted_data: str) -> dict:
        """Desencripta los datos del QR"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"QR inválido o corrupto: {str(e)}")

    def generate_qr_code(self, ticket_code: str, user_name: str, event_name: str, event_date: str) -> str:
        """Genera la imagen del código QR y retorna la ruta del archivo"""
        # Usar solo el código del ticket (más simple y fácil de escanear)
        # El QR contendrá solo el ticket_code hash SHA-256 (64 caracteres)
        qr_data = ticket_code

        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar imagen
        filename = f"{ticket_code}.png"
        filepath = self.qr_directory / filename
        img.save(filepath)

        return str(filepath)

    def generate_qr_base64(self, ticket_code: str, user_name: str, event_name: str, event_date: str) -> str:
        """Genera el QR como base64 para mostrar en web"""
        # Usar solo el código del ticket (más simple y fácil de escanear)
        qr_data = ticket_code

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"


# Instancia global del servicio
# En producción, usar variable de entorno para la clave
# Generar clave válida para Fernet (32 bytes en base64)
SECRET_KEY = Fernet.generate_key()  # Genera una clave válida automáticamente
ticket_service = TicketService(SECRET_KEY)
