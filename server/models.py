from datetime import datetime, timedelta
from email.policy import default
from typing import Optional
from flask_login import UserMixin

from .app import db, login_manager


class User(db.Model, UserMixin):
    id: int = db.Column(db.Integer, primary_key=True)
    admin: bool = db.Column(db.Boolean, nullable=False, default=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    name: str = db.Column(db.String(20), unique=True, nullable=False)
    password: str = db.Column(db.String(60), nullable=False)
    image_file: str = db.Column(db.String(20), nullable=False,
                                default='default.jpg')
    phone: str = db.Column(db.Text, nullable=False)
    address: Optional[str] = db.Column(db.Text)

    contact: Optional[int] = db.Column(
        db.Integer, db.ForeignKey('user.id'))  # set if user

    def contact_class(self):
        return User.query.filter_by(id=self.contact).first()


class Trap(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    token: str = db.Column(db.String(16), unique=True, nullable=False)
    owner: Optional[int] = db.Column(db.Integer, db.ForeignKey('user.id'))
    owned_date: Optional[datetime] = db.Column(db.DateTime)
    name: str = db.Column(db.Text, nullable=False, default='n/a')

    last_status: datetime = db.Column(db.DateTime, nullable=False)
    caught: bool = db.Column(db.Boolean, nullable=False, default=False)
    battery: int = db.Column(db.Integer, nullable=False, default=0)
    charging: bool = db.Column(db.Boolean, nullable=False, default=False)
    temperature: int = db.Column(db.Integer, nullable=False, default=0)
    location_search: bool = db.Column(db.Boolean, nullable=False, default=True)
    location_searching: bool = db.Column(
        db.Boolean, nullable=False, default=True)
    location_acc: float = db.Column(db.Float, nullable=False, default=0)
    location_lat: Optional[float] = db.Column(db.Float)
    location_lon: Optional[float] = db.Column(db.Float)
    location_satellites: Optional[int] = db.Column(db.Integer)

    def owner_class(self) -> Optional[User]:
        return User.query.get(self.owner)

    def offline(self):
        return datetime.now() - self.last_status > timedelta(hours=1)

    def to_json(self):
        owner = self.owner_class()
        owner_name = owner.name if owner else 'n/a'

        return dict(
            id=self.id,
            name=self.name,
            offline=self.offline(),
            locationSearch=self.location_search,
            locationSearching=self.location_searching,
            latitude=self.location_lat,
            longitude=self.location_lon,
            accuracy=round(self.location_acc, 1),
            satellites=self.location_satellites,
            activated=self.caught,
            owner=owner_name,
            battery=self.battery,
            charging=self.charging,
            temperature=self.temperature,
            lastStatus=self.last_status.strftime('%d-%m-%y %H:%M'),
            ownedDate=self.owned_date.strftime(
                '%d-%m-%y %H:%M') if self.owned_date else '-'
        )


class Statistic(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date: datetime = db.Column(db.DateTime, nullable=False)


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)
