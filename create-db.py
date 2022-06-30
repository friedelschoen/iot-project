from random import randint, choice
from server.app import db, bcrypt
from server.models import User

TOKEN_CHARS = '0123456789abcdefghijklmnopqrstuvwxyz'

users = [
    #    (1, False, 'Boer Herman', 'boer@muizenval.tk', 2),
    #   (2, True, 'Administrator Ralf', 'admin@muizenval.tk', None),
]

address = 'Kerklaan 69\n9876XY Groningen'

hashed_password = bcrypt.generate_password_hash('hallo').decode('utf-8')

db.create_all()

for id, admin, name, email, contact in users:
    phone = '06-' + str(randint(10000000, 99999999))
    user = User(
        id=id,
        admin=admin,
        name=name,
        email=email,
        password=hashed_password,
        phone=phone,
        address=address,
        contact=contact
    )
    db.session.add(user)

db.session.commit()
print('Added')
