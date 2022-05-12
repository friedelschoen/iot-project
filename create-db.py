from server.app import db
import server.models

db.create_all()
db.session.commit()
