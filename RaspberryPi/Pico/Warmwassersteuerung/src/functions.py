# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from src.log import log
from src.button import check_button
from src.config import config  # Config() instance
from src.lcd import print_lcd, print_lcd_char
from src.relay import open_relay, close_relay
from src.temp import temp_sensor  # TemperatureSensor() instance

# ==================================================
# functions
# ==================================================


# categorize temp change
def categorize_temp_change(temp_change=0.0):
    # load config
    high_threshold = config.get_float_value("temp_change_high_threshold_temp", 1.0)
    # medium_threshold = config.get_float_value("temp_change_medium_threshold", 0.3)
    
    abs_temp_change = abs(temp_change)

    if abs_temp_change >= high_threshold:
        category = "HIGH"  # TempChangeCategory.HIGH
    # elif abs_temp_change >= medium_threshold:
    #     category = "MEDIUM"  # TempChangeCategory.MEDIUM
    else:
        category = "LOW"  # TempChangeCategory.LOW

    arrow_direction = 0 if temp_change > 0 else 1
    print_lcd(2, 0, f"Temperatur   {category}")
    print_lcd_char(2, 11, arrow_direction)

    return category


# adjust relay time based on temp category
def adjust_relay_time_based_on_temp_category():
    # load config
    temp_category = config.get_value("temp_change_category", "LOW")
    relay_time = config.get_int_value("relay_time", 2000)

    if temp_category == "HIGH":
        return int(relay_time * 0.3)  # shorter opening time for rapid temperature changes
    # elif temp_category == "MEDIUM":
    #     return int(relay_time * 0.6)  # moderate opening time for normal temperature changes
    else:
        return relay_time  # normal opening time for slow temperature changes


# adjust update time based on temp category
def adjust_update_time_based_on_temp_category():
    # load config
    temp_category = config.get_value("temp_change_category", "LOW")
    update_time = config.get_int_value("update_time", 120)

    if temp_category == "HIGH":
        return int(update_time * config.get_float_value("temp_change_high_threshold_multiplier", 0.5))  # temp measurement takes place very often
    # elif temp_category == "MEDIUM":
    #     return return int(update_time * config.get_float_value("temp_change_medium_threshold_multiplier", 0.75))  # temp measurement takes place more often
    else:
        return update_time  # temp measurement takes place normally


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
    # read and set temp
    temp_sensor.get_temp()

    # get current temperature and LCD columns once
    current_temp = config.get_float_value("current_temp", -127.0, 1)
    lcd_cols = config.get_int_value("LCD_COLS", 4)

    # format the temperature string
    current_temp_string = f"{current_temp:.1f} °C"
    current_temp_string_utf8 = convert_utf8(current_temp_string)

    log("INFO", f"update_temp({current_temp_string_utf8})")

    temp_pos = lcd_cols - len(current_temp_string)
    print_lcd(0, 0, "Aktuell:")
    print_lcd(0, temp_pos, current_temp_string_utf8)


# print nominal temp
def print_nominal_temp():
    # load config
    min_temp = config.get_float_value("nominal_min_temp", 42.0)
    max_temp = config.get_float_value("nominal_max_temp", 55.0)

    # set lower and upper bounds for nominal temperatures
    nominal_min_temp = max(0.0, min(120.0, min_temp))
    nominal_max_temp = max(nominal_min_temp, min(120.0, max_temp))

    # format nominal temperature string
    nominal_temp = f"{nominal_min_temp:.1f} - {nominal_max_temp:.1f} °C"

    # calculate the position for displaying the temperature
    lcd_cols = config.get_int_value("LCD_COLS", 4)
    temp_pos = lcd_cols - len(nominal_temp)

    # print the formatted temperature on LCD
    print_lcd(1, 0, "Soll:")
    print_lcd(1, temp_pos, nominal_temp)


# set relay
def set_relay(pin, relay_time):
    # load config
    current_temp = config.get_float_value("current_temp", -127.0)
    relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
    relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)

    # only switch if the temperature can be read
    if 0 < current_temp <= 120:
        if pin == relay_open_pin:
            print_lcd(3, 0, "öffne Ventil     >>>")
            open_relay(relay_time)
        elif pin == relay_close_pin:
            print_lcd(3, 0, "schließe Ventil: <<<")
            close_relay(relay_time)
    else:
        print_lcd(3, 0, "Fehler: Temp Fehler!")
        time.sleep(2)


