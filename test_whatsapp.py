"""
Script de prueba para el servicio de WhatsApp
"""
from whatsapp_client import WhatsAppClient


def main():
    print("=" * 60)
    print("TEST DE SERVICIO DE WHATSAPP")
    print("=" * 60)
    print()

    # Crear cliente
    client = WhatsAppClient()

    # 1. Verificar estado
    print("[1] Verificando estado del servicio...")
    status = client.get_status()

    print(f"   Estado: {status.get('message', 'Desconocido')}")
    print(f"   Listo: {'✓ Sí' if status.get('ready') else '✗ No'}")

    if status.get('qr'):
        print("\n   [!] Se requiere escanear código QR")
        print("   [!] Abre http://localhost:3000/status en tu navegador")
        print("   [!] O revisa la consola del servicio Node.js")
        return

    if not status.get('ready'):
        print("\n   [!] WhatsApp no está listo todavía")
        print("   [!] Inicia el servicio con: cd whatsapp-service && npm start")
        return

    print("\n   ✓ WhatsApp está listo para enviar mensajes\n")

    # 2. Menú de prueba
    while True:
        print("\n" + "=" * 60)
        print("MENÚ DE PRUEBAS")
        print("=" * 60)
        print("1. Enviar mensaje de prueba")
        print("2. Enviar mensaje de cumpleaños")
        print("3. Verificar estado")
        print("4. Salir")
        print()

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            print("\n--- ENVIAR MENSAJE DE PRUEBA ---")
            phone = input("Número de teléfono (ej: +573001234567): ").strip()
            message = input("Mensaje: ").strip()

            if phone and message:
                print("\nEnviando mensaje...")
                result = client.send_message(phone, message)

                if result.get("success"):
                    print("✓ Mensaje enviado exitosamente!")
                    print(f"  ID: {result.get('messageId')}")
                else:
                    print(f"✗ Error: {result.get('error')}")
            else:
                print("✗ Debes ingresar teléfono y mensaje")

        elif opcion == "2":
            print("\n--- ENVIAR MENSAJE DE CUMPLEAÑOS ---")
            phone = input("Número (ej: 3001234567): ").strip()
            country_code = input("Código de país (default: +57): ").strip() or "+57"
            name = input("Nombre del usuario: ").strip()

            if phone and name:
                from whatsapp_client import send_birthday_whatsapp

                print("\nEnviando mensaje de cumpleaños...")
                success = send_birthday_whatsapp(phone, country_code, name)

                if success:
                    print("✓ Mensaje de cumpleaños enviado!")
                else:
                    print("✗ Error al enviar mensaje")
            else:
                print("✗ Debes ingresar teléfono y nombre")

        elif opcion == "3":
            print("\n--- VERIFICAR ESTADO ---")
            status = client.get_status()
            print(f"Estado: {status.get('message')}")
            print(f"Listo: {'✓ Sí' if status.get('ready') else '✗ No'}")

        elif opcion == "4":
            print("\n¡Hasta luego!")
            break

        else:
            print("\n✗ Opción inválida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego!")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
