from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from .app import app, bcrypt, db
from .forms import AdminForm, LoginForm, RegistrationForm, SearchForm, UpdateAccountForm, UpdateTrapForm
from .models import Trap, User

import secrets
import os
import random
import string

current_user: User


def validate_mac(mac):
    return len(mac) == 16 and all(c in string.hexdigits for c in mac)


""" index.html (home-page) route """


@app.route("/")
def index():
    return render_template('index.html')


""" home.html route """


@app.route("/home")
def home():
    return render_template('home.html', title='Home')


""" register.html route """


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('U bent al ingelogd', 'warning')
        return redirect('/')

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        address = f"{form.street} {form.housenumber}\n{form.postcode} {form.place}"
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            phone=form.phone.data,
            address=address
        )
        db.session.add(user)
        db.session.commit()
        flash('Uw profiel werd toegevoegd! U kan nu inloggen.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registeren', form=form)


@app.route("/producten")
def producten():
    return render_template('producten.html')


""" login.html route """


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('U bent al ingelogd', 'warning')
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if bcrypt.check_password_hash(user.password, form.email.data):
                flash(
                    'Wij zullen aanbevelen uw wachtwoord weer te veranderen', 'warning')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else '/')
        else:
            flash('Kon niet inloggen, is uw e-mail en wachtwoord juist?', 'danger')
    return render_template('login.html', title='Inloggen', form=form)


""" logout route """


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


""" save-picture function for account.html """


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picturepath = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picturepath)

    return picture_fn


""" account.html route """


@app.route("/user/self", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.password.data:
            current_user.password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
        db.session.commit()
        flash('Uw profiel is bewerkt!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',  title='Profiel', image_file=image_file, form=form)


@app.route('/traps')
@login_required
def traps():
    if current_user.admin:
        #        clean_traps()
        query = Trap.query.all()
    else:
        query = Trap.query.filter_by(owner=current_user.id)

    trap_json = [trap.dict() for trap in query]

    return render_template('trap.html', traps=query, trap_json=trap_json)


"""
@app.route('/traps/connect', methods=['POST', 'GET'])
@login_required
def trap_connect():
    form = ConnectTrapForm()
    if form.validate_on_submit() and form.code.data:
        trap = Trap.query.filter_by(mac=form.code.data.replace(':', '').replace(
            ' ', '').lower()).filter(Trap.connect_expired > datetime.utcnow()).first()
        if not trap:
            flash('Muizenval niet gevonden', 'danger')
            return redirect(url_for('trap_connect'))

        trap.owner = current_user.id
        trap.connect_expired = None
        trap.connect_code = None
        db.session.commit()
        flash('Muizenval toegevoegd!', 'success')
        return redirect(url_for('traps'))

    return render_template('connect.html', form=form)
"""


@app.route('/trap/<trap_id>/update', methods=['POST', 'GET'])
@login_required
def trap_update(trap_id):
    form = UpdateTrapForm()
    trap = Trap.query.filter_by(mac=trap_id).first()
    if form.validate_on_submit():
        trap.name = form.name.data
        print(form.location.data)
        if form.location.data:
            trap.location_lat, trap.location_lon = form.location.data.split(
                ' ', 2)
        db.session.commit()
        return redirect(url_for('traps'))
    elif not trap:
        flash('Muizenval niet gevonden', 'danger')
        return redirect(url_for('traps'))
    elif request.method == 'GET':
        form.mac.data = trap.pretty_mac()
        form.name.data = trap.name
    return render_template('updatetrap.html', form=form, trap=trap)


@app.route('/trap/<trap_id>/delete')
@login_required
def trap_delete(trap_id):
    trap = Trap.query.filter_by(mac=trap_id.lower()).first()
    db.session.delete(trap)
    db.session.commit()

    return redirect(url_for('traps'))


@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html', contact=current_user.contact_class())


""" admin.html route """


@app.route("/users", methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.admin:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    form = SearchForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user == None:
            flash(
                f'Geen gebrukers gevonden met de gebruikersnaam: {form.username.data}!', 'danger')
        else:
            flash(
                f'Gebruiker gevonden met gebruikersnaam: {form.username.data}!', 'success')
            return redirect(url_for('admin_user', user_id=user.id))
    return render_template('admin.html', form=form)


""" account-admin route """


@app.route("/user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def admin_user(user_id):
    if not current_user.admin:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    form = AdminForm()
    user = User.query.filter_by(id=user_id).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    if form.validate_on_submit():
        user.admin = form.type.data == 'admin'
        db.session.commit()
        flash(f'De gebruiker {user.username} is nu een {user.type}', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.type.data = 'admin' if user.admin else 'client'
    return render_template('admin_user.html', form=form, user=user, image_file=image_file)


""" delete-user route """


@app.route("/user/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if not current_user.admin:
        flash('U mag deze website niet bereiken', 'danger')
        return redirect('/')
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'De gebruiker {user.username} werd verwijdert', 'success')
    return redirect(url_for('admin'))


""" reset user's password route """


@app.route("/user/<int:user_id>/reset", methods=['GET', 'POST'])
@login_required
def reset_user(user_id):
    if not current_user.admin:
        flash('U mag deze website niet bereiken', 'danger')
        return redirect('/')
    user = User.query.get_or_404(user_id)
    user.password = bcrypt.generate_password_hash(user.email).decode('utf-8')
    db.session.commit()
    flash(f'{user.name}\'s wachtwoord is nu zijn/haar e-mail', 'success')
    return redirect(url_for('admin'))


""" 404 not found handler """


@app.errorhandler(404)
def not_found(error):
    flash(f"Deze pagina werd niet gevonden", 'danger')
    return index()  # geen redirect om de '/bla' te houden
