import sys

from server.app import socket, app

if len(sys.argv) > 1:
    if not sys.argv[1].isnumeric():
        print(f'Usage: {sys.argv[0]} [port=80]')
        exit(1)
    port = int(sys.argv[1])
else:
    port = 80

socket.run(app, "0.0.0.0", port, debug=True)
