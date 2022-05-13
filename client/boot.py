import sys
import config
import network
from time import sleep
from machine import Pin, ADC

led2 = Pin(2, Pin.OUT)

connection = network.WLAN(network.STA_IF)

def connect():

    if connection.isconnected():
        print("Already connected")
        led2.on()
        return

    connection.active(True)
    connection.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    retry = 0
    while not connection.isconnected():  # wait until connection is complete
        if retry == 10:  # try 10 times
            sys.exit("Could not establish connection, check your settings")
        retry += 1

        sleep(1)  # check again in a sec

    # no exit, we have a connection!
    print("Connection established")
    led2.on()


if __name__ == "__main__":
    connect()