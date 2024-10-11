# imports
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from src.log import log
from src.config import config  # Config() instance

# ==================================================
# functions
# ==================================================


# init relays
def init_relays():
    relay_open_pin = Pin(config.get_int_value("RELAY_OPEN_PIN", 14), Pin.OUT)
    relay_close_pin = Pin(config.get_int_value("RELAY_CLOSE_PIN", 15), Pin.OUT)
    relay_open_pin.value(0)
    relay_close_pin.value(0)


# activate relay
def activate_relay(relay_pin):
    relay = Pin(relay_pin, Pin.OUT)
    relay.value(1)  # activate relay


# deactivate relay
def deactivate_relay(relay_pin):
    relay = Pin(relay_pin, Pin.OUT)
    relay.value(0)  # deactivate relay


# open relay
async def open_relay(relay_time=config.get_int_value("relay_time", 1200)):
    relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
    log("INFO", f"open_relay({relay_time}): activate")
    activate_relay(relay_open_pin)
    await asyncio.sleep_ms(relay_time)  # time in milliseconds
    deactivate_relay(relay_open_pin)
    log("INFO", "open_relay(): deactivate")


# close relay
async def close_relay(relay_time=config.get_int_value("relay_time", 1200)):
    relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)
    log("INFO", f"close_relay({relay_time}): activate")
    activate_relay(relay_close_pin)
    await asyncio.sleep_ms(relay_time)  # time in milliseconds
    deactivate_relay(relay_close_pin)
    log("INFO", "close_relay(): deactivate")