# open relays depending on temp
def open_relays(relay_time=config.get_int_value("relay_time", 2000)):
    # load config
    current_temp = config.get_float_value("current_temp", -127.0)
    nominal_min_temp = config.get_float_value("nominal_min_temp", 42.0)
    nominal_max_temp = config.get_float_value("nominal_max_temp", 55.0)
    relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
    relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)

    if current_temp < nominal_min_temp:
        # increase temp
        set_relay(relay_open_pin, relay_time)
    elif current_temp > nominal_max_temp:
        # decrease temp
        set_relay(relay_close_pin, relay_time)
    else:
        # do nothing
        print_lcd(3, 0, "Soll Temp erreicht !")


# update temp display
async def update_temp_display(rate, message, symbol):
    if rate >= 3:
        print_lcd(2, 0, f"{message}   {symbol * 3}")
    elif rate >= 0.5:
        print_lcd(2, 0, f"{message}    {symbol * 2}")
    else:
        print_lcd(2, 0, f"{message}     {symbol}")

    await asyncio.sleep(2)
    print_lcd(2, 0, f"                    ")


# update nominal temp
async def update_nominal_temp(button_pin):
    button_long = 0
    rate = 0.1

    # load config
    temp_up_pin = config.get_int_value("BUTTON_TEMP_UP_PIN", 2)
    temp_down_pin = config.get_int_value("BUTTON_TEMP_DOWN_PIN", 3)
    nominal_min_temp = config.get_float_value("nominal_min_temp", 42.0)
    nominal_max_temp = config.get_float_value("nominal_max_temp", 55.0)

    # while button is pressed
    while check_button(button_pin):
        # increase temp on temp up button
        if button_pin == temp_up_pin:
            nominal_min_temp += rate
            nominal_max_temp += rate
            await update_temp_display(rate, "TempUp Pressed", "+")

        # decrease temp on temp down button
        elif button_pin == temp_down_pin:
            nominal_min_temp -= rate
            nominal_max_temp -= rate
            await update_temp_display(rate, "TempDown Pressed", "-")

        # Update config values and print nominal temp
        config.set_value("nominal_min_temp", nominal_min_temp)
        config.set_value("nominal_max_temp", nominal_max_temp)
        print_nominal_temp()

        # Adjust rate and sleep
        await asyncio.sleep(0.5)
        button_long += 1
        if button_long == 5:
            rate = 1
        elif button_long == 10:
            rate = 1  # Adjust rate as needed

    # save config
    config.save_config()


# check buttons
async def check_buttons():
    # update nomianl temp
    await update_nominal_temp(config.get_int_value("BUTTON_TEMP_UP_PIN", 2))
    await update_nominal_temp(config.get_int_value("BUTTON_TEMP_DOWN_PIN", 3))


# format time
def format_time(secs):
    hours = secs // 3600
    mins = (secs % 3600) // 60
    secs = secs % 60
    if hours > 0:
        return f"{hours:02d}h {mins:02d}m {secs:02d}s"
    else:
        return f"{mins:02d}m {secs:02d}s"


# update timer
def update_timer(secs, message="Warte:"):
    log("INFO", f"update_timer({secs})")

    time = format_time(secs)
    cursor = 20 - len(time)

    print_lcd(3, 0, message)
    print_lcd(3, cursor, time)


# wait start
async def wait_start(secs):
    log("INFO", f"wait start ({secs})")

    # load config
    previous_millis = time.ticks_ms()
    interval = config.get_int_value("interval")
    temp_update_interval = config.get_int_value("temp_update_interval", 5)

    while secs >= 0:
        current_millis = time.ticks_ms()
        if time.ticks_diff(current_millis, previous_millis) > interval:
            # check buttons
            await check_buttons()

            # temp update on interval
            if secs % temp_update_interval == 0:
                update_temp()

            # update timer
            update_timer(secs, "Starte in:")

            # decrease secs
            secs -= 1
            previous_millis = current_millis

        await asyncio.sleep(0.1)
