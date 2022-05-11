from datetime import datetime

from flask_login import UserMixin

from .app import db, login_manager

""" function to load a user from database """
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(7), nullable=False, default="guest") # guest, client, catcher, admin
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

class Home(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    catcher = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    street = db.Column(db.Text, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    zipcode = db.Column(db.Text, nullable=False)
    place = db.Column(db.Text, nullable=False)

class Trap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(16), unique=True, nullable=False)
    name = db.Column(db.Text)
    home = db.Column(db.Integer, db.ForeignKey('home.id'), nullable=False)
    last_heartbeat = db.Column(db.Integer, nullable=True, default=0)
    caught = db.Column(db.Boolean, nullable=False, default=False)
