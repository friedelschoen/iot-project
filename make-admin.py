from server.app import db
from server.models import User
import sys

user = User.query.filter_by(email=sys.argv[1]).first()
if not user:
    print('not found')
    exit(1)

user.admin = True

db.session.commit()
