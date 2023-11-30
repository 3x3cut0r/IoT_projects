# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
from machine import Pin

# load config
from src.config import load_config

config = load_config()

# setup relays
relay_open_pin = Pin(int(config["RELAY_OPEN_PIN"]), Pin.OUT)
relay_close_pin = Pin(int(config["RELAY_CLOSE_PIN"]), Pin.OUT)

# ==================================================
# functions
# ==================================================


# init relays
def init_relays():
    relay_open_pin.value(0)
    relay_close_pin.value(0)


# activate relay
def activate_relay(relay):
    relay.value(1)  # activate relay


# deactivate relay
def deactivate_relay(relay):
    relay.value(0)  #  deactivate relay


# open relay
def open_relay(time=1):
    activate_relay(relay_open_pin)
    time.sleep(time)  # time in seconds
    deactivate_relay(relay_open_pin)


# close relay
def close_relay(time=1):
    activate_relay(relay_close_pin)
    time.sleep(time)  # time in seconds
    deactivate_relay(relay_close_pin)
