from enum import Enum
from flask_login import UserMixin

from .app import db, login_manager

""" function to load a user from database """
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserType(Enum):
    ADMIN = 0
    MANAGER = 1
    TECHNICIAN = 2
    CATCHER = 3
    CLIENT = 4

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(UserType))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    phone = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)

    manager = db.Column(db.Integer, db.ForeignKey('user.id')) # set if technician, catcher, user
    catcher_code = db.Column(db.String(5)) # set if catcher 
    catcher = db.Column(db.Integer, db.ForeignKey('user.id')) # set if user


class Trap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(16), unique=True, nullable=False)
    name = db.Column(db.Text)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_heartbeat = db.Column(db.DateTime, nullable=True, default=0)
    caught = db.Column(db.Boolean, nullable=False, default=False)

    def pretty_mac(self):
        upper = self.mac.upper()
        return ':'.join([ upper[i] + upper[i+1] for i in range(0, len(upper), 2) ])

    def status_color(self):
        if self.caught:
            return '#f4a900'
        return 'currentColor'
