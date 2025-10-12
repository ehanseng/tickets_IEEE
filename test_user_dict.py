from database import SessionLocal
from models import User, Ticket
from sqlalchemy import func
from birthday_utils import get_birthday_status

db = SessionLocal()

# Simular el código del endpoint /admin/users
users = db.query(
    User,
    func.count(Ticket.id).label('ticket_count')
).outerjoin(Ticket).group_by(User.id).limit(3).all()

print("Testing user data structure for /admin/users:\n")

for user, ticket_count in users:
    # Obtener información del cumpleaños
    birthday_status = get_birthday_status(user.birthday)

    user_dict = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'identification': user.identification,
        'university_id': user.university_id,
        'is_ieee_member': user.is_ieee_member,
        'birthday': user.birthday,
        'created_at': user.created_at,
        'ticket_count': ticket_count,
        'university': None,
        'birthday_status': birthday_status
    }

    print(f"Usuario: {user.name}")
    print(f"  ID: {user.id}")
    print(f"  Birthday in DB: {user.birthday}")
    print(f"  Birthday in dict: {user_dict['birthday']}")
    if user.birthday:
        print(f"  Birthday formatted: {user.birthday.strftime('%Y-%m-%d')}")
    print()

db.close()
