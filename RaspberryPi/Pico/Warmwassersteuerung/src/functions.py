# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
from src.button import check_button
from src.config import save_config, get_value, get_int_value, get_float_value, set_value
from src.lcd import print_lcd, print_lcd_char
from src.relay import open_relay, close_relay
from src.temp import get_temp

# ==================================================
# functions
# ==================================================


# categorize temp change
def categorize_temp_change(temp_change=0.0):
    if abs(float(temp_change)) >= float(
        get_float_value("temp_change_high_threshold", 1.0)
    ):
        print_lcd(2, 0, "Temperatur      HIGH")
        print_lcd_char(2, 11, (0 if float(temp_change) > 0 else 1))
        return "HIGH"  # TempChangeCategory.HIGH
    elif abs(float(temp_change)) >= float(
        get_float_value("temp_change_medium_threshold", 0.3)
    ):
        print_lcd(2, 0, "Temperatur    MEDIUM")
        print_lcd_char(2, 11, (0 if float(temp_change) > 0 else 1))
        return "MEDIUM"  # TempChangeCategory.MEDIUM
    else:
        print_lcd(2, 0, "Temperatur       LOW")
        print_lcd_char(2, 11, (0 if float(temp_change) > 0 else 1))
        return "LOW"  # return TempChangeCategory.LOW


# adjust relay time based on temp category
def adjust_relay_time_based_on_temp_category():
    if get_value("temp_change_category", "LOW") == "HIGH":
        return int(
            get_int_value("relay_time", 2000) * 0.3
        )  # shorter opening time for rapid temperature changes
    elif get_value("temp_change_category", "LOW") == "MEDIUM":
        return int(
            get_int_value("relay_time", 2000) * 0.6
        )  # moderate opening time for normal temperature changes
    # elif get_value("temp_change_category") == "LOW":
    else:
        return get_int_value(
            "relay_time", 2000
        )  # normal opening time for slow temperature changes


# adjust update time based on temp category
def adjust_update_time_based_on_temp_category():
    if get_value("temp_change_category", "LOW") == "HIGH":
        return int(
            get_int_value("update_time", 120) / 2.0
        )  # temp measurement takes place very often
    elif get_value("temp_change_category", "LOW") == "MEDIUM":
        return int(
            get_int_value("update_time", 120) / 1.3
        )  # temp measurement takes place more often
    # elif get_value("temp_change_category") == "LOW":
    else:
        return get_int_value(
            "update_time", 120
        )  # temp measurement takes place normally


# convert utf-8 characters to HD44780 characters
# get dual number from the HD44780 table: https://de.wikipedia.org/wiki/HD44780#Schrift_und_Zeichensatz
# convert dual number to octal number: https://www.arndt-bruenner.de/mathe/scripts/Zahlensysteme.htm
def convert_utf8(string=""):
    replacements = {
        "ß": "\u00DF",  # Unicode for ß
        "°": "\u00B0",  # Unicode for °
        "ä": "\u00E4",  # Unicode for ä
        "ö": "\u00F6",  # Unicode for ö
        "ü": "\u00FC",  # Unicode for ü
    }
    for original, replacement in replacements.items():
        string = string.replace(original, replacement)
    return string


# update current temp on lcd
def update_temp():
    # read temp
    get_temp()

    # print temp on lcd
    current_temp_string = str(
        "{:.1f} °C".format(get_float_value("current_temp", -127.0, 1))
    )
    print(f"INFO: update_temp({convert_utf8(current_temp_string)})")

    temp_pos = get_int_value("LCD_COLS", 4) - len(current_temp_string)
    print_lcd(0, 0, "Aktuell:")
    print_lcd(0, temp_pos, current_temp_string)


# print nominal temp
def print_nominal_temp():
    # set lower and upper bounds for nominal temperatures
    nominal_min_temp = max(0.0, min(120.0, get_float_value("nominal_min_temp", 42.0)))
    nominal_max_temp = max(
        nominal_min_temp, min(120.0, get_float_value("nominal_max_temp", 55.0))
    )

    # format the nominal temperature string
    nominal_temp = f"{nominal_min_temp:.1f} - {nominal_max_temp:.1f} °C"

    # calculate the position for displaying the temperature
    temp_pos = get_int_value("LCD_COLS", 4) - len(nominal_temp)

    # print the formatted temperature on LCD
    print_lcd(1, 0, "Soll:")
    print_lcd(1, temp_pos, nominal_temp)


