"""
Script para crear los templates de WhatsApp en Meta Business API.

Estos templates deben ser aprobados por Meta antes de poder usarlos
para enviar mensajes a usuarios que no han iniciado conversación (24h).

Ejecutar: python create_whatsapp_templates.py

Documentación: https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates
"""
import sys
import io

# Configurar codificacion UTF-8 para stdout en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from whatsapp_client import WhatsAppClient


def create_birthday_template(client: WhatsAppClient) -> dict:
    """
    Crea el template de felicitación de cumpleaños.

    Variables:
        {{1}} - Nombre del usuario (display_name)
    """
    return client.create_template(
        name="feliz_cumpleanos_v2",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Feliz Cumpleanos",
        body_text="""🎉 ¡Feliz Cumpleaños {{1}}! 🎂

Desde IEEE Tadeo queremos desearte un día lleno de alegría y éxito.

¡Que cumplas muchos más! 🎈✨""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=["María"]
    )


def create_ticket_notification_template(client: WhatsAppClient) -> dict:
    """
    Crea el template de notificación de ticket para eventos.

    Variables:
        {{1}} - Nombre del usuario
        {{2}} - Nombre del evento
        {{3}} - Fecha y hora del evento
        {{4}} - Ubicación del evento
        {{5}} - Código del ticket
        {{6}} - PIN de acceso
        {{7}} - URL del ticket
    """
    return client.create_template(
        name="ticket_evento",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Tu Ticket para el Evento",
        body_text="""Hola {{1}}! Tu registro para {{2}} ha sido confirmado.

Fecha: {{3}}
Lugar: {{4}}

Codigo: {{5}}
PIN: {{6}}

Presenta este codigo o tu QR en la entrada.

Ver tu ticket aqui: {{7}}

Te esperamos!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=[
            "Juan Perez",
            "Workshop de Python",
            "15 de Enero 2025 - 10:00 AM",
            "Auditorio Principal UTadeo",
            "TKT-12345",
            "1234",
            "https://ticket.ieeetadeo.org/t/TKT-12345"
        ]
    )


def create_ticket_with_companions_template(client: WhatsAppClient) -> dict:
    """
    Crea el template de notificación de ticket con acompañantes.

    Variables:
        {{1}} - Nombre del usuario
        {{2}} - Nombre del evento
        {{3}} - Fecha y hora del evento
        {{4}} - Ubicación del evento
        {{5}} - Código del ticket
        {{6}} - PIN de acceso
        {{7}} - Número de acompañantes
        {{8}} - URL del ticket
    """
    return client.create_template(
        name="ticket_evento_acompanantes",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Tu Ticket para el Evento",
        body_text="""Hola {{1}}! Tu registro para {{2}} ha sido confirmado.

Fecha: {{3}}
Lugar: {{4}}

Codigo: {{5}}
PIN: {{6}}
Acompanantes: {{7}}

Presenta este codigo en la entrada.

Ver tu ticket aqui: {{8}}

Te esperamos!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=[
            "Juan Perez",
            "Workshop de Python",
            "15 de Enero 2025 - 10:00 AM",
            "Auditorio Principal UTadeo",
            "TKT-12345",
            "1234",
            "2",
            "https://ticket.ieeetadeo.org/t/TKT-12345"
        ]
    )


def create_event_reminder_template(client: WhatsAppClient) -> dict:
    """
    Crea el template de recordatorio de evento (24h antes).

    Variables:
        {{1}} - Nombre del usuario
        {{2}} - Nombre del evento
        {{3}} - Fecha y hora del evento
        {{4}} - Ubicación del evento
    """
    return client.create_template(
        name="recordatorio_evento",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Recordatorio de Evento",
        body_text="""Hola {{1}}!

Te recordamos que manana tienes el evento:

{{2}}

Fecha: {{3}}
Lugar: {{4}}

Te esperamos!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=[
            "Maria Garcia",
            "Hackathon IEEE 2025",
            "16 de Enero 2025 - 9:00 AM",
            "Edificio de Ingenieria UTadeo"
        ]
    )


