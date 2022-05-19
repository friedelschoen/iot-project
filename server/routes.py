import json
import os
import secrets
from datetime import datetime, timedelta

from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from .app import app, bcrypt, db, socket
from .forms import ConnectTrapForm, LoginForm, RegistrationForm, UpdateAccountForm, UpdateTrapForm
from .models import Trap, User, UserType

def clean_traps():
    query = Trap.query.filter((Trap.connect_expired < datetime.utcnow()) & (Trap.owner == None))
    i = len(query.all())
    query.delete()
    db.session.commit()
    print(f'[*] {i} traps cleaned')

@app.route("/api/update_status", methods=['POST', 'GET'])
def update_status():
    if not request.json:
        return jsonify({ "error": "invalid-json" })
    trap = Trap.query.filter_by(mac=request.json['mac']).first() 
    if not trap:
        return jsonify({ "error": "not-found" })

    trap.caught = request.json['status']
    db.session.commit()

    if trap.owner:
        socket.emit('trap-change', { 'user': trap.owner })

    return jsonify({ "error": "ok" })

@app.route("/api/search_connect", methods=['POST', 'GET'])
def search_connect():
    if not request.json:
        return jsonify({ "error": "invalid-json" })
    
    trap = Trap.query.filter_by(mac=request.json['mac']).first()
    if not trap:
        trap = Trap(mac=request.json['mac'])
        db.session.add(trap)

    trap.owner = None
    trap.connect_expired = datetime.utcnow() + timedelta(minutes=5)

    db.session.commit()

    return jsonify({ "error": "ok" })


""" index.html (home-page) route """
@app.route("/")
def index():
    return render_template('index.html')

""" about.html route """
@app.route("/about")
def about():
    return render_template('about.html', title='Over ons')

""" register.html route """
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('U bent al ingelogd', 'warning')
        return redirect('/')

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        address = f"{form.street} {form.housenumber}\n{form.zipcode} {form.place}"
        user = User(
            name=form.name.data, 
            email=form.email.data, 
            password=hashed_password,
            phone=form.phone.data,
            address = address
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
                flash('Wij zullen aanbevelen uw wachtwoord weer te veranderen', 'warning')
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
    picturepath = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picturepath)

    return picture_fn

""" account.html route """
@app.route("/user/self", methods=[ 'GET', 'POST' ])
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
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Uw profiel is bewerkt!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',  title='Profiel', image_file=image_file, form=form)


@app.route('/traps')
@login_required
def traps():
    if current_user.type == UserType.ADMIN:
        clean_traps()
        query = Trap.query.all()
    else:
        query = Trap.query.filter_by(owner=current_user.id)

    trap_json = [ { c.name: str(getattr(trap, c.name)) for c in trap.__table__.columns } for trap in query ]

    return render_template('trap.html', traps=query, trap_json=trap_json)

@app.route('/traps/connect', methods=['POST', 'GET'])
@login_required
def trap_connect():
    form = ConnectTrapForm()
    if form.validate_on_submit() and form.mac.data:
        trap = Trap.query.filter_by(mac=form.mac.data.replace(':', '').replace(' ', '')).filter(Trap.connect_expired > datetime.utcnow()).first()
        if not trap:
            flash('Muizenval niet gevonden', 'danger')
            return redirect(url_for('trap_connect'))

        trap.owner = current_user.id
        db.session.commit()
        flash('Muizenval toegevoegd!', 'success')
        return redirect(url_for('traps'))

    return render_template('connect.html', form=form)


@app.route('/trap/<trap_id>/update', methods=['POST', 'GET'])
@login_required
def trap_update(trap_id):
    form = UpdateTrapForm()
    trap = Trap.query.filter_by(mac=trap_id).first()
    if form.validate_on_submit():
        trap.name = form.name.data
        if form.email.data:
            user = User.query.filter_by(email=form.email.data).first()
            trap.owner = user.id
        db.session.commit()
        return redirect(url_for('traps'))
    elif not trap:
        flash('Muizeval niet gevonden', 'danger')
        return redirect(url_for('traps'))
    elif request.method == 'GET':
        form.mac.data = trap.mac
        form.name.data = trap.name
    return render_template('updatetrap.html', form=form, trap=trap)

@app.route('/trap/<trap_id>/delete')
@login_required
def trap_delete(trap_id):
    trap = Trap.query.filter_by(mac=trap_id).first()
    db.session.delete(trap)
    db.session.commit()
    
    return redirect(url_for('traps'))

""" 404 not found handler """
@app.errorhandler(404)
def not_found(error):
    flash(f"Deze pagina werd niet gevonden", 'danger')
    return index() # geen redirect om de '/bla' te houden
