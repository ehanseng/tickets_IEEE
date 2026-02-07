"""
Script para eliminar templates rechazados y crear nuevas versiones.
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from whatsapp_client import WhatsAppClient


def main():
    client = WhatsAppClient()

    if not client.is_ready():
        print("Error: WhatsApp API no configurado")
        sys.exit(1)

    # 1. Eliminar templates rechazados
    print("=" * 60)
    print("Eliminando templates rechazados...")
    print("=" * 60)

    templates_to_delete = ["ticket_evento", "ticket_evento_acompanantes"]

    for template_name in templates_to_delete:
        print(f"\nEliminando: {template_name}")
        result = client.delete_template(template_name)
        if result.get("success"):
            print(f"   OK: {result.get('message')}")
        else:
            print(f"   Error: {result.get('error')}")

    # 2. Crear nuevas versiones sin URL (las URLs pueden causar rechazo)
    print("\n" + "=" * 60)
    print("Creando nuevos templates...")
    print("=" * 60)

    # Template de ticket simplificado (sin URL, sin muchas variables)
    print("\nCreando: ticket_confirmacion")
    result = client.create_template(
        name="ticket_confirmacion",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Registro Confirmado",
        body_text="""Hola {{1}}! Tu registro para el evento {{2}} ha sido confirmado.

Fecha: {{3}}
Lugar: {{4}}

Tu codigo de acceso es: {{5}}
PIN: {{6}}

Guarda este mensaje y presentalo en la entrada del evento. Te esperamos!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=[
            "Juan Perez",
            "Workshop de Python",
            "15 de Enero 2025",
            "Auditorio UTadeo",
            "TKT-12345",
            "1234"
        ]
    )

    if result.get("success"):
        print(f"   OK: ID={result.get('template_id')}, Estado={result.get('status')}")
    else:
        print(f"   Error: {result.get('error')}")
        if result.get("error_user_msg"):
            print(f"   Detalle: {result.get('error_user_msg')}")

    # Template simple para enviar ticket (solo 3 variables)
    print("\nCreando: entrada_evento")
    result = client.create_template(
        name="entrada_evento",
        category="UTILITY",
        language="es_MX",
        header_type="TEXT",
        header_text="Tu entrada al evento",
        body_text="""Hola {{1}}! Tienes una entrada para {{2}}.

Tu codigo de acceso: {{3}}

Presenta este codigo en la entrada. Te esperamos!""",
        footer_text="IEEE Tadeo Student Branch",
        variable_examples=[
            "Maria Garcia",
            "Conferencia IEEE 2025",
            "TKT-ABC123"
        ]
    )

    if result.get("success"):
        print(f"   OK: ID={result.get('template_id')}, Estado={result.get('status')}")
    else:
        print(f"   Error: {result.get('error')}")
        if result.get("error_user_msg"):
            print(f"   Detalle: {result.get('error_user_msg')}")

    # Listar templates
    print("\n" + "=" * 60)
    print("Templates actuales:")
    print("=" * 60)

    result = client.get_templates()
    if result.get("success"):
        for t in result.get("templates", []):
            status_emoji = {"APPROVED": "OK", "PENDING": "...", "REJECTED": "X"}.get(t.get("status"), "?")
            print(f"  [{status_emoji}] {t.get('name')} ({t.get('language')}) - {t.get('status')}")


if __name__ == "__main__":
    main()
