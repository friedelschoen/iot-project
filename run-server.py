from server.app import socket, app

if __name__ == '__main__':
    socket.run(app, "0.0.0.0", 5000, debug=True)
