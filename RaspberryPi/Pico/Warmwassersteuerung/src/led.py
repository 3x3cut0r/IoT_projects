# imports
from machine import Pin

# load config
from src.config import get_int_value

# setup temperature sensor
led = Pin("LED", Pin.OUT)

# ==================================================
# functions
# ==================================================


# init led
def init_led():
    led.value(get_int_value("LED"))


# set led
def set_led(value):
    if int(value) == 0:
        led.value(0)
    else:
        led.value(1)
