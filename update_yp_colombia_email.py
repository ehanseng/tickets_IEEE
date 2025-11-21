"""
Script para actualizar el email de contacto de IEEE Young Professionals Colombia
"""
import sqlite3
import sys
import io

# Configurar stdout para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def update_yp_email():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Verificar si existe la organización
    cursor.execute("""
        SELECT id, name, contact_email
        FROM organizations
        WHERE name LIKE '%Young Professionals%' OR name LIKE '%YP%'
    """)

    orgs = cursor.fetchall()

    if not orgs:
        print("❌ No se encontró la organización IEEE Young Professionals Colombia")
        print("   Creando organización...")

        cursor.execute("""
            INSERT INTO organizations (name, short_name, description, contact_email)
            VALUES (?, ?, ?, ?)
        """, (
            'IEEE Young Professionals Colombia',
            'IEEE YP Colombia',
            'Organización de IEEE Young Professionals en Colombia',
            'yp@ieee.org.co'  # Cambiar por el email real
        ))

        conn.commit()
        print("✅ Organización creada")
        print("   Por favor actualiza el email de contacto manualmente si es necesario")
    else:
        print(f"✅ Organización encontrada:")
        for org_id, name, email in orgs:
            print(f"   ID: {org_id}")
            print(f"   Nombre: {name}")
            print(f"   Email actual: {email or '(sin email)'}")

            if not email:
                # Pedir el email al usuario
                print("\n⚠️  Esta organización no tiene email de contacto configurado")
                new_email = input("   Ingresa el email de contacto (o Enter para saltar): ").strip()

                if new_email:
                    cursor.execute("""
                        UPDATE organizations
                        SET contact_email = ?
                        WHERE id = ?
                    """, (new_email, org_id))

                    conn.commit()
                    print(f"   ✅ Email actualizado a: {new_email}")

    conn.close()

if __name__ == "__main__":
    update_yp_email()
