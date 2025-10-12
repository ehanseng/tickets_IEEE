from database import SessionLocal
from models import User

db = SessionLocal()

users = db.query(User).filter(User.birthday.isnot(None)).all()
print(f'Usuarios con cumpleanos: {len(users)}')
print()

for u in users:
    birthday_str = u.birthday.strftime('%Y-%m-%d') if u.birthday else 'None'
    print(f'{u.id}. {u.name}: {birthday_str}')

db.close()