# set relay
def set_relay(pin, relay_time):
    # Schalte nur, wenn die Temperatur ausgelesen werden kann
    if 0 < get_float_value("current_temp", -127.0) <= 120:
        if int(pin) == get_int_value("RELAY_OPEN_PIN", 14):
            print_lcd(3, 0, "öffne Ventil     >>>")
            open_relay(relay_time)
        elif int(pin) == get_int_value("RELAY_CLOSE_PIN", 15):
            print_lcd(3, 0, "schließe Ventil: <<<")
            close_relay(relay_time)
    else:
        print_lcd(3, 0, "Fehler: Temp Fehler!")
        time.sleep(2)


# open relays depending on temp
def open_relays(time=get_int_value("relay_time", 2000)):
    print(f"INFO: open_relays({time})")

    if get_float_value("current_temp", -127.0) < get_float_value(
        "nominal_min_temp", 42.0
    ):
        # increase temp
        set_relay(get_int_value("RELAY_OPEN_PIN", 14), time)
    elif get_float_value("current_temp", -127.0) > get_float_value(
        "nominal_max_temp", 55.0
    ):
        # decrease temp
        set_relay(get_int_value("RELAY_CLOSE_PIN", 15), time)
    else:
        # do nothing
        print_lcd(3, 0, "Soll Temp erreicht !")


# update nominal temp
def update_nominal_temp(button_pin):
    button_long = 0
    rate = 0.1

    # while button is pressed
    while check_button(button_pin):
        # increase temp on temp up button
        if int(button_pin) == get_int_value("BUTTON_TEMP_UP_PIN", 2):
            if rate >= 3:
                print_lcd(2, 0, "TempUp Pressed   +++")
            elif rate >= 0.5:
                print_lcd(2, 0, "TempUp Pressed    ++")
            else:
                print_lcd(2, 0, "TempUp Pressed     +")
            set_value(
                "nominal_min_temp", (get_float_value("nominal_min_temp", 42.0)) + rate
            )
            set_value(
                "nominal_max_temp", (get_float_value("nominal_max_temp", 55.0)) + rate
            )

        # decrease temp on temp down button
        elif int(button_pin) == get_int_value("BUTTON_TEMP_DOWN_PIN", 3):
            if rate >= 3:
                print_lcd(2, 0, "TempDown Pressed ---")
            elif rate >= 0.5:
                print_lcd(2, 0, "TempDown Pressed  --")
            else:
                print_lcd(2, 0, "TempDown Pressed   -")
            set_value(
                "nominal_min_temp", (get_float_value("nominal_min_temp", 42.0)) - rate
            )
            set_value(
                "nominal_max_temp", (get_float_value("nominal_max_temp", 55.0)) - rate
            )

        # print nominal temp
        print_nominal_temp()

        time.sleep(0.5)
        button_long += 1
        if button_long == 5:
            rate = 1
        elif button_long == 10:
            rate = 1  # rate = 5 -> was to fast

    # save config
    save_config()


# check buttons
def check_buttons():
    # update nomianl temp
    update_nominal_temp(get_int_value("BUTTON_TEMP_UP_PIN", 2))
    update_nominal_temp(get_int_value("BUTTON_TEMP_DOWN_PIN", 3))


# format time
def format_time(secs):
    hours = int(secs / 3600)
    mins = int((secs % 3600) / 60)
    secs = int(secs % 60)
    if hours > 0:
        return "{:02d}h {:02d}m {:02d}s".format(hours, mins, secs)
    else:
        return "{:02d}m {:02d}s".format(mins, secs)


# update timer
def update_timer(secs, message="Warte:"):
    print(f"INFO: update_timer({secs})")

    time = format_time(secs)
    cursor = 20 - len(time)

    print_lcd(3, 0, message)
    print_lcd(3, cursor, time)


# wait start
def wait_start(secs):
    print(f"INFO: wait start ({secs})")

    previous_millis = time.ticks_ms()
    interval = 1000

    while secs >= 0:
        current_millis = time.ticks_ms()
        if time.ticks_diff(current_millis, previous_millis) > interval:
            # check buttons
            check_buttons()

            # temp update on interval
            if secs % get_int_value("temp_update_interval", 120) == 0:
                update_temp()

            # update timer
            update_timer(secs, "Starte in:")

            # decrease secs
            secs -= 1
            previous_millis = current_millis
