# imports
from enum import Enum
import time
from src.button import check_button
from src.config import load_config, save_config, get_value, set_value
from src.lcd import (
    set_backlight,
    show_cursor,
    blink_cursor,
    clear_lcd,
    print_lcd,
    print_lcd_char,
)
from src.relay import open_relay, close_relay
from src.temp import read_temp


# define temp change category
class TempChangeCategory(Enum):
    LOW_TEMP = 1
    MEDIUM_TEMP = 2
    HIGH_TEMP = 3


# ==================================================
# functions
# ==================================================


# categorize temp change
def categorize_temp_change(temp_change):
    if abs(temp_change) >= float(get_value("temp_change_high_threshold")):
        print_lcd(2, 0, "Temperatur      HIGH")
        print_lcd_char(2, 11, (0 if temp_change > 0 else 1))
        return "HIGH_TEMP"  # TempChangeCategory.HIGH_TEMP
    elif abs(temp_change) >= float(get_value("temp_change_medium_threshold")):
        print_lcd(2, 0, "Temperatur    MEDIUM")
        print_lcd_char(2, 11, (0 if temp_change > 0 else 1))
        return "MEDIUM_TEMP"  # TempChangeCategory.MEDIUM_TEMP
    else:
        print_lcd(2, 0, "Temperatur       LOW")
        print_lcd_char(2, 11, (0 if temp_change > 0 else 1))
        return "LOW_TEMP"  # return TempChangeCategory.LOW_TEMP


# adjust update time based on temp category
def adjust_update_time_based_on_temp_category(update_time):
    if get_value("temp_change_category") == "HIGH_TEMP":
        return int(
            int(get_value("update_time")) / 2.0
        )  # temp measurement takes place very often
    elif get_value("temp_change_category") == "MEDIUM_TEMP":
        return int(
            int(get_value("update_time")) / 1.3
        )  # temp measurement takes place more often
    elif get_value("temp_change_category") == "LOW_TEMP":
        return int(
            int(get_value("update_time")) / 1.0
        )  # temp measurement takes place normally


# update current temp on lcd
def update_temp():
    # read temp
    read_temp()

    # load config
    config = load_config()

    # print temp on lcd
    current_temp_string = str("{} \337C".format(config["current_temp"]))
    temp_pos = int(config["LCD_COLS"]) - len(current_temp_string)
    print_lcd(0, 0, ("Aktuell:"))
    print_lcd(0, temp_pos, current_temp_string)


# print nominal temp
def print_nominal_temp():
    # load config
    config = load_config()

    # set lower and upper bounds for nominal temperatures
    nominal_min_temp = max(0.0, min(120.0, float(config["nominal_min_temp"])))
    nominal_max_temp = max(
        nominal_min_temp, min(120.0, float(config["nominal_max_temp"]))
    )

    # format the nominal temperature string
    nominal_temp = f"{nominal_min_temp:.1f} - {nominal_max_temp:.1f} \337C"

    # calculate the position for displaying the temperature
    temp_pos = int(config["LCD_COLS"]) - len(nominal_temp)

    # print the formatted temperature on LCD
    print_lcd(1, 0, "Soll:")
    print_lcd(1, temp_pos, nominal_temp)


# set relay
def set_relay(pin, time):
    # load config
    config = load_config()

    # Schalte nur, wenn die Temperatur ausgelesen werden kann
    if 0 <= int(config["config['current_temp']"]) <= 150:
        if int(pin) == int(config["RELAY_OPEN_PIN"]):
            print_lcd(3, 0, "\357ffne Ventil     >>>")
            open_relay(time)
        elif int(pin) == int(config["RELAY_CLOSE_PIN"]):
            print_lcd(3, 0, "schlie\342e Ventil: <<<")
            close_relay(time)
    else:
        print_lcd(3, 0, "Fehler: Temp Fehler!")
        time.sleep(2)


# open relay depending on temp
def open_relay(time):
    # load config
    config = load_config()

    if int(config["current_temp"]) < int(config["nominal_min_temp"]):
        # increase temp
        set_relay(int(config["RELAY_OPEN_PIN"]), time)
    elif int(config["current_temp"]) > int(config["nominal_max_temp"]):
        # decrease temp
        set_relay(int(config["RELAY_CLOSE_PIN"]), time)
    else:
        # do nothing
        print_lcd(3, 0, "Soll Temp erreicht !")


# update nominal temp
def update_nominal_temp(button_pin):
    # load config
    config = load_config()

    button_long = 0
    rate = 0.1

    # while button is pressed
    while check_button(button_pin):
        # increase temp on temp up button
        if int(button_pin) == int(config["BUTTON_TEMP_UP_PIN"]):
            if rate >= 3:
                print_lcd(2, 0, "TempUp Pressed   +++")
            elif rate >= 0.5:
                print_lcd(2, 0, "TempUp Pressed    ++")
            else:
                print_lcd(2, 0, "TempUp Pressed     +")
            config["nominal_min_temp"] += rate
            config["nominal_max_temp"] += rate

        # decrease temp on temp down button
        elif int(button_pin) == int(config["BUTTON_TEMP_DOWN_PIN"]):
            if rate >= 3:
                print_lcd(2, 0, "TempDown Pressed ---")
            elif rate >= 0.5:
                print_lcd(2, 0, "TempDown Pressed  --")
            else:
                print_lcd(2, 0, "TempDown Pressed   -")
            config["nominal_min_temp"] -= rate
            config["nominal_max_temp"] -= rate

        # save config
        save_config(config)

        # print nominal temp
        print_nominal_temp()

        time.sleep(0.5)
        button_long += 1
        if button_long == 5:
            rate = 1
        elif button_long == 10:
            rate = 1  # rate = 5 -> was to fast


# check buttons
def check_buttons():
    # load config
    config = load_config()

    # update nomianl temp
    update_nominal_temp(int(config["BUTTON_TEMP_UP_PIN"]))
    update_nominal_temp(int(config["BUTTON_TEMP_DOWN_PIN"]))


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
def update_timer(secs, message="WARTE:"):
    time = format_time(secs)
    cursor = 20 - len(time)

    print_lcd(3, 0, message)
    print_lcd(3, cursor, time)


# wait start
def wait_start(secs):
    previous_millis = time.ticks_ms()
    interval = 1000

    while secs >= 0:
        current_millis = time.ticks_ms()
        if time.ticks_diff(current_millis, previous_millis) > interval:
            # check buttons
            check_buttons()

            # temp update on interval
            if secs % get_value("temp_update_interval") == 0:
                update_temp()

            # update timer
            update_timer(secs, "STARTE IN:")

            # decrease secs
            secs -= 1
            previous_millis = current_millis
