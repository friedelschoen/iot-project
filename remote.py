from threading import Thread
from time import sleep
import tkinter as tk
from tkinter import Button, OptionMenu, StringVar, Tk, Label
from http.client import HTTPConnection
from typing import Optional

from remote import Remote

import json
import sys
import asyncio
import websockets


WEBSOCKET_PORT = 1612

client = HTTPConnection('localhost', 5000)
remote = Remote(115200)
token: Optional[str] = None


@remote.command("set_token")
def set_token(req):
    global token
    token = req['token']


@remote.command("send")
def send_http(params):
    method, endpoint, body = params["method"], params["endpoint"], params["body"]

    print(body)

    client.request(method, endpoint, json.dumps(body))
    res = client.getresponse()
    response = json.load(res)

    print(response)

    return dict(code=res.status, body=response)


token = 'abcdefghijklmnoq'


async def websocket_handler(ws, _):
    if await ws.recv() == 'token':
        if token:
            await ws.send(token)
        else:
            await ws.send(None)
    await ws.close()


class RemoteWindow(Tk):
    running = False
    closed = False
    disconnecting = False

    def __init__(self):
        super().__init__()

        self.title('Team Benni - Remote')
        self.geometry('500x100')
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
#        self.columnconfigure(2, weight=3)

        self.devices = Remote.list_ports()
        self.device_names = [
            f'{p.name} ({p.description})' for p in self.devices]

        self.dev_var = StringVar(self, self.device_names[0])

        self.label = Label(self, text='Not connected')
        self.label['anchor'] = tk.CENTER
        self.label.grid(column=0, row=0, sticky=tk.W,
                        padx=5, pady=5, columnspan=2)

        self.dev_label = Label(self, text='Device:')
        self.dev_label.grid(column=0, row=1, sticky=tk.E, padx=5, pady=5)

        self.dev_menu = OptionMenu(self, self.dev_var, *self.device_names)
        self.dev_menu.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        self.connect_button = Button(
            self, text="Connect", command=self.on_connect)
        self.connect_button.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)

    async def run_websocket(self):
        async with websockets.serve(websocket_handler, '0.0.0.0',  # type: ignore
                                    WEBSOCKET_PORT):
            while self.running:
                await asyncio.sleep(1)

    def on_connect(self):
        if self.disconnecting:
            return
        self.running = not self.running
        if self.running:
            port = self.devices[self.device_names.index(self.dev_var.get())]

            self.websocket_thread = Thread(
                target=lambda: asyncio.run(self.run_websocket()))
            self.remote_thread = Thread(
                target=lambda: remote.run(port.device))

            self.websocket_thread.start()
            self.remote_thread.start()

            self.label['text'] = f'Connected to {port.name}'
            if port.description != 'n/a':
                self.label['text'] += f' ({port.description})'
            self.connect_button['text'] = 'Disconnect'
        else:
            remote.stop()
            self.disconnecting = True

            self.connect_button['text'] = 'Disconnecting...'

    def on_close(self):
        if self.running:
            self.on_connect()

        self.closed = True

    def run(self):
        while not self.closed or self.disconnecting:
            if self.disconnecting and not self.remote_thread.is_alive() and not self.websocket_thread.is_alive():
                self.label['text'] = 'Not connected'
                self.connect_button['text'] = 'Connect'
                self.disconnecting = False

            sleep(0.1)
            self.update()


if __name__ == "__main__":
    win = RemoteWindow()
    win.run()
