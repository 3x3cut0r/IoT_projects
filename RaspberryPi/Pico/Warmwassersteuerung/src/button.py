from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from src.config import config  # Config() instance

# setup buttons
buttons_activated = config.get_bool_value("buttons_activated")
if buttons_activated:
    BUTTON_TEMP_UP_PIN = config.get_int_value("BUTTON_TEMP_UP_PIN", 2)
    BUTTON_TEMP_DOWN_PIN = config.get_int_value("BUTOTN_TEMP_DOWN_PIN", 3)
    button_temp_up = Pin(BUTTON_TEMP_UP_PIN, Pin.IN, Pin.PULL_UP)
    button_temp_down = Pin(BUTTON_TEMP_DOWN_PIN, Pin.IN, Pin.PULL_UP)

# ==================================================
# functions
# ==================================================


# check button
def check_button(button):
    if buttons_activated:
        try:
            if button == BUTTON_TEMP_UP_PIN:
                return not button_temp_up.value()  # return true, if button is pressed
            elif button == BUTTON_TEMP_DOWN_PIN:
                return not button_temp_down.value()  # return true, if button is pressed
            else:
                return False
        except:
            return False
    else:
        return False
