# imports
from machine import Pin
from onewire import OneWire  # OneWire
from ds18x20 import DS18X20  # DS180B20

# load config
from src.config import load_config, save_config

# setup temperature sensor
ds_pin = Pin(int(config["TEMP_SENSOR_PIN"]))
ds_sensor = DS18X20(OneWire(ds_pin))

# ==================================================
# functions
# ==================================================


# set temp sensor resolution
# bits   resolution        time
#    9       0,5 °C    93,75 ms
#   10      0,25 °C   187,50 ms
#   11     0,125 °C   375,00 ms
#   12   0,00626 °C   750,00 ms
def set_temp_resolution(bits=9):
    # load config
    config = load_config()

    # set temp resolution
    if int(bits) >= 9 and int(bits) <= 12:
        resolution = int(bits)
    else:
        resolution = 9

    config["TEMP_SENSOR_RESOLUTION_BIT"] = resolution
    save_config(config)


# read temperature
def read_temp():
    # load config
    config = load_config()

    # read temps
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    for rom in roms:
        temp = float(
            ds_sensor.read_temp(rom, int(config["TEMP_SENSOR_RESOLUTION_BIT"]))
        )
        config["current_temp"] = temp
        save_config(config)

        # return only first temp found
        return temp