def create_welcome_template(client: WhatsAppClient) -> dict:
    """
    Crea el template de bienvenida para nuevos registros.

    Variables:
        {{1}} - Nombre del usuario
    """
    return client.create_template(
        name="bienvenida_ieee",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Bienvenido a IEEE Tadeo",
        body_text="""Hola {{1}}!

Bienvenido/a al sistema de tickets de IEEE Tadeo Student Branch.

Aqui podras:
- Recibir tickets para nuestros eventos
- Ver tu historial de asistencia
- Mantenerte informado de actividades

Gracias por registrarte!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=["Carlos Rodriguez"]
    )


def list_existing_templates(client: WhatsAppClient):
    """Lista los templates existentes en la cuenta"""
    print("\n📋 Templates existentes en la cuenta:")
    print("=" * 60)

    result = client.get_templates()

    if result.get("success"):
        templates = result.get("templates", [])
        if templates:
            for t in templates:
                status_emoji = {
                    "APPROVED": "✅",
                    "PENDING": "⏳",
                    "REJECTED": "❌"
                }.get(t.get("status"), "❓")

                print(f"\n{status_emoji} {t.get('name')}")
                print(f"   Categoría: {t.get('category')}")
                print(f"   Idioma: {t.get('language')}")
                print(f"   Estado: {t.get('status')}")
        else:
            print("No hay templates registrados.")
    else:
        print(f"Error al obtener templates: {result.get('error')}")

    print("\n" + "=" * 60)


def main():
    print("=" * 60)
    print("🔧 Creador de Templates de WhatsApp para IEEE Tadeo")
    print("=" * 60)

    # Inicializar cliente
    client = WhatsAppClient()

    if not client.is_ready():
        print("\n❌ Error: WhatsApp API no está configurado.")
        print("   Asegúrate de tener configuradas las siguientes variables en .env:")
        print("   - WHATSAPP_PHONE_NUMBER_ID")
        print("   - WHATSAPP_BUSINESS_ACCOUNT_ID")
        print("   - WHATSAPP_ACCESS_TOKEN")
        sys.exit(1)

    print("\n✅ Cliente de WhatsApp inicializado correctamente.")

    # Listar templates existentes
    list_existing_templates(client)

    # Definir templates a crear
    templates_to_create = [
        ("Cumpleaños", create_birthday_template),
        ("Ticket de Evento", create_ticket_notification_template),
        ("Ticket con Acompañantes", create_ticket_with_companions_template),
        ("Recordatorio de Evento", create_event_reminder_template),
        ("Bienvenida", create_welcome_template),
    ]

    print("\n📝 Creando templates...")
    print("-" * 60)

    results = {
        "created": [],
        "failed": []
    }

    for name, create_func in templates_to_create:
        print(f"\n➡️  Creando template: {name}")

        try:
            result = create_func(client)

            if result.get("success"):
                template_id = result.get("template_id")
                status = result.get("status", "PENDING")
                print(f"   ✅ Creado exitosamente")
                print(f"      ID: {template_id}")
                print(f"      Estado: {status}")
                results["created"].append(name)
            else:
                error = result.get("error", "Error desconocido")
                error_code = result.get("error_code", "N/A")
                error_subcode = result.get("error_subcode", "N/A")
                error_user_msg = result.get("error_user_msg", "")
                print(f"   ❌ Error al crear: {error}")
                print(f"      Código: {error_code}, Subcódigo: {error_subcode}")
                if error_user_msg:
                    print(f"      Detalle: {error_user_msg}")
                # Mostrar error completo para debug
                full_error = result.get("full_error")
                if full_error:
                    print(f"      Debug: {full_error}")

                # Si ya existe, no es un error real
                if "already exists" in error.lower() or error_code == 2388047:
                    print(f"      ℹ️  El template ya existe, no es necesario crearlo de nuevo.")
                    results["created"].append(f"{name} (ya existía)")
                else:
                    results["failed"].append((name, error))

        except Exception as e:
            print(f"   ❌ Excepción: {str(e)}")
            results["failed"].append((name, str(e)))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)

    print(f"\n✅ Templates creados/existentes: {len(results['created'])}")
    for name in results["created"]:
        print(f"   • {name}")

    if results["failed"]:
        print(f"\n❌ Templates con error: {len(results['failed'])}")
        for name, error in results["failed"]:
            print(f"   • {name}: {error}")

    print("\n" + "-" * 60)
    print("📋 Próximos pasos:")
    print("   1. Espera la aprobación de Meta (puede tomar 24-48 horas)")
    print("   2. Verifica el estado en Meta Business Suite:")
    print("      https://business.facebook.com/wa/manage/message-templates/")
    print("   3. Una vez aprobados, actualiza el código para usar templates")
    print("      en lugar de mensajes de texto libre.")
    print("=" * 60)

    # Listar templates al final
    list_existing_templates(client)


if __name__ == "__main__":
    main()
