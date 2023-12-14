# imports
from machine import Pin
from onewire import OneWire  # OneWire
from ds18x20 import DS18X20  # DS180B20

# load config
from src.config import get_int_value, set_value

# setup temperature sensor
temp_sensor_pin = Pin(get_int_value("TEMP_SENSOR_PIN", 16))
temp_sensor = DS18X20(OneWire(temp_sensor_pin))

# ==================================================
# functions
# ==================================================


# set temp sensor pin
def set_temp_sensor_pin(pin):
    global temp_sensor_pin
    try:
        set_value("TEMP_SENSOR_PIN", int(pin))
        temp_sensor_pin = Pin(int(pin))
    except OSError as e:
        print("error set temp sensor pin: ", e)


# set temp sensor resolution
# bits   resolution        time
#    9       0,5 °C    93,75 ms
#   10      0,25 °C   187,50 ms
#   11     0,125 °C   375,00 ms
#   12   0,00626 °C   750,00 ms
def set_temp_resolution(bits=9):
    # set temp resolution
    if int(bits) >= 9 and int(bits) <= 12:
        resolution = int(bits)
    else:
        resolution = 9

    set_value("TEMP_SENSOR_RESOLUTION_BIT", resolution)


# get temperature
def get_temp():
    try:
        # get temps
        roms = temp_sensor.scan()
        temp_sensor.convert_temp()
        for rom in roms:
            temp = float(temp_sensor.read_temp(rom))
            set_value("current_temp", round(temp, 1))

            # return only first temp found
            return temp
    except:
        temp = float(-127.0)
        set_value("current_temp", temp)
        return temp
