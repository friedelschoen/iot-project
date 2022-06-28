from datetime import datetime
from typing import Any, Dict, Optional
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
    name: Optional[str] = db.Column(db.Text)

    last_status: Optional[datetime] = db.Column(db.DateTime)
    caught: Optional[bool] = db.Column(db.Boolean)
    battery: Optional[int] = db.Column(db.Integer)
    charging: Optional[bool] = db.Column(db.Boolean)
    temperature: Optional[int] = db.Column(db.Integer)
    location_lat: Optional[float] = db.Column(db.Float)
    location_lon: Optional[float] = db.Column(db.Float)
    location_acc: Optional[float] = db.Column(db.Float)
    location_satellites: Optional[int] = db.Column(db.Integer)

    def owner_class(self) -> Optional[User]:
        return User.query.get(self.owner)

    def status_color(self) -> str:
        if self.caught:
            return '#f4a900'
        return 'currentColor'

    def dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self, token: bool = False):
        owner = self.owner_class()
        owner_name = owner.name if owner else '{nobody}'

        return dict(
            id=self.id,
            name=self.name or '<code>unnamed</code>',
            status=self.status_color(),
            location=self.location_acc and self.location_acc > 0,
            latitude=self.location_lat,
            longitude=self.location_lon,
            accuracy=self.location_acc,
            satellites=self.location_satellites,
            activated=self.caught,
            owner=owner_name,
            battery=self.battery,
            charging=self.charging,
            temperature=self.temperature,
            byToken=token
        )


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(user_id)
