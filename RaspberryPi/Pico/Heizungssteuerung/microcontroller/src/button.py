from machine import Pin

# load config
from src.config import load_config

config = load_config()

# setup buttons
button_temp_up = Pin(int(config["BUTTON_TEMP_UP_PIN"]), Pin.IN, Pin.PULL_UP)
button_temp_down = Pin(int(config["BUTOTN_TEMP_DOWN_PIN"]), Pin.IN, Pin.PULL_UP)


# ==================================================
# functions
# ==================================================


# check button
def check_button(button):
    return not button.value()  # return true, if button is pressed
