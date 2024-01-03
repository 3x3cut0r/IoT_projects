# imports
from machine import I2C, Pin
from src.machine_i2c_lcd import I2cLcd  # I2C LCD

# load config
from src.config import get_value, get_int_value

# setup i2c
sda_pin = Pin(get_int_value("LCD_PIN_SDA", 20))
scl_pin = Pin(get_int_value("LCD_PIN_SCL", 21))
i2c = I2C(0, sda=sda_pin, scl=scl_pin, freq=get_int_value("LCD_FREQ", 100000))

# setup lcd
lcd_addr = int(str(get_value("LCD_ADDR", "0x27")), 16)
lcd_cols = get_int_value("LCD_COLS", 16)
lcd_rows = get_int_value("LCD_ROWS", 2)
lcd = I2cLcd(i2c, lcd_addr, lcd_rows, lcd_cols)
lcd_list = [
    "".join([" " for _ in range(get_int_value("LCD_COLS", 16))])
    for _ in range(get_int_value("LCD_ROWS", 2))
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


# convert utf-8 characters to HD44780 characters
# (https://de.wikipedia.org/wiki/HD44780#Schrift_und_Zeichensatz)
def convert_HD44780(string=""):
    string = string.replace("ß", "\342")
    string = string.replace("°", "\337")
    string = string.replace("ä", "\341")
    string = string.replace("ö", "\357")
    string = string.replace("ü", "\365")
    return string


# ljust
def ljust(string="", width=0, fillchar=" "):
    if len(str(string)) >= int(width):
        return str(string)
    return str(string + str(fillchar) * (int(width) - len(str(string))))


# fill string with spaces up to 20 chars
def fill(string="", cursor=0, padding=" "):
    fill = get_int_value("LCD_COLS", 20) - int(cursor)
    return ljust(str(string), fill, str(padding))


# get lcd list
def get_lcd_list():
    return lcd_list


# set lcd list
def set_lcd_list(line=0, message=""):
    global lcd_list
    lcd_list[int(line)] = str(message)


# get lcd line
def get_lcd_line(line=0):
    return lcd_list[int(line)]


# set lcd line
def set_lcd_line(line=0, cursor=0, message=""):
    line = int(line)
    cursor = int(cursor)
    message = str(message)
    current_line = lcd_list[line]

    # set parts
    part1 = current_line[:cursor]
    part2 = message
    part3 = current_line[(cursor + len(message)) :]

    lcd_list[line] = str(part1 + part2 + part3)[: get_int_value("LCD_COLS", 20)]


# print lcd
def print_lcd(line=0, cursor=0, message=""):
    line = int(line)
    cursor = int(cursor)
    message = str(message)

    # fill message
    message = str(fill(message, cursor))

    # set lcd line
    set_lcd_line(line, cursor, message)

    # convert utf-8 characters to HD44780 characters
    message = convert_HD44780(message)

    # print lcd
    lcd.move_to(cursor, line)  # lcd.move_to(col, row)
    lcd.putstr(message)
    lcd.hide_cursor()


# print lcd custom character
def print_lcd_char(line=0, cursor=0, char=0):
    line = int(line)
    cursor = int(cursor)
    char = int(char)

    # get char for lcd_list
    char_string = ""
    if char == 0:
        char_string = "↑"
    elif char == 1:
        char_string = "↓"
    else:
        char_string = "-"

    current_line = get_lcd_line(line)
    set_lcd_list(
        line,
        current_line[:cursor] + char_string + current_line[cursor + 1 :],
    )

    lcd.move_to(cursor, line)  # lcd.move_to(col, row)
    lcd.putchar(chr(char))
