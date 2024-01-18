# imports
import time  # https://docs.micropython.org/en/latest/library/time.html
from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from onewire import OneWire  # OneWire
from ds18x20 import DS18X20  # DS180B20
from src.log import log
from src.config import config  # Config() instance


# ==================================================
# class TemperatureSensor
# ==================================================
class TemperatureSensor:
    def __init__(self):
        # set temp sensor pin
        self.temp_sensor_pin = Pin(config.get_int_value("TEMP_SENSOR_PIN", 16))
        self.temp_sensor = DS18X20(OneWire(self.temp_sensor_pin))
        # self.set_resolution(config.get_int_value("TEMP_SENSOR_RESOLUTION_BIT", 9))

    # set temp sensor resolution
    # bits   resolution        time
    #    9       0,5 °C    93,75 ms
    #   10      0,25 °C   187,50 ms
    #   11     0,125 °C   375,00 ms
    #   12   0,00626 °C   750,00 ms
    def set_resolution(self, resolution):
        try:
            # set temp resolution
            resolution = max(
                9, min(resolution, 12)
            )  # Beschränken Sie die Auflösung auf gültige Werte
            roms = self.temp_sensor.scan()
            for rom in roms:
                self.temp_sensor.write_scratch(rom, resolution=resolution)  # type: ignore
        except OSError as e:
            log("ERROR", f"setting temp resolution: {e}")

    # get temperature
    def get_temp(self):
        try:
            roms = self.temp_sensor.scan()
            if not roms:
                raise ValueError("no sensors found")
            time.sleep_ms(750)

            self.temp_sensor.convert_temp()
            # get temps
            for rom in roms:
                temp = self.temp_sensor.read_temp(rom)
                config.set_value("current_temp", round(temp, 1))
                return round(temp, 1)  # return only first temp found
        except (OSError, ValueError) as e:
            log("ERROR", f"reading temp: {e}")
            temp = -127.0
            config.set_value("current_temp", temp)
            return temp


# instance TemperatureSensor()
temp_sensor = TemperatureSensor()
