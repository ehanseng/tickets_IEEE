"""
Servicio de templates personalizables para organizaciones
"""
from typing import Optional, Dict
from datetime import datetime
import models


class TemplateService:
    """Servicio para generar templates personalizados por organización"""

    # Template predeterminado de IEEE Tadeo para email
    DEFAULT_EMAIL_TEMPLATE = """
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
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        .ticket-code {{
            font-size: 20px;
            font-weight: bold;
            color: #0066cc;
            letter-spacing: 2px;
            font-family: 'Courier New', monospace;
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-all;
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
        .info-item {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .info-item strong {{
            color: #0066cc;
        }}
        .button {{
            display: inline-block;
            padding: 15px 30px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .note {{
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
            <h1>🎟️ Tu Ticket está Listo</h1>
        </div>

        <p style="font-size: 16px;">Hola <strong>{user_name}</strong>,</p>

        <p>Tu registro para el evento ha sido confirmado exitosamente.</p>

        <div class="info-section">
            <h2>📋 Información del Evento</h2>
            <div class="info-item"><strong>Evento:</strong> {event_name}</div>
            <div class="info-item"><strong>Fecha y Hora:</strong> {event_date}</div>
            <div class="info-item"><strong>Ubicación:</strong> {event_location}</div>
            {companions_info}
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <img src="{qr_base64}" alt="Código QR del Ticket" style="max-width: 250px; border: 3px solid #0066cc; border-radius: 8px; margin: 20px auto; display: block;">
            <p style="color: #666; font-size: 14px; margin-top: 10px;">Presenta este código QR en la entrada del evento</p>
        </div>

        <div class="pin-box">
            <p style="margin: 0 0 10px 0; color: #666;">Tu PIN de acceso es:</p>
            <div class="pin-code">{access_pin}</div>
            <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Guarda este PIN, lo necesitarás para acceder a tu ticket</p>
        </div>

        <div style="text-align: center;">
            <a href="{ticket_url}" class="button">Ver Mi Ticket Completo</a>
        </div>

        <div class="note">
            <strong>⚠️ Importante:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>Presenta este ticket en el evento</li>
                <li>El código QR será escaneado en la entrada</li>
                <li>Llega con anticipación para evitar congestiones</li>
            </ul>
        </div>

        <div class="footer">
            <p>IEEE Tadeo Student Branch</p>
            <p><a href="https://ticket.ieeetadeo.org">ticket.ieeetadeo.org</a></p>
        </div>
    </div>
</body>
</html>
"""

    # Template predeterminado de IEEE Tadeo para WhatsApp
    DEFAULT_WHATSAPP_TEMPLATE = """🎟️ *¡Tu Ticket está listo!*

Hola *{user_name}*,

Tu registro para el evento ha sido confirmado.

📋 *INFORMACIÓN DEL EVENTO*
━━━━━━━━━━━━━━━━━━━
🎯 *Evento:* {event_name}
📍 *Lugar:* {event_location}
📅 *Fecha y Hora:* {event_date}

🎫 *INFORMACIÓN DEL TICKET*
━━━━━━━━━━━━━━━━━━━
👤 *Titular:* {user_name}
🔢 *Código:* {ticket_code}
🔐 *PIN de acceso:* {access_pin}{companions_text}

✅ *TICKET VÁLIDO*
Este ticket es válido para el ingreso al evento. El código QR será escaneado en la entrada.

🔗 *Accede a tu ticket web aquí:*
{ticket_url}

🌐 *Portal de usuarios:*
https://ticket.ieeetadeo.org/portal/login

*IMPORTANTE:*
• Presenta este ticket en el evento
• El código QR será escaneado en la entrada
• Guarda este enlace para acceder cuando lo necesites
• Llega con anticipación para evitar congestiones

¡Nos vemos en el evento! 🎉

---
IEEE Tadeo Student Branch"""

    @staticmethod
    def render_email_template(
        organization: Optional[models.Organization],
        user_name: str,
        event_name: str,
        event_date: str,
        event_location: str,
        ticket_code: str,
        ticket_url: str,
        access_pin: str,
        companions: int = 0,
        qr_base64: str = "",
        event: Optional[models.Event] = None
    ) -> str:
        """
        Genera el HTML del email usando el template del evento, organización o el predeterminado

        Args:
            organization: Organización del evento (None = IEEE Tadeo)
            user_name: Nombre del usuario
            event_name: Nombre del evento
            event_date: Fecha formateada del evento
            event_location: Ubicación del evento
            ticket_code: Código del ticket
            ticket_url: URL del ticket
            access_pin: PIN de acceso
            companions: Número de acompañantes
            qr_base64: Código QR en formato base64
            event: Evento (opcional, para usar template específico del evento)

        Returns:
            str: HTML del email renderizado
        """
        # Jerarquía de templates: Evento > Organización > Default
        if event and event.email_template:
            template = event.email_template
        elif organization and organization.email_template:
            template = organization.email_template
        else:
            template = TemplateService.DEFAULT_EMAIL_TEMPLATE

        # Preparar información de acompañantes
        companions_info = ""
        if companions > 0:
            companions_info = f'<div class="info-item"><strong>Acompañantes:</strong> {companions} persona{"s" if companions != 1 else ""}</div>'

        # Reemplazar variables en el template
        html = template.format(
            user_name=user_name,
            event_name=event_name,
            event_date=event_date,
            event_location=event_location,
            ticket_code=ticket_code,
            ticket_url=ticket_url,
            access_pin=access_pin,
            companions=companions,
            companions_info=companions_info,
            qr_base64=qr_base64
        )

        return html

    @staticmethod
    def render_whatsapp_template(
        organization: Optional[models.Organization],
        user_name: str,
        event_name: str,
        event_date: str,
        event_location: str,
        ticket_code: str,
        ticket_url: str,
        access_pin: str,
        companions: int = 0,
        event: Optional[models.Event] = None
    ) -> str:
        """
        Genera el mensaje de WhatsApp usando el template del evento, organización o el predeterminado

        Args:
            organization: Organización del evento (None = IEEE Tadeo)
            user_name: Nombre del usuario
            event_name: Nombre del evento
            event_date: Fecha formateada del evento
            event_location: Ubicación del evento
            ticket_code: Código del ticket
            ticket_url: URL del ticket
            access_pin: PIN de acceso
            companions: Número de acompañantes
            event: Evento (opcional, para usar template específico del evento)

        Returns:
            str: Mensaje de WhatsApp renderizado
        """
        # Jerarquía de templates: Evento > Organización > Default
        if event and event.whatsapp_template:
            template = event.whatsapp_template
        elif organization and organization.whatsapp_template:
            template = organization.whatsapp_template
        else:
            template = TemplateService.DEFAULT_WHATSAPP_TEMPLATE

        # Preparar información de acompañantes
        companions_text = ""
        if companions > 0:
            companions_text = f"\n👥 *Acompañantes:* {companions} persona{'s' if companions != 1 else ''}"

        # Reemplazar variables en el template
        message = template.format(
            user_name=user_name,
            event_name=event_name,
            event_date=event_date,
            event_location=event_location,
            ticket_code=ticket_code,
            ticket_url=ticket_url,
            access_pin=access_pin,
            companions=companions,
            companions_text=companions_text
        )

        return message

    @staticmethod
    def get_email_subject(organization: Optional[models.Organization], event_name: str) -> str:
        """
        Genera el asunto del email según la organización

        Args:
            organization: Organización del evento
            event_name: Nombre del evento

        Returns:
            str: Asunto del email
        """
        if organization:
            org_name = organization.short_name or organization.name
            return f'Tu Ticket para {event_name} - {org_name}'
        else:
            return f'Tu Ticket para {event_name} - IEEE Tadeo'


# Instancia global del servicio
template_service = TemplateService()
