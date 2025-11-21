"""
Script para corregir las llaves en el template de email
Duplica las llaves del CSS para que Python las escape correctamente
"""
import sqlite3
import sys
import io

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_template_braces():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Obtener todos los eventos con email_template
    cursor.execute("""
        SELECT id, name, email_template
        FROM events
        WHERE email_template IS NOT NULL
    """)

    events = cursor.fetchall()

    if not events:
        print("❌ No se encontraron eventos con templates de email")
        return

    print(f"✅ Encontrados {len(events)} eventos con templates")

    for event_id, name, template in events:
        print(f"\n📧 Evento: {name} (ID: {event_id})")

        if not template:
            print("   ⚠️  Template vacío, saltando...")
            continue

        # Verificar si ya tiene llaves dobles en el <style>
        if '{{' in template and '<style>' in template:
            print("   ✅ Template ya tiene llaves dobles en CSS")
            continue

        # Buscar la sección <style> y duplicar las llaves
        fixed_template = template

        # Solo duplicar llaves dentro de <style>...</style>
        import re

        def duplicate_braces_in_style(match):
            style_content = match.group(1)
            # Duplicar llaves solo si no están ya duplicadas
            style_content = style_content.replace('{{', '<<<DOUBLE>>>').replace('}}', '<<<DOUBLE_CLOSE>>>')
            style_content = style_content.replace('{', '{{').replace('}', '}}')
            style_content = style_content.replace('<<<DOUBLE>>>', '{{').replace('<<<DOUBLE_CLOSE>>>', '}}')
            return f'<style>{style_content}</style>'

        fixed_template = re.sub(r'<style>(.*?)</style>', duplicate_braces_in_style, fixed_template, flags=re.DOTALL)

        if fixed_template != template:
            # Actualizar el template
            cursor.execute("""
                UPDATE events
                SET email_template = ?
                WHERE id = ?
            """, (fixed_template, event_id))

            conn.commit()
            print("   ✅ Template corregido y actualizado")
        else:
            print("   ℹ️  No se necesitaron cambios")

    conn.close()
    print("\n✅ Proceso completado")

if __name__ == "__main__":
    fix_template_braces()
