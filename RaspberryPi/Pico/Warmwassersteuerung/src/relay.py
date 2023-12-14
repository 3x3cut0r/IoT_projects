# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
from machine import Pin

# load config
from src.config import get_int_value

# setup relays
relay_open_pin = Pin(get_int_value("RELAY_OPEN_PIN", 14), Pin.OUT)
relay_close_pin = Pin(get_int_value("RELAY_CLOSE_PIN", 15), Pin.OUT)

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
def open_relay(relay_time=get_int_value("relay_time", 2000)):
    activate_relay(relay_open_pin)
    time.sleep_ms(relay_time)  # time in seconds
    deactivate_relay(relay_open_pin)


# close relay
def close_relay(relay_time=get_int_value("relay_time", 2000)):
    activate_relay(relay_close_pin)
    time.sleep_ms(relay_time)  # time in seconds
    deactivate_relay(relay_close_pin)
