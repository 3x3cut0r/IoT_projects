# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from src.log import log

# from src.button import check_button
from src.config import config  # Config() instance
from src.lcd import print_lcd, print_lcd_char, rjust
from src.relay import open_relay, close_relay
from src.temp import temp_sensor, temp_sensor_2  # TemperatureSensor() instance

# ==================================================
# functions
# ==================================================


# categorize temp change
def categorize_temp_change(temp_change=0.0):
    # load config
    high_threshold = config.get_float_value("temp_change_high_threshold_temp", 1.0)
    # medium_threshold = config.get_float_value("temp_change_medium_threshold", 0.3)

    # set category
    abs_temp_change = abs(temp_change)
    if abs_temp_change >= high_threshold:
        category = "HIGH"  # TempChangeCategory.HIGH
    # elif abs_temp_change >= medium_threshold:
    #     category = "MEDIUM"  # TempChangeCategory.MEDIUM
    else:
        category = "LOW"  # TempChangeCategory.LOW
    config.set_value("temp_change_category", category)

    # temp increasing?
    arrow_direction = 0 if temp_change > 0 else 1
    config.set_value("temp_increasing", 0 if temp_change <= 0 else 1)
    print_lcd(2, 0, f"Temperatur   {category}")
    print_lcd_char(2, 11, arrow_direction)

    return category


# adjust relay time based on temp category
def adjust_relay_time_based_on_temp_category():
    # load config
    relay_time = config.get_int_value("relay_time", 1200)
    temp_increasing = config.get_bool_value("temp_increasing", False)

    # only on temp_increasing = true
    if temp_increasing:

        temp_category = config.get_value("temp_change_category", "LOW")
        if temp_category == "HIGH":
            return int(
                relay_time
                * config.get_float_value(
                    "temp_change_high_threshold_relay_time_multiplier", 1.5
                )
            )  # shorter opening time for rapid temperature changes
        # elif temp_category == "MEDIUM":
        #     return int(
        #         relay_time
        #         * config.get_float_value(
        #             "temp_change_medium_threshold_relay_time_multiplier", 1.25
        #        )
        #     )  # moderate opening time for normal temperature changes

    return relay_time  # normal opening time for slow temperature changes


# adjust update time based on temp category
def adjust_update_time_based_on_temp_category():
    # load config
    update_time = config.get_int_value("update_time", 120)
    temp_increasing = config.get_bool_value("temp_increasing", False)

    # only on temp_increasing = true
    if temp_increasing:

        temp_category = config.get_value("temp_change_category", "LOW")
        if temp_category == "HIGH":
            return int(
                update_time
                * config.get_float_value(
                    "temp_change_high_threshold_update_time_multiplier", 0.5
                )
            )  # temp measurement takes place very often
        # elif temp_category == "MEDIUM":
        #     return int(
        #         update_time
        #         * config.get_float_value(
        #             "temp_change_medium_threshold_update_time_multiplier", 0.75
        #        )
        #     )  # moderate opening time for normal temperature changes

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
async def update_temp(sensor_number=1):
    # set sensor postfix
    sensor_postfix = f"_{sensor_number}" if sensor_number > 1 else ""

    # read temp
    current_temp = await globals()[f"temp_sensor{sensor_postfix}"].get_temp()

    # set temp
    config.set_value(f"current_temp{sensor_postfix}", current_temp)

    # set LCD columns once
    lcd_cols = config.get_int_value("LCD_COLS", 20)
    lcd_cols_half = int(lcd_cols / 2)

    # format the temperature string
    current_temp_string = rjust(f"{current_temp:.1f} °C", lcd_cols_half)
    current_temp_string_utf8 = convert_utf8(current_temp_string)

    log("INFO", f"update_temp{sensor_postfix}({current_temp_string_utf8})")

    # print temp on LCD
    # ....................
    # temp 2     temp 1
    # -127.0 °C  -127.0 °C
    temp_pos = max(lcd_cols - len(current_temp_string), 0)
    if sensor_number > 1:
        temp_pos = max(lcd_cols_half - len(current_temp_string), 0)
    print_lcd(0, temp_pos, current_temp_string_utf8, False)


