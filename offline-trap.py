from datetime import timedelta
from server.app import db
from server.models import Trap

for trap in Trap.query:
    trap.last_status -= timedelta(hours=1)

db.session.commit()
