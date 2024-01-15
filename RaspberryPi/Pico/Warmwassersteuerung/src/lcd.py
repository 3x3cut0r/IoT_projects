# imports
from machine import (
    I2C,
    Pin,
)  # https://docs.micropython.org/en/latest/library/machine.html
from src.machine_i2c_lcd import I2cLcd  # I2C LCD
from src.config import config  # Config() instance

# setup i2c
sda_pin = Pin(config.get_int_value("LCD_PIN_SDA", 20))
scl_pin = Pin(config.get_int_value("LCD_PIN_SCL", 21))
i2c = I2C(0, sda=sda_pin, scl=scl_pin, freq=config.get_int_value("LCD_FREQ", 100000))

# setup lcd
lcd_addr = int(str(config.get_value("LCD_ADDR", "0x27")), 16)
lcd_cols = config.get_int_value("LCD_COLS", 16)
lcd_rows = config.get_int_value("LCD_ROWS", 2)
lcd = I2cLcd(i2c, lcd_addr, lcd_rows, lcd_cols)
lcd_lines = [
    "".join([" " for _ in range(config.get_int_value("LCD_COLS", 16))])
    for _ in range(config.get_int_value("LCD_ROWS", 2))
]

# create custom characters
arrow_up = [0b00100, 0b01110, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100]
arrow_down = [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111, 0b01110, 0b00100]
lcd.custom_char(0, bytearray(arrow_up))
lcd.custom_char(1, bytearray(arrow_down))


# ==================================================
# functions
# ==================================================


# init lcd
def init_lcd():
    lcd.backlight_on()
    lcd.hide_cursor()
    lcd.blink_cursor_off()
    lcd.clear()


# set backlight
def set_backlight(value=True):
    if value:
        lcd.backlight_on()
    else:
        lcd.backlight_off()


# show cursor
def show_cursor(value=True):
    if value:
        lcd.show_cursor()
    else:
        lcd.hide_cursor()


# blink cursor
def blink_cursor(value=True):
    if value:
        lcd.blink_cursor_on()
    else:
        lcd.blink_cursor_off()


# clear lcd
def clear_lcd():
    lcd.clear()


# convert utf-8 characters to HD44780A00 characters
# get dual number from the HD44780A00 table: https://de.wikipedia.org/wiki/HD44780#Schrift_und_Zeichensatz
# convert dual number to octal number: https://www.arndt-bruenner.de/mathe/scripts/Zahlensysteme.htm
def convert_HD44780A00(string=""):
    replacements = {
        "ß": "\342",  # HD44780A00 for ß
        "°": "\337",  # HD44780A00 for °
        "ä": "\341",  # HD44780A00 for ä
        "ö": "\357",  # HD44780A00 for ö
        "ü": "\365",  # HD44780A00 for ü
    }
    for original, replacement in replacements.items():
        string = string.replace(original, replacement)
    return string


# ljust
def ljust(string="", width=0, fillchar=" "):
    if len(str(string)) >= int(width):
        return str(string)
    return str(string + str(fillchar) * (int(width) - len(str(string))))


# fill string with spaces up to 20 chars
def fill(string="", cursor=0, padding=" "):
    fill = config.get_int_value("LCD_COLS", 20) - int(cursor)
    return ljust(str(string), fill, str(padding))


# get lcd line
def get_lcd_line(line=0):
    return lcd_lines[int(line)]


# get lcd lines
def get_lcd_lines():
    return lcd_lines


# set lcd lines
def set_lcd_lines(line=0, message=""):
    global lcd_lines
    lcd_lines[int(line)] = str(message)


# set lcd line
def set_lcd_line(line=0, cursor=0, message=""):
    line = int(line)
    cursor = int(cursor)
    message = str(message)
    current_line = lcd_lines[line]

    # set parts
    part1 = current_line[:cursor]
    part2 = message
    part3 = current_line[(cursor + len(message)) :]

    lcd_lines[line] = str(part1 + part2 + part3)[: config.get_int_value("LCD_COLS", 20)]


# print lcd
def print_lcd(line=0, cursor=0, message=""):
    line = int(line)
    cursor = int(cursor)
    message = str(message)

    # fill message
    message = str(fill(message, cursor))

    # set lcd line
    set_lcd_line(line, cursor, message)

    # convert utf-8 characters to HD44780A00 characters
    message = convert_HD44780A00(message)

    # print lcd
    lcd.move_to(cursor, line)  # lcd.move_to(col, row)
    lcd.putstr(message)
    lcd.hide_cursor()


# print lcd custom character
def print_lcd_char(line=0, cursor=0, char=0):
    line = int(line)
    cursor = int(cursor)
    char = int(char)

    # get char for lcd_lines
    char_string = ""
    if char == 0:
        char_string = "↑"
    elif char == 1:
        char_string = "↓"
    else:
        char_string = "-"

    current_line = get_lcd_line(line)
    set_lcd_lines(
        line,
        current_line[:cursor] + char_string + current_line[cursor + 1 :],
    )

    lcd.move_to(cursor, line)  # lcd.move_to(col, row)
    lcd.putchar(chr(char))
