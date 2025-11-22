"""
Script para cambiar tickets existentes al modo 'daily' (validación diaria)

Uso:
    python cambiar_tickets_a_daily.py <event_id>
    python cambiar_tickets_a_daily.py --all  # Cambiar TODOS los tickets
    python cambiar_tickets_a_daily.py --ticket <ticket_id>  # Cambiar un ticket específico
"""

import sqlite3
import sys

def cambiar_evento_a_daily(event_id):
    """Cambia todos los tickets de un evento al modo daily"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Verificar que el evento existe
    cursor.execute("SELECT name, event_date FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()

    if not event:
        print(f"[ERROR] No se encontró el evento con ID {event_id}")
        conn.close()
        return False

    event_name, event_date = event

    # Contar tickets del evento
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE event_id = ?", (event_id,))
    ticket_count = cursor.fetchone()[0]

    print(f"\n=== Cambiar tickets a modo DAILY ===")
    print(f"Evento: {event_name}")
    print(f"Fecha: {event_date}")
    print(f"Tickets a modificar: {ticket_count}")
    print()

    # Confirmar
    respuesta = input(f"¿Deseas cambiar {ticket_count} tickets al modo 'daily'? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada")
        conn.close()
        return False

    # Actualizar tickets
    cursor.execute("""
        UPDATE tickets
        SET validation_mode = 'daily'
        WHERE event_id = ?
    """, (event_id,))

    conn.commit()
    print(f"\n[OK] {ticket_count} tickets cambiados a modo 'daily'")

    # Mostrar algunos ejemplos
    cursor.execute("""
        SELECT t.id, u.name, t.validation_mode
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        WHERE t.event_id = ?
        LIMIT 5
    """, (event_id,))

    print("\nEjemplos de tickets actualizados:")
    for ticket_id, user_name, mode in cursor.fetchall():
        print(f"  - Ticket #{ticket_id} ({user_name}): modo '{mode}'")

    conn.close()
    return True


def cambiar_ticket_especifico(ticket_id):
    """Cambia un ticket específico al modo daily"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Verificar que el ticket existe
    cursor.execute("""
        SELECT t.id, u.name, e.name, t.validation_mode
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        JOIN events e ON t.event_id = e.id
        WHERE t.id = ?
    """, (ticket_id,))

    ticket = cursor.fetchone()

    if not ticket:
        print(f"[ERROR] No se encontró el ticket con ID {ticket_id}")
        conn.close()
        return False

    tid, user_name, event_name, current_mode = ticket

    print(f"\n=== Cambiar ticket a modo DAILY ===")
    print(f"Ticket ID: {tid}")
    print(f"Usuario: {user_name}")
    print(f"Evento: {event_name}")
    print(f"Modo actual: {current_mode}")
    print()

    respuesta = input("¿Deseas cambiar este ticket al modo 'daily'? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada")
        conn.close()
        return False

    # Actualizar ticket
    cursor.execute("""
        UPDATE tickets
        SET validation_mode = 'daily'
        WHERE id = ?
    """, (ticket_id,))

    conn.commit()
    print(f"\n[OK] Ticket #{ticket_id} cambiado a modo 'daily'")

    conn.close()
    return True


def cambiar_todos_a_daily():
    """Cambia TODOS los tickets al modo daily"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tickets")
    total = cursor.fetchone()[0]

    print(f"\n=== ADVERTENCIA ===")
    print(f"Esto cambiará TODOS los {total} tickets al modo 'daily'")
    print()

    respuesta = input("¿Estás seguro? Escribe 'SI' para confirmar: ")
    if respuesta != 'SI':
        print("Operación cancelada")
        conn.close()
        return False

    cursor.execute("UPDATE tickets SET validation_mode = 'daily'")
    conn.commit()

    print(f"\n[OK] {total} tickets cambiados a modo 'daily'")
    conn.close()
    return True


def listar_eventos():
    """Lista todos los eventos disponibles"""
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            e.id,
            e.name,
            e.event_date,
            COUNT(t.id) as ticket_count,
            SUM(CASE WHEN t.validation_mode = 'daily' THEN 1 ELSE 0 END) as daily_count
        FROM events e
        LEFT JOIN tickets t ON e.event_id = t.event_id
        GROUP BY e.id
        ORDER BY e.event_date DESC
    """)

    print("\n=== EVENTOS DISPONIBLES ===\n")
    print(f"{'ID':<5} {'Nombre':<50} {'Fecha':<20} {'Tickets':<10} {'Daily':<10}")
    print("-" * 100)

    for event_id, name, date, tickets, daily in cursor.fetchall():
        print(f"{event_id:<5} {name:<50} {date:<20} {tickets:<10} {daily:<10}")

    print()
    conn.close()


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python cambiar_tickets_a_daily.py <event_id>")
        print("  python cambiar_tickets_a_daily.py --all")
        print("  python cambiar_tickets_a_daily.py --ticket <ticket_id>")
        print("  python cambiar_tickets_a_daily.py --list")
        print()
        listar_eventos()
        return

    arg = sys.argv[1]

    if arg == '--list':
        listar_eventos()
    elif arg == '--all':
        cambiar_todos_a_daily()
    elif arg == '--ticket':
        if len(sys.argv) < 3:
            print("[ERROR] Debes especificar el ID del ticket")
            print("Uso: python cambiar_tickets_a_daily.py --ticket <ticket_id>")
            return
        ticket_id = int(sys.argv[2])
        cambiar_ticket_especifico(ticket_id)
    else:
        event_id = int(arg)
        cambiar_evento_a_daily(event_id)


if __name__ == "__main__":
    main()
