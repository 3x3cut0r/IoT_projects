# ==================================================
# Hot water control
# ==================================================
#
# Components:
#   - 4 line LCD
#   - 2 Relays
#   - 2 Buttons
#   - 1 DS18B20 I2C temperature sensor
#
#   Copyright (C) 2023, 3x3cut0r
#
#   Published under the MIT license.

# ==================================================
# imports
# ==================================================

# micro python imports
import gc  # https://docs.micropython.org/en/latest/library/gc.html
import time  # https://docs.micropython.org/en/latest/library/time.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html

# custom imports
from src.log import log
from src.config import config
from src.lcd import init_lcd
from src.led import init_led
from src.relay import init_relays
from src.webserver import run_webserver
from src.functions import (
    categorize_temp_change,
    adjust_update_time_based_on_temp_category,
    update_temp,
    print_nominal_temp,
    set_relay,
    open_relays,
    # check_buttons,
    update_timer,
    wait_start,
)


async def main():
    try:
        log("INFO", "main()")

        # ========================================
        # setup
        # ========================================
        log("INFO", "--------------------------")
        log("INFO", "main setup()")
        log("INFO", "--------------------------")

        # init led
        init_led()

        # init lcd
        init_lcd()

        # init relays
        init_relays()

        # update temp
        await update_temp()
        await update_temp(2)
        config.set_value(
            "temp_last_measurement", config.get_float_value("current_temp", -127.0)
        )

        # print nominal temp
        print_nominal_temp()

        # wait start
        await wait_start(config.get_int_value("delay_before_start_1"))
        await set_relay(
            config.get_int_value("RELAY_CLOSE_PIN", 13),
            config.get_int_value("init_relay_time", 2000),
        )  # open relay initial
        await wait_start(config.get_int_value("delay_before_start_2"))

        previous_millis = 0
        interval = config.get_int_value("interval", 1000)
        update_time = config.get_int_value("update_time", 120)

        # open relay
        await open_relays(config.get_int_value("relay_time", 2000))

        # ==================================================
        # main loop
        # ==================================================
        log("INFO", "--------------------------")
        log("INFO", "main loop()")
        log("INFO", "--------------------------")

        while True:
            current_millis = time.ticks_ms()

            # adjust temp category
            if current_millis - config.get_int_value(
                "temp_last_measurement_time"
            ) >= config.get_int_value("temp_sampling_interval"):

                # update temp
                await update_temp()
                temp_change = config.get_float_value(
                    "current_temp", -127.0
                ) - config.get_float_value("temp_last_measurement")

                # categorize temp change
                categorize_temp_change(temp_change)

                # update last measurement temp
                config.set_value(
                    "temp_last_measurement",
                    config.get_float_value("current_temp", -127.0),
                )

                # update last measurement temp time
                config.set_value("temp_last_measurement_time", current_millis)

            # main
            if current_millis - previous_millis > interval:
                # update time
                if update_time > 0:
                    update_timer(update_time)

                    # print mem alloc
                    log("VERBOSE", "mem_alloc(): {} Bytes".format(gc.mem_alloc()))

                    # update temp on temp update interval
                    if (
                        update_time % config.get_int_value("temp_update_interval", 5)
                        == 0
                    ):
                        await update_temp()
                        await update_temp(2)

                    update_time -= 1

                # # check buttons
                # await check_buttons()

                if update_time <= 0:
                    # open relay
                    await open_relays(config.get_int_value("relay_time", 2000))

                    # set and adjust update_time based on temp category
                    update_time = adjust_update_time_based_on_temp_category()

                    # create config backup
                    config.create_config_backup()

                    # allocate memory
                    gc.mem_free()
                    log("INFO", "gc.mem_free({} Bytes)".format(gc.mem_alloc()))

                # update previous millis
                previous_millis = current_millis
                config.set_value("previous_millis", previous_millis)

            await asyncio.sleep(0.1)

    except Exception as e:
        with open("/error.log", "a", encoding="utf-8") as file:
            file.write(f"ERROR: main.py: {str(e)}\n")


if __name__ == "__main__":
    log("INFO", "__main__")

    # create asyncio event loop
    loop = asyncio.get_event_loop()

    # run webserver() as task
    loop.create_task(run_webserver())

    # run main() as task
    loop.create_task(main())

    # run event loop forever
    loop.run_forever()
