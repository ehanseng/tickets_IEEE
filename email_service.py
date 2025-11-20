"""
Servicio para envío de correos electrónicos usando Resend
"""
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import resend
import base64
import models
from template_service import template_service

# Cargar variables de entorno desde .env
load_dotenv()


class EmailService:
    """Servicio para enviar correos electrónicos usando Resend"""

    def __init__(self):
        # Configuración de Resend
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
        self.from_name = os.getenv("FROM_NAME", "IEEE Tadeo - Control System")

        # Configurar Resend
        if self.api_key:
            resend.api_key = self.api_key
            print(f"[OK] Resend configurado: {self.from_email}")
        else:
            print("[AVISO] RESEND_API_KEY no configurado - Los correos se simularán")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Envía un correo genérico con contenido HTML

        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            text_content: Contenido de texto plano (opcional)

        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        if not self.api_key:
            print("⚠️  RESEND_API_KEY no configurado - El correo NO se enviará")
            print(f"📧 Correo simulado enviado a: {to_email}")
            print(f"📬 Asunto: {subject}")
            return True

        try:
            # Si no hay texto plano, crear uno simple del HTML
            if not text_content:
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)

            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }

            response = resend.Emails.send(params)
            print(f"[OK] Correo enviado exitosamente a {to_email} (ID: {response.get('id', 'N/A')})")
            return True

        except Exception as e:
            print(f"[ERROR] Error al enviar correo: {str(e)}")
            return False

    def send_ticket_email(
        self,
        to_email: str,
        user_name: str,
        event_name: str,
        event_date: datetime,
        event_location: str,
        ticket_code: str,
        ticket_url: str,
        access_pin: str,
        companions: int = 0,
        organization: Optional[models.Organization] = None,
        event: Optional[models.Event] = None
    ) -> bool:
        """
        Envía un correo con la información del ticket usando templates personalizados

        Args:
            to_email: Email del destinatario
            user_name: Nombre del usuario
            event_name: Nombre del evento
            event_date: Fecha del evento
            event_location: Ubicación del evento
            ticket_code: Código del ticket
            ticket_url: URL del ticket
            access_pin: PIN de acceso
            companions: Número de acompañantes
            organization: Organización del evento (None = IEEE Tadeo)
            event: Evento (opcional, para usar template específico del evento)

        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        # Formato de fecha en español
        event_date_str = event_date.strftime('%d de %B de %Y a las %H:%M')

        # Generar asunto usando template service
        subject = template_service.get_email_subject(organization, event_name)

        # Generar contenido HTML usando template service
        html_content = template_service.render_email_template(
            organization=organization,
            user_name=user_name,
            event_name=event_name,
            event_date=event_date_str,
            event_location=event_location,
            ticket_code=ticket_code,
            ticket_url=ticket_url,
            access_pin=access_pin,
            companions=companions,
            event=event
        )

        return self.send_email(to_email, subject, html_content)

    def send_birthday_email(self, to_email: str, user_name: str, nick: Optional[str] = None) -> bool:
        """
        Envía un correo de felicitación de cumpleaños

        Args:
            to_email: Email del destinatario
            user_name: Nombre completo del usuario
            nick: Apodo o nombre corto (opcional, si no se proporciona usa el primer nombre)

        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        # Determinar el nombre a usar: nick, o primer nombre del nombre completo
        display_name = nick if nick else user_name.split()[0]

        subject = f"¡Feliz Cumpleaños {display_name}! 🎉 - IEEE Tadeo"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, Helvetica, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin: 0 auto;">
                <tr>
                    <td>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="background-color: #e91e63; color: #ffffff; padding: 40px 30px; text-align: center;">
                                    <div style="font-size: 60px; margin-bottom: 10px;">🎂</div>
                                    <h1 style="margin: 0; font-size: 28px; font-weight: 600;">¡Feliz Cumpleaños!</h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 30px; text-align: center;">
                                    <div style="font-size: 48px; margin-bottom: 20px;">🎈🎉🎊🎁</div>

                                    <p style="font-size: 22px; color: #333333; margin-bottom: 20px; font-weight: 600;">¡Hola {display_name}!</p>

                                    <p style="font-size: 16px; color: #555555; line-height: 1.8; margin: 20px 0;">
                                        En este día tan especial, todo el equipo de <strong style="color: #e91e63;">IEEE Tadeo</strong>
                                        quiere desearte un <strong>muy feliz cumpleaños</strong>.
                                    </p>

                                    <p style="font-size: 16px; color: #555555; line-height: 1.8; margin: 20px 0;">
                                        Esperamos que este nuevo año de vida esté lleno de alegría, éxito y
                                        grandes experiencias. Gracias por ser parte de nuestra comunidad.
                                    </p>

                                    <p style="font-size: 16px; color: #555555; line-height: 1.8; margin: 20px 0;">
                                        ¡Que este día esté lleno de momentos inolvidables! 🎉
                                    </p>

                                    <div style="font-size: 48px; margin-top: 20px;">🥳🎈🎊</div>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
                                    <p style="margin: 5px 0; font-weight: 600; color: #495057; font-size: 15px;">Con cariño,</p>
                                    <p style="margin: 5px 0; font-weight: 600; color: #495057; font-size: 15px;">El equipo de IEEE Tadeo</p>
                                    <p style="margin-top: 20px; margin-bottom: 5px; color: #6c757d; font-size: 14px;">IEEE Tadeo Control System</p>
                                    <p style="margin: 5px 0;">
                                        <a href="https://ticket.ieeetadeo.org" style="color: #e91e63; text-decoration: none; font-size: 14px;">ticket.ieeetadeo.org</a>
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
¡Feliz Cumpleaños {display_name}! 🎉

