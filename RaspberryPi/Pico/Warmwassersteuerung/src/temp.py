# imports
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from machine import Pin  # https://docs.micropython.org/en/latest/library/machine.html
from onewire import OneWire  # OneWire
from ds18x20 import DS18X20  # DS180B20
from src.log import log
from src.config import config  # Config() instance


# ==================================================
# class TemperatureSensor
# ==================================================
class TemperatureSensor:
    instance_counter = 0

    def __init__(
        self,
        pin_number,
        resolution,
    ):
        TemperatureSensor.instance_counter += 1
        self.sensor_number = TemperatureSensor.instance_counter
        self.sensor_postfix = f"_{self.sensor_number}" if self.sensor_number > 1 else ""

        if pin_number is None:
            pin_number = config.get_int_value("TEMP_SENSOR_PIN", 6)
        if resolution is None:
            resolution = config.get_int_value("TEMP_SENSOR_RESOLUTION_BIT", 11)
        self.pin_number = pin_number

        # init temp sensor
        self.temp_sensor_pin = Pin(pin_number)
        self.temp_sensor = DS18X20(OneWire(self.temp_sensor_pin))
        self.resolution = resolution
        self.resolution_time = int(750 / (2 ** (12 - resolution)))
        self.set_resolution()

    # set temp sensor resolution
    # bits   resolution        time
    #    9       0,5 °C    93,75 ms
    #   10      0,25 °C   187,50 ms
    #   11     0,125 °C   375,00 ms
    #   12   0,00626 °C   750,00 ms
    def set_resolution(self):
        try:
            # set temp resolution
            resolution = max(
                9, min(self.resolution, 12)
            )  # limits the resolution to valid values

            # scan for available temp sensors
            roms = self.temp_sensor.scan()

            # set resolution
            for rom in roms:
                if resolution == 9:
                    byte_string = b"\x00\x00\x1f"
                elif resolution == 10:
                    byte_string = b"\x00\x00\x3f"
                elif resolution == 11:
                    byte_string = b"\x00\x00\x5f"
                else:
                    byte_string = b"\x00\x00\x7f"
                self.temp_sensor.write_scratch(rom, byte_string)

        except OSError as e:
            log("ERROR", f"setting temp resolution: {e}")

    # get temperature
    async def get_temp(self):
        try:
            # scan for available temp sensors
            roms = self.temp_sensor.scan()
            if not roms:
                raise ValueError("no sensors found")

            # start measurement
            self.temp_sensor.convert_temp()

            # wait for measurement
            await asyncio.sleep_ms(self.resolution_time)

            # get temps from measurements
            for rom in roms:
                temp = self.temp_sensor.read_temp(rom)
                return round(temp, 1)  # return only first temp found

        except (OSError, ValueError) as e:
            log(
                "ERROR",
                f"reading temp on sensor {self.sensor_number} (pin {self.pin_number}): {e}",
            )
            temp = -127.0
            config.set_value(f"current_temp{self.sensor_postfix}", temp)
            return temp


# instance TemperatureSensor()
temp_sensor = TemperatureSensor(
    config.get_int_value("TEMP_SENSOR_PIN", 6),
    config.get_int_value("TEMP_SENSOR_RESOLUTION_BIT", 11),
)
temp_sensor_2 = TemperatureSensor(
    config.get_int_value("TEMP_SENSOR_2_PIN", 10),
    config.get_int_value("TEMP_SENSOR_RESOLUTION_BIT", 11),
)
