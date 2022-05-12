from machine import Pin
from time import sleep
import config
import urequests as requests

urlstatus = f"http://{config.SERVER}:{config.PORT}{config.ENDPOINTSTATUS}"
urlconnect =  f"http://{config.SERVER}:{config.PORT}{config.ENDPOINTCONNECT}"

led = Pin(23, Pin.OUT)
trap = Pin(15, Pin.IN, Pin.PULL_DOWN)
connectbutton = Pin(4, Pin.IN, Pin.PULL_DOWN)

state = False
#esp32.wake_on_ext1(pins = (button, button2), level = esp32.WAKEUP_ANY_HIGH)

while connection.isconnected():
    print(connectbutton.value())
    print(trap.value())
    new_state = trap.value()
    led.value(new_state)

    if state != new_state:
        response = requests.post(urlstatus, json={ "mac": config.MAC_ADDRESS, "state": new_state })
        answer = response.json()
        state = new_state
        print(answer)

    if connectbutton.value():
        response = requests.post(urlconnect, json={ "mac": config.MAC_ADDRESS })
        answer = response.json()
        print(answer)

    sleep(config.SLEEP_TIME)

#deepsleep()
