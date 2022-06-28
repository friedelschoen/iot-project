from datetime import datetime
from typing import Any, Callable, Dict, Optional
from serial import Serial
from serial.tools.list_ports import comports
from .exception import RemoteException

import json
import traceback


CommandHandler = Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]


class Remote:
    commands: Dict[str, CommandHandler] = dict()
    running = True

    @staticmethod
    def list_ports():
        return comports()

    def __init__(self, baud: int):
        self.baud = baud

    def command(self, name: str):
        def inner(func: CommandHandler):
            self.commands[name] = func
            return func

        return inner

    def run(self, serial_path, timeout=1):
        serial = Serial(port=serial_path, baudrate=self.baud, timeout=timeout)
        self.running = True
        while self.running:
            command = ''
            status = ''
            params = None
            response = None
            try:
                line = serial.readline().decode(errors='ignore')
                try:
                    if line == '':
                        continue
                    if ' ' in line:
                        command, params_raw = line.split(' ', 1)
                        params = json.loads(params_raw)
                    else:
                        command = line
                        params = dict()
                except json.JSONDecodeError:
                    raise RemoteException('bad-request')

                if command not in self.commands:
                    raise RemoteException('bad-command')

                res = self.commands[command](params) or dict()

                status = 'ok'
                response = json.dumps(res)
            except RemoteException as err:
                status = err.name
            except KeyboardInterrupt:
                break
            except Exception as err:
                print(f'Error handling {command} ({params}):')
                traceback.print_exc()
                status = 'unknown'

            print(
                f'{datetime.now().strftime("%d/%m/%y %H:%M:%S")} | {command} -> { status }')
            serial.write(status.encode())
            if response is not None:
                serial.write(b' ' + response.encode())
            serial.write(b'\n')
        serial.close()

    def stop(self):
        self.running = False
