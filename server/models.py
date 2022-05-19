from email.policy import default
from enum import Enum
from flask_login import UserMixin

from .app import db, login_manager

""" function to load a user from database """
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserType(Enum):
    ADMIN = 0
    CLIENT = 1

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(UserType), nullable=False, default=UserType.CLIENT)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    phone = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)

    contact = db.Column(db.Integer, db.ForeignKey('user.id')) # set if user

    def contact_class(self):
        return User.query.filter_by(id=self.contact).first()


class Trap(db.Model):
    mac = db.Column(db.String(16), primary_key=True, nullable=False)
    name = db.Column(db.Text)
    last_heartbeat = db.Column(db.DateTime)
    caught = db.Column(db.Boolean, nullable=False, default=False)  
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    connect_expired = db.Column(db.DateTime)
    location_lat = db.Column(db.Float)
    location_lon = db.Column(db.Float)

    def pretty_mac(self):
        upper = self.mac.upper()
        return ':'.join([ upper[i] + upper[i+1] for i in range(0, len(upper), 2) ])
    
    def owner_class(self):
        return User.query.filter_by(id=self.owner).first()

    def status_color(self):
        if self.caught:
            return '#f4a900'
        return 'currentColor'
