from machine import Pin

# load config
from src.config import get_value

# setup buttons
button_temp_up = Pin(int(get_value("BUTTON_TEMP_UP_PIN")), Pin.IN, Pin.PULL_UP)
button_temp_down = Pin(int(get_value("BUTOTN_TEMP_DOWN_PIN")), Pin.IN, Pin.PULL_UP)


# ==================================================
# functions
# ==================================================


# check button
def check_button(button):
    return not button.value()  # return true, if button is pressed
