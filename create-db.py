from random import randint
from server.app import db, bcrypt
from server.models import User, UserType

#name = input('Naam? ')
#email = input('E-Mail? ')
#typ = input('Type [admin,manager,technician,catcher,client]? ')

users = [
	(1, UserType.CLIENT, 'Boer Herman', 'boer@muizenval.tk', 2),
	(2, UserType.ADMIN, 'Administrator Ralf', 'admin@muizenval.tk', None),
]

address = 'Kerklaan 69\n9876XY Groningen'

hashed_password = bcrypt.generate_password_hash('hallo').decode('utf-8')

db.create_all()

for id, typ, name, email, contact in users:
	phone = '06-' + str(randint(10000000, 99999999))
	user = User(
		id=id,
		type=typ,
		name=name, 
		email=email, 
		password=hashed_password,
		phone=phone,
		address = address,
		contact=contact
	)
	db.session.add(user)

db.session.commit()
print('Added')
