# REPOSITORY VOOR ONS IOT-PROJECT (5GRONINGEN)

> Hamdi Hassan, Loes Hoogstra, Gerco van Woudenberg, Friedel Schon

## De server runnen

Dit is een dev-server, dus run je met `debug=True`-flag!

**Deze repository clonen:**
```
$ git clone https://github.com/friedelschoen/muizenval.tk/
```

**Alle afhankelijkheden installeren:**
```
$ pip3 install flask wtforms flask_sqlalchemy flask-wtf email_validator flask-bcrypt flask-login pillow flask_socketio simple-websocket gevent-websocket
```

**Is de database leeg? Test-gebruikers toevoegen:**
```
$ python3 add-user.py
```

Volgende gebuikers worden toegevoegd:
| E-Mail             | Wachtwoord | Rechten |
| ------------------ | ---------- | ------- |
| boer@muizenval.tk  | `hallo`    | cliënt  |
| admin@muizenval.tk | `hallo`    | admin   |

**De server runnen:**
```
$ python3 run-server.py
```

**Geen muizenval bij de hand? Interactieve test-muizenval proberen:**
```
$ python3 test-client.py
```

## Known issues

- op Anaconda-python werkt niks (flask zou gewoon ophangen), dus gebruik de officiële Python-versie