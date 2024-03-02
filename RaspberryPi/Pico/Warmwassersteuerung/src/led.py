# imports
from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from src.log import log
from src.config import config  # Config() instance

# ==================================================
# functions
# ==================================================


# set led
def set_led(value):
    try:
        led = Pin("LED", Pin.OUT)
        led.value(bool(value))
        if value:
            log("INFO", f"LED: on")
        else:
            log("INFO", f"LED: off")

    except Exception as e:
        log("ERROR", f"LED: could not be set: {e}")


# init led
def init_led():
    set_led(config.get_bool_value("LED", True))
