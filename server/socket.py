from datetime import datetime, timedelta
import random
from typing import Dict
from flask import request, jsonify
from flask_login import current_user
from flask_socketio import emit, Namespace

from .app import app, db, socket, domain
from .models import Trap, User

current_user: User

sockets: Dict[int, Namespace] = {}


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
        trap = Trap(token=token)
        db.session.add(trap)
        db.session.commit()
        res['token'] = token

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

    trap.caught = req['trap']
    trap.battery = req['battery']
    trap.temperature = req['temperature']
    trap.charging = req['charging']
    trap.location_lat = req['latitude']
    trap.location_lon = req['longitude']
    trap.location_acc = req['accuracy']
    trap.location_satellites = req['satellites']

    db.session.commit()

    if trap.owner and trap.owner in sockets:
        sockets[trap.owner].emit('trap-change', trap.to_json())

    return jsonify(dict())


"""@app.route("/api/search_connect", methods=['POST', 'GET'])
def search_connect():
    if not request.json:
        return jsonify({"error": "invalid-json"})
    # if not validate_mac(request.json['mac']):
     #   return jsonify({"error": "invalid-mac"})

    mac = request.json['mac'].lower()

    trap = Trap.query.filter_by(mac=mac).first()
    if not trap:
        trap = Trap(mac=mac)
        db.session.add(trap)

    code = ""
    while True:
        code = ''.join(random.choice(
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(5))
        if not Trap.query.filter_by(connect_code=code).first():
            break

    trap.owner = None
    trap.connect_expired = datetime.utcnow() + timedelta(minutes=5)
    trap.connect_code = code

    db.session.commit()

    return jsonify({"error": "ok"})
"""


@socket.on('connect')
def socket_connect():
    if not current_user.is_authenticated:
        return

    sockets[current_user.id] = request.namespace  # type: ignore

    for trap in Trap.query.filter_by(owner=current_user.id):
        emit('trap-change', trap.to_json())


@socket.on('disconnect')
def socket_disconnect():
    if not current_user.is_authenticated:
        return

    del sockets[current_user.id]


@socket.on('token')
def socket_token(token):
    if not token or not current_user.is_authenticated:
        return

    for trap in Trap.query.filter_by(token=token):
        emit('trap-change', trap.to_json(True))
