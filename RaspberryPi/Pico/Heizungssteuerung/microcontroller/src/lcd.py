# imports
from machine import I2C, Pin
from lcd_api import LcdApi  # LCD API
from i2c_lcd import I2cLcd  # I2C LCD

# load config
from src.config import get_value

# setup i2c
sda_pin = Pin(int(get_value("LCD_PIN_SDA")))
scl_pin = Pin(int(get_value("LCD_PIN_SCL")))
i2c = I2C(0, sda=sda_pin, scl=scl_pin, freq=int(get_value("LCD_FREQ")))

# setup lcd
lcd_addr = int(get_value("LCD_ADDR"), 16)
lcd_cols = int(get_value("LCD_COLS"))
lcd_rows = int(get_value("LCD_ROWS"))
lcd = I2cLcd(i2c, lcd_addr, lcd_rows, lcd_cols)

# create custom characters
arrow_up = {0b00100, 0b01110, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100}
arrow_down = {0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111, 0b01110, 0b00100}
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


# fill string with spaces up to 20 chars
def fill(string, cursor=0, padding=" "):
    fill = int(get_value("LCD_COLS")) - cursor
    return string.ljust(fill, padding)


# print lcd
def print_lcd(line=0, cursor=0, message=""):
    lcd.move_to(int(cursor), int(line))  # lcd.move_to(col, row)
    lcd.putstr(str(fill(message, cursor)))


# print lcd custom character
def print_lcd_char(line=0, cursor=0, char=0):
    lcd.move_to(int(cursor), int(line))  # lcd.move_to(col, row)
    lcd.putchar(chr(int(char)))