# print nominal temp
def print_nominal_temp():
    # load config
    min_temp = config.get_float_value("nominal_min_temp", 42.0)
    max_temp = config.get_float_value("nominal_max_temp", 57.0)

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
async def set_relay(pin, relay_time):
    # load config
    current_temp = config.get_float_value("current_temp", -127.0)
    relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
    relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)

    # only switch if the temperature can be read
    if 0 < current_temp <= 120:
        if pin == relay_open_pin:
            print_lcd(3, 0, "öffne Ventil     >>>")
            await open_relay(relay_time)
        elif pin == relay_close_pin:
            print_lcd(3, 0, "schließe Ventil: <<<")
            await close_relay(relay_time)
    else:
        print_lcd(3, 0, "Fehler: Temp Fehler!")
        await asyncio.sleep(2)


# open relays depending on temp
async def open_relays(relay_time=config.get_int_value("relay_time", 1200)):
    # load config
    current_temp = config.get_float_value("current_temp", -127.0)
    nominal_min_temp = config.get_float_value("nominal_min_temp", 42.0)
    nominal_max_temp = config.get_float_value("nominal_max_temp", 58.0)
    relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
    relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)

    # set stop timer
    config.set_value("stop_timer", relay_time // 1000 + 1)

    if current_temp < nominal_min_temp:
        # increase temp
        await set_relay(relay_close_pin, relay_time)
    elif current_temp > nominal_max_temp:
        # decrease temp
        await set_relay(relay_open_pin, relay_time)
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


# # update nominal temp
# async def update_nominal_temp(button_pin):
#     button_long = 0
#     rate = 0.1
#
#     # load config
#     temp_up_pin = config.get_int_value("BUTTON_TEMP_UP_PIN", 1)
#     temp_down_pin = config.get_int_value("BUTTON_TEMP_DOWN_PIN", 2)
#     nominal_min_temp = config.get_float_value("nominal_min_temp", 42.0)
#     nominal_max_temp = config.get_float_value("nominal_max_temp", 58.0)
#
#     # while button is pressed
#     while check_button(button_pin):
#         # increase temp on temp up button
#         if button_pin == temp_up_pin:
#             nominal_min_temp += rate
#             nominal_max_temp += rate
#             await update_temp_display(rate, "TempUp Pressed", "+")
#
#         # decrease temp on temp down button
#         elif button_pin == temp_down_pin:
#             nominal_min_temp -= rate
#             nominal_max_temp -= rate
#             await update_temp_display(rate, "TempDown Pressed", "-")
#
#         # Update config values and print nominal temp
#         config.set_value("nominal_min_temp", nominal_min_temp)
#         config.set_value("nominal_max_temp", nominal_max_temp)
#         print_nominal_temp()
#
#         # Adjust rate and sleep
#         await asyncio.sleep(0.5)
#         button_long += 1
#         if button_long == 5:
#             rate = 1
#         elif button_long == 10:
#             rate = 1  # Adjust rate as needed
#
#     # save config
#     config.save_config()


# check buttons
# async def check_buttons():
#     # check if buttons_activated = 1
#     if config.get_bool_value("buttons_activated", False):
#         # update nomianl temp
#         await update_nominal_temp(config.get_int_value("BUTTON_TEMP_UP_PIN", 1))
#         await update_nominal_temp(config.get_int_value("BUTTON_TEMP_DOWN_PIN", 2))


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
def update_timer(secs, message="Regle in:"):
    stop_timer = config.get_int_value("stop_timer", 0)
    if stop_timer >= 0:
        log("INFO", f"stop_timer({stop_timer})")
        config.set_value("stop_timer", stop_timer - 1)
    else:
        log("INFO", f"update_timer({secs})")
        config.set_value("timer", secs)

        time = format_time(secs)
        cursor = 20 - len(time)

        print_lcd(3, 0, message)
        print_lcd(3, cursor, time)


# wait start
async def wait_start(secs, lcd_text="Starte in:"):
    log("INFO", f"wait start ({secs})")

    # load config
    previous_millis = 0
    interval = config.get_int_value("interval", 930)
    temp_update_interval = config.get_int_value("temp_update_interval", 5)

    while secs > 0:
        current_millis = time.ticks_ms()
        if time.ticks_diff(current_millis, previous_millis) > interval:
            # update timer
            update_timer(secs, lcd_text)

            # temp update on interval
            if secs % temp_update_interval == 0:
                await update_temp()
                await update_temp(2)

            # # check buttons
            # await check_buttons()

            # decrease secs
            secs -= 1
            previous_millis = current_millis

        await asyncio.sleep(0.1)
