"""
Endpoint público para agregar al archivo user_portal_routes.py
"""

# Agregar al final del archivo user_portal_routes.py:

"""
# ========== ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN) ==========
@router.get("/api/public/ticket/{unique_url}")
async def get_public_ticket(
    unique_url: str,
    db: Session = Depends(get_db)
):
    '''Obtiene información del ticket usando la URL única (sin autenticación)'''
    ticket = db.query(models.Ticket).options(
        joinedload(models.Ticket.event),
        joinedload(models.Ticket.user)
    ).filter(
        models.Ticket.unique_url == unique_url
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )

    return {
        "id": ticket.id,
        "ticket_code": ticket.ticket_code,
        "user_name": ticket.user.name,
        "event": {
            "name": ticket.event.name,
            "date": ticket.event.event_date,
            "location": ticket.event.location,
            "description": ticket.event.description
        },
        "companions": ticket.companions,
        "is_used": ticket.is_used,
        "used_at": ticket.used_at,
        "qr_path": ticket.qr_path,
        "created_at": ticket.created_at
    }
"""
