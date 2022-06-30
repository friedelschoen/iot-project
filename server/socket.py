from datetime import datetime
import os
import random
from typing import Dict
from flask import request, jsonify
from flask_login import current_user
from flask_socketio import emit

from .app import app, db, socket, domain
from .models import Statistic, Trap, User

current_user: User

sockets: Dict[int, str] = {}

accuracy_min = 80


def make_token():
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for _ in range(16))


@app.post("/api/hello")
def register_trap():
    req = request.get_json(True)
    if not req:
        return jsonify(dict(error='invalid-request'))

    res = dict()
    if 'token' not in req or not req['token'] or not Trap.query.filter_by(token=req['token']).first():
        while True:
            token = make_token()
            if not Trap.query.filter_by(token=token).first():
                break

        trap = Trap(token=token, last_status=datetime.now())
        db.session.add(trap)
        db.session.commit()
        res['token'] = token
    else:
        trap: Trap = Trap.query.filter_by(token=req['token']).first()

    res['location_search'] = trap.location_search

    if 'domain' not in req or req['domain'] != domain:
        res['domain'] = domain

    return jsonify(res)


@app.post("/api/update")
def update_status():
    req = request.get_json(True)
    if not req:
        return jsonify(dict(error='invalid-request'))

    trap: Trap = Trap.query.filter_by(token=req['token']).first()
    if not trap:
        return jsonify(dict(error='invalid-token'))

    if not trap.caught and req['trap']:
        if trap.owner:
            stc = Statistic(user=trap.owner, date=datetime.now())
            db.session.add(stc)
        # os.system(
        #   f"echo -e -s \"Je muizenval '{trap.name}' heeft iets gevangen!\\n\\nGroetjes uw Team Benni!\" | mailx -s 'Muizenval werd geactiveerd' {trap.owner_class().email}")        # type: ignore
        print('Email sent!')

    trap.last_status = datetime.now()
    trap.caught = req['trap']
    trap.battery = req['battery']
    trap.temperature = req['temperature']
    trap.charging = req['charging']
    trap.location_searching = req['searching']
    if trap.location_search:
        trap.location_satellites = req['satellites']
        if req['accuracy'] != 0:
            trap.location_acc = req['accuracy']
            trap.location_lat = req['latitude']
            trap.location_lon = req['longitude']

    db.session.commit()

    if trap.owner and trap.owner in sockets:
        socket.emit('trap-change', trap.to_json(), to=sockets[trap.owner])
        socket.emit('statistics', make_statistics(
            trap.owner), to=sockets[trap.owner])

    return jsonify(dict(location_search=trap.location_search))


def make_statistics(user: int):
    year = datetime.now().year
    months = [0] * 12
    stc: Statistic
    for stc in Statistic.query.filter_by(user=user):
        if stc.date.year == year:
            months[stc.date.month-1] += 1

    return months


@socket.on('connect')
def socket_connect():
    if not current_user.is_authenticated:
        return

    sockets[current_user.id] = request.sid  # type: ignore

    for trap in Trap.query.filter_by(owner=current_user.id):
        emit('trap-change', trap.to_json())

    emit('statistics', make_statistics(current_user.id))


@socket.on('disconnect')
def socket_disconnect():
    if not current_user.is_authenticated:
        return

    if current_user.id in sockets:
        del sockets[current_user.id]


@socket.on('token')
def socket_token(token):
    if not token or not current_user.is_authenticated:
        return

    trap: Trap = Trap.query.filter_by(token=token).first()
    if not trap or trap.owner == current_user.id:
        return

    trap.owner = current_user.id
    trap.owned_date = datetime.now()
    db.session.commit()

    emit('trap-change', trap.to_json())


@socket.on('location-search')
def socket_location(data):
    if not data or not current_user.is_authenticated:
        return

    print(data['id'])
    trap: Trap = Trap.query.get(data['id'])
    if not trap or trap.owner != current_user.id:
        return

    trap.location_search = data['search']
    db.session.commit()

    emit('trap-change', trap.to_json())


@socket.on('delete')
def socket_delete(data):
    if not data or not current_user.is_authenticated:
        return

    print(data['id'])
    trap: Trap = Trap.query.get(data['id'])
    if not trap or trap.owner != current_user.id:
        return

    trap.owner = False
    db.session.commit()


@socket.on('name')
def socket_name(data):
    if not data or not current_user.is_authenticated:
        return

    print(data['id'])
    trap: Trap = Trap.query.get(data['id'])
    if not trap or trap.owner != current_user.id:
        return

    trap.name = data['name']
    db.session.commit()

    emit('trap-change', trap.to_json())
