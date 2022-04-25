from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User

""" registration form for register.html """
class RegistrationForm(FlaskForm):
    name = StringField('Naam', validators=[ DataRequired(), Length(min=2, max=20) ])
    email = StringField('E-Mail', validators=[ DataRequired(), Email() ])
    password = PasswordField('Wachtwoord', validators=[ DataRequired() ])
    confirm_password = PasswordField('Wachtwoord herhalen', validators=[ DataRequired(), EqualTo('password') ])
    submit = SubmitField('Registeren')

    """ validates whether name is already in use """
    def validate_name(self, name):
        if User.query.filter_by(name=name.data).first():
            raise ValidationError('Deze gebruikersnaam bestaat al, kies een andere.')

    """ validates whether e-mail is already in use """
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Deze e-mail bestaat al, log in als dat uw e-mail is')


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
