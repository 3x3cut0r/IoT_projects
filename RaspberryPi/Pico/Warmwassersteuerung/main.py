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
from machine import (
    reset,
)  # https://docs.micropython.org/en/latest/library/machine.html#machine.reset

# custom imports
from src.log import log
from src.config import config
from src.lcd import init_lcd
from src.led import init_led
from src.relay import init_relays
from src.webserver import run_webserver
from src.functions import (
    categorize_temp_change,
    adjust_relay_time_based_on_temp_category,
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

        if config.get_bool_value("boot_normal", True):

            # wait start 1
            await wait_start(config.get_int_value("delay_before_start_1"), "Start 1/2:")

            # open relay initial
            await set_relay(
                config.get_int_value("RELAY_OPEN_PIN", 14),
                config.get_int_value("init_relay_time", 5000),
            )

            # wait start 2
            await wait_start(config.get_int_value("delay_before_start_2"), "Start 2/2:")

        # open relay
        await open_relays(config.get_int_value("relay_time", 1800))

        # set normal boot to True
        config.set_value("boot_normal", 1)

        # init time values
        previous_millis = 0
        interval = config.get_int_value("interval", 930)
        update_time = config.get_int_value("update_time", 120)
        temp_update_interval = config.get_int_value("temp_update_interval", 5)

        # ==================================================
        # main loop
        # ==================================================
        log("INFO", "--------------------------")
        log("INFO", "main loop()")
        log("INFO", "--------------------------")

        while True:
            current_millis = time.ticks_ms()

            # adjust temp category
            if time.ticks_diff(
                current_millis, config.get_int_value("temp_last_measurement_time")
            ) >= config.get_int_value("temp_sampling_interval"):

                # update temp
                await update_temp()
                temp_change = config.get_float_value(
                    "current_temp", -127.0
                ) - config.get_float_value("temp_last_measurement")

                # categorize temp change
                _ = categorize_temp_change(temp_change)

                # update last measurement temp
                config.set_value(
                    "temp_last_measurement",
                    config.get_float_value("current_temp", -127.0),
                )

                # update last measurement temp time
                config.set_value("temp_last_measurement_time", current_millis)

                # release memory
                gc.collect()

            # main
            if time.ticks_diff(current_millis, previous_millis) > interval:

                if update_time > 0:
                    # update timer
                    update_timer(update_time)

                    # update temp on temp update interval
                    if update_time % temp_update_interval == 0:
                        await update_temp()
                        await update_temp(2)

                    update_time -= 1

                    # # check buttons
                    # await check_buttons()

                    # print mem alloc
                    log("VERBOSE", "mem_alloc(): {} Bytes".format(gc.mem_alloc()))

                else:

                    # update temp
                    await update_temp()
                    await update_temp(2)

                    # set and adjust relay_time based on temp category
                    relay_time = adjust_relay_time_based_on_temp_category()

                    # set and adjust update_time based on temp category
                    update_time = adjust_update_time_based_on_temp_category()

                    # open relays
                    await open_relays(relay_time)

                    # create config backup
                    config.create_config_backup()

                    # print allocated memory
                    log("INFO", "gc.mem_alloc(): {} Bytes".format(gc.mem_alloc()))

                # update previous millis
                previous_millis = current_millis
                config.set_value("previous_millis", previous_millis)

            await asyncio.sleep(0.1)

    except Exception as e:

        # print error message
        message = f"ERROR: main.py: {str(e)}\n"
        print(message)

        # set normal boot to False
        config.set_value("boot_normal", 0)
        config.save_config()

        # write error.log
        with open("/error.log", "w", encoding="utf-8") as file:
            file.write(message)

        # reset pico
        reset()


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
