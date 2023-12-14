from machine import Pin

# load config
from src.config import get_int_value

# setup buttons
button_temp_up = Pin(get_int_value("BUTTON_TEMP_UP_PIN", 2), Pin.IN, Pin.PULL_UP)
button_temp_down = Pin(get_int_value("BUTOTN_TEMP_DOWN_PIN", 3), Pin.IN, Pin.PULL_UP)


# ==================================================
# functions
# ==================================================


# check button
def check_button(button):
    try:
        if button == get_int_value("BUTTON_TEMP_UP_PIN", 2):
            return not button_temp_up.value()  # return true, if button is pressed
        elif button == get_int_value("BUTOTN_TEMP_DOWN_PIN", 3):
            return not button_temp_down.value()  # return true, if button is pressed
        else:
            return False
    except:
        return False
