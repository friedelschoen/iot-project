import re
from tokenize import String
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, HiddenField, PasswordField, StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User

""" registration form for register.html """
class RegistrationForm(FlaskForm):
    name = StringField('Naam', validators=[ DataRequired(), Length(min=5, max=20) ])
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[ DataRequired() ])
    confirm_password = PasswordField('Wachtwoord herhalen', validators=[ DataRequired(), EqualTo('password') ])
    phone = StringField('Telefoon', validators=[ DataRequired(), Length(min=5) ])
    street = StringField('Straat', validators=[ DataRequired() ])
    housenumber = IntegerField('Huisnummer', validators=[ DataRequired() ])
    zipcode = StringField('Postcode', validators=[ DataRequired() ])
    place = StringField('Plaats', validators=[ DataRequired() ])
    submit = SubmitField('Registeren')

    """ validates whether name is already in use """
    def validate_name(self, name):
        if User.query.filter_by(name=name.data).first():
            raise ValidationError('Deze gebruikersnaam bestaat al, kies een andere.')

    """ validates whether e-mail is already in use """
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Deze e-mail bestaat al, log in als dat uw e-mail is.')

    def validate_phone(self, phone):
        for c in phone.data:
            if c not in '0123456789- ':
                raise ValidationError('Dit belnummer is niet geldig.')

    def validate_postcode(self, code):
        if len(code.data) != 6 or not code.data[0:4].isnumeric() or not code.data[4:6].isalpha():
            raise ValidationError('De postcode is niet geldig.')


""" login form for login.html """
class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[ DataRequired() ])
    remember = BooleanField('Herinneren')
    submit = SubmitField('Inloggen')


""" update account form for account.html """
class UpdateAccountForm(FlaskForm):
    name = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20) ])
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[])
    confirm_password = PasswordField('Wachtwoord herhalen', validators=[ EqualTo('password') ])
    picture = FileField('Profielfoto bewerken', validators=[ FileAllowed(['jpg', 'png']) ])
    submit = SubmitField('Bewerken')

    """ validates whether name is already in use """
    def validate_name(self, name):
        if name.data != current_user.name and User.query.filter_by(name=name.data).first():
            raise ValidationError('Deze gebruikersnaam bestaat al, kies een andere.')

    """ validates whether e-mail is already in use """
    def validate_email(self, email):
        if email.data != current_user.email and User.query.filter_by(email=email.data).first():
            raise ValidationError('Deze e-mail bestaat al, log in als dat uw e-mail is')

class UpdateTrapForm(FlaskForm):
    mac = StringField('MAC')
    name = StringField('Naam')
    location = StringField('Locatie')
    submit = SubmitField('Bewerken')

class ConnectTrapForm(FlaskForm):
    mac = StringField('MAC', validators=[ Length(min=16, max=16) ])
    submit = SubmitField('Verbinden')




""" search form for admin.html """
class SearchForm(FlaskForm):
    username = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Zoeken')

""" account-settings form for admin_user.html """
class AdminForm(FlaskForm):
    type = SelectField('Type',  choices=[('client', 'Klant'), ('admin', 'Administrator')])
    submit = SubmitField('Bewerken')
