"""
Servicio para envío de correos electrónicos
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class EmailService:
    """Servicio para enviar correos electrónicos"""

    def __init__(self):
        # Configuración SMTP (usar variables de entorno en producción)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "IEEE Tadeo - Sistema de Tickets")

        # Mostrar configuración en desarrollo (sin mostrar contraseña)
        if self.smtp_user:
            print(f"OK - SMTP configurado: {self.smtp_user} via {self.smtp_host}:{self.smtp_port}")
        else:
            print("AVISO - SMTP no configurado - Los correos se simularan")

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
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email

            # Si no hay texto plano, crear uno simple del HTML
            if not text_content:
                # Crear versión simple quitando etiquetas HTML básicas
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)

            # Adjuntar partes
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')

            msg.attach(part1)
            msg.attach(part2)

            # Enviar correo
            if not self.smtp_user or not self.smtp_password:
                print("⚠️  SMTP no configurado - El correo NO se enviará")
                print(f"📧 Correo simulado enviado a: {to_email}")
                print(f"📬 Asunto: {subject}")
                return True  # Retornar True en desarrollo para no bloquear

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"[OK] Correo enviado exitosamente a {to_email}")
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
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Tu Ticket para {event_name} - IEEE Tadeo'
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email

            # Formato de fecha
            event_date_str = event_date.strftime('%d de %B de %Y a las %H:%M')

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

            # Adjuntar partes
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')

            msg.attach(part1)
            msg.attach(part2)

            # Enviar correo
            if not self.smtp_user or not self.smtp_password:
                print("⚠️  SMTP no configurado - El correo NO se enviará")
                print(f"📧 Correo simulado enviado a: {to_email}")
                print(f"🔑 PIN: {access_pin}")
                print(f"🔗 URL: {ticket_url}")
                return True  # Retornar True en desarrollo para no bloquear

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"[OK] Correo enviado exitosamente a {to_email}")
            return True

        except Exception as e:
            print(f"[ERROR] Error al enviar correo: {str(e)}")
            # En desarrollo, imprimir la información pero no fallar
            print(f"📧 Información del ticket:")
            print(f"   Email: {to_email}")
            print(f"   PIN: {access_pin}")
            print(f"   URL: {ticket_url}")
            return False

    def send_birthday_email(self, to_email: str, user_name: str) -> bool:
        """
        Envía un correo de felicitación de cumpleaños

        Args:
            to_email: Email del destinatario
            user_name: Nombre del usuario

        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        subject = f"¡Feliz Cumpleaños {user_name}! 🎉 - IEEE Tadeo"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 32px;
                    font-weight: 700;
                }}
                .emoji {{
                    font-size: 60px;
                    margin: 20px 0;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .greeting {{
                    font-size: 24px;
                    color: #333;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}
                .message {{
                    font-size: 16px;
                    color: #666;
                    line-height: 1.8;
                    margin: 20px 0;
                }}
                .highlight {{
                    color: #667eea;
                    font-weight: 600;
                }}
                .balloons {{
                    font-size: 48px;
                    margin: 20px 0;
                    animation: float 3s ease-in-out infinite;
                }}
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0px); }}
                    50% {{ transform: translateY(-20px); }}
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 5px 0;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .signature {{
                    margin-top: 20px;
                    font-weight: 600;
                    color: #495057;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="emoji">🎂</div>
                    <h1>¡Feliz Cumpleaños!</h1>
                </div>

                <div class="content">
                    <div class="balloons">🎈🎉🎊🎁</div>

                    <p class="greeting">¡Hola {user_name}!</p>

                    <p class="message">
                        En este día tan especial, todo el equipo de <span class="highlight">IEEE Tadeo</span>
                        quiere desearte un <strong>muy feliz cumpleaños</strong>.
                    </p>

                    <p class="message">
                        Esperamos que este nuevo año de vida esté lleno de alegría, éxito y
                        grandes experiencias. Gracias por ser parte de nuestra comunidad.
                    </p>

                    <p class="message">
                        ¡Que este día esté lleno de momentos inolvidables! 🎉
                    </p>

                    <div class="balloons">🥳🎈🎊</div>
                </div>

                <div class="footer">
                    <p class="signature">Con cariño,</p>
                    <p class="signature">El equipo de IEEE Tadeo</p>
                    <p style="margin-top: 20px;">
                        Sistema de Tickets - IEEE Tadeo<br>
                        <a href="https://ticket.ieeetadeo.org" style="color: #667eea;">ticket.ieeetadeo.org</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
¡Feliz Cumpleaños {user_name}! 🎉

En este día tan especial, todo el equipo de IEEE Tadeo quiere desearte un muy feliz cumpleaños.

Esperamos que este nuevo año de vida esté lleno de alegría, éxito y grandes experiencias.
Gracias por ser parte de nuestra comunidad.

¡Que este día esté lleno de momentos inolvidables!

Con cariño,
El equipo de IEEE Tadeo

Sistema de Tickets - IEEE Tadeo
https://ticket.ieeetadeo.org
        """

        return self.send_email(to_email, subject, html_content, text_content)


# Instancia global del servicio
email_service = EmailService()