En este día tan especial, todo el equipo de IEEE Tadeo quiere desearte un muy feliz cumpleaños.

Esperamos que este nuevo año de vida esté lleno de alegría, éxito y grandes experiencias.
Gracias por ser parte de nuestra comunidad.

¡Que este día esté lleno de momentos inolvidables!

Con cariño,
El equipo de IEEE Tadeo

IEEE Tadeo Control System
https://ticket.ieeetadeo.org
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_bulk_message(
        self,
        to_email: str,
        user_name: str,
        subject: str,
        message: str,
        link: Optional[str] = None,
        link_text: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Envía un mensaje masivo personalizado

        Args:
            to_email: Email del destinatario
            user_name: Nombre del usuario (ya personalizado con nick o primer nombre)
            subject: Asunto del mensaje
            message: Contenido del mensaje
            link: URL opcional para incluir
            link_text: Texto del botón del enlace
            image_url: URL de la imagen opcional (data URL base64)

        Returns:
            bool: True si el correo se envió correctamente
        """
        # Procesar imagen si existe
        image_html = ''
        image_attachment = None

        if image_url and image_url.startswith('data:'):
            # Extraer datos de la imagen
            try:
                header, encoded = image_url.split(',', 1)
                image_data = base64.b64decode(encoded)

                # Usar CID para referenciar la imagen (más compatible con correos universitarios)
                image_html = '<div style="text-align: center; margin: 30px 0;"><img src="cid:bulk_image" alt="Imagen" style="max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto;"/></div>'
                image_attachment = image_data
            except Exception as e:
                print(f"[WARN] No se pudo procesar la imagen: {e}")

        # Link con estilos inline más compatibles
        link_html = f'''
        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
            <tr>
                <td align="center">
                    <a href="{link}" style="display: inline-block; background-color: #0066cc; color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 6px; font-weight: 600; font-size: 16px;">{link_text or "Ver más"}</a>
                </td>
            </tr>
        </table>
        ''' if link else ''

        # HTML con estilos inline (más compatible)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, Helvetica, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin: 0 auto;">
                <tr>
                    <td>
                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="background-color: #667eea; color: #ffffff; padding: 30px; text-align: center;">
                                    <h1 style="margin: 0; font-size: 24px; font-weight: 600;">{subject}</h1>
                                </td>
                            </tr>

                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <p style="font-size: 18px; color: #333333; margin-bottom: 20px;">Hola <strong>{user_name}</strong>,</p>

                                    {image_html}

                                    <div style="font-size: 16px; color: #333333; line-height: 1.8; white-space: pre-wrap; margin: 20px 0;">{message}</div>

                                    {link_html}
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e9ecef;">
                                    <p style="margin: 5px 0; font-weight: 600; color: #6c757d; font-size: 14px;">IEEE Tadeo Student Branch</p>
                                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">Control System</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
{subject}

Hola {user_name},

{message}

{f'Enlace: {link}' if link else ''}

---
IEEE Tadeo Student Branch
Control System
        """

        # Si hay imagen adjunta, usar Resend con attachments
        if image_attachment:
            if not self.api_key:
                print("⚠️  RESEND_API_KEY no configurado - El correo NO se enviará")
                return True

            try:
                import re
                if not text_content:
                    text_content = re.sub('<[^<]+?>', '', html_content)

                # Preparar imagen como adjunto inline
                params = {
                    "from": f"{self.from_name} <{self.from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                    "text": text_content,
                    "attachments": [
                        {
                            "content": base64.b64encode(image_attachment).decode('utf-8'),
                            "filename": "image.jpg",
                            "content_id": "bulk_image",
                            "disposition": "inline"
                        }
                    ]
                }

                response = resend.Emails.send(params)
                print(f"[OK] Correo con imagen enviado exitosamente a {to_email} (ID: {response.get('id', 'N/A')})")
                return True

            except Exception as e:
                print(f"[ERROR] Error al enviar correo con imagen: {str(e)}")
                return False
        else:
            # Sin imagen, usar método normal
            return self.send_email(to_email, subject, html_content, text_content)


# Instancia global del servicio
email_service = EmailService()
