# imports
from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from src.config import config  # Config() instance

# ==================================================
# functions
# ==================================================


# init led
def init_led():
    led = Pin("LED", Pin.OUT)
    led.value(config.get_int_value("LED", True))


# set led
def set_led(value):
    led = Pin("LED", Pin.OUT)
    led.value(bool(value))
