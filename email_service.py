"""
Servicio para envío de correos electrónicos usando Resend
"""
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import resend
import base64

# Cargar variables de entorno desde .env
load_dotenv()


class EmailService:
    """Servicio para enviar correos electrónicos usando Resend"""

    def __init__(self):
        # Configuración de Resend
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
        self.from_name = os.getenv("FROM_NAME", "IEEE Tadeo - Sistema de Tickets")

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
        event_description: str,
        ticket_url: str,
        access_pin: str,
        companions: int
    ) -> bool:
        """
        Envía un correo con la información del ticket y el PIN de acceso

        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        # Formato de fecha
        event_date_str = event_date.strftime('%d de %B de %Y a las %H:%M')

        subject = f'Tu Ticket para {event_name} - IEEE Tadeo'

        # Crear contenido HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #0066cc;
            margin: 0;
            font-size: 28px;
        }}
        .pin-box {{
            background-color: #f0f7ff;
            border: 2px solid #0066cc;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }}
        .pin-code {{
            font-size: 36px;
            font-weight: bold;
            color: #0066cc;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .info-section {{
            margin: 25px 0;
        }}
        .info-section h2 {{
            color: #0066cc;
            font-size: 18px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .info-label {{
            font-weight: 600;
            color: #666;
        }}
        .info-value {{
            color: #333;
        }}
        .btn {{
            display: inline-block;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            padding: 15px 40px;
            border-radius: 6px;
            font-weight: 600;
            text-align: center;
            margin: 20px 0;
        }}
        .btn:hover {{
            background-color: #0052a3;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 14px;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎟️ Tu Ticket IEEE Tadeo</h1>
            <p style="color: #666; margin: 10px 0 0 0;">Confirmación de Registro</p>
        </div>

        <p>Hola <strong>{user_name}</strong>,</p>
        <p>¡Gracias por registrarte! Tu ticket para el evento ha sido generado exitosamente.</p>

        <div class="info-section">
            <h2>📅 Información del Evento</h2>
            <div class="info-row">
                <span class="info-label">Evento:</span>
                <span class="info-value">{event_name}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Fecha:</span>
                <span class="info-value">{event_date_str}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Ubicación:</span>
                <span class="info-value">{event_location}</span>
            </div>
            {f'<div class="info-row"><span class="info-label">Acompañantes:</span><span class="info-value">{companions}</span></div>' if companions > 0 else ''}
        </div>

        <div class="pin-box">
            <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">Tu PIN de Acceso</p>
            <div class="pin-code">{access_pin}</div>
            <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">Guarda este PIN, lo necesitarás para acceder a tu ticket</p>
        </div>

        <div style="text-align: center;">
            <a href="{ticket_url}" class="btn">Ver Mi Ticket</a>
        </div>

        <div class="warning">
            <strong>⚠️ Importante:</strong>
            <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                <li>Guarda este correo en un lugar seguro</li>
                <li>No compartas tu PIN con nadie</li>
                <li>Presenta el código QR en la entrada del evento</li>
                <li>Llega con 15 minutos de anticipación</li>
            </ul>
        </div>

        {f'<div class="info-section"><h2>ℹ️ Sobre el Evento</h2><p>{event_description}</p></div>' if event_description else ''}

        <div class="footer">
            <p>Este correo fue generado automáticamente por el Sistema de Tickets IEEE Tadeo.</p>
            <p>Si tienes alguna pregunta, contacta al organizador del evento.</p>
        </div>
    </div>
</body>
</html>
        """

        # Crear versión texto plano
        text_content = f"""
Tu Ticket IEEE Tadeo - {event_name}

Hola {user_name},

¡Gracias por registrarte! Tu ticket para el evento ha sido generado exitosamente.

INFORMACIÓN DEL EVENTO:
- Evento: {event_name}
- Fecha: {event_date_str}
- Ubicación: {event_location}
{f'- Acompañantes: {companions}' if companions > 0 else ''}

TU PIN DE ACCESO: {access_pin}

Para ver tu ticket y código QR, accede al siguiente enlace:
{ticket_url}

IMPORTANTE:
- Guarda este correo en un lugar seguro
- No compartas tu PIN con nadie
- Presenta el código QR en la entrada del evento
- Llega con 15 minutos de anticipación

{f'SOBRE EL EVENTO:\\n{event_description}\\n' if event_description else ''}

---
Este correo fue generado automáticamente por el Sistema de Tickets IEEE Tadeo.
        """

        return self.send_email(to_email, subject, html_content, text_content)

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
                                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">Sistema de Tickets</p>
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
Sistema de Tickets
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
