# ==================================================
# Warmwassersteuerung
# ==================================================
#
# Komponenten:
#   - 4 Zeilen LCD
#   - 2 Ventile
#   - 2 Buttons
#   - 1 DS18B20 I2C Temperatursensor
#
#   Copyright (C) 2023, 3x3cut0r
#
#   Veröffentlicht unter der MIT Lizenz.

# ==================================================
# imports
# ==================================================

# micro python imports
import time  # https://docs.micropython.org/en/latest/library/time.html

# custom imports
from src.config import (
    init_config,
    create_config_backup,
    get_int_value,
    get_float_value,
    set_value,
)

# init config
init_config()

from src.lcd import init_lcd
from src.led import init_led
from src.relay import init_relays
from src.wifi import connect_wifi, check_wifi_isconnected
from src.webserver import run_webserver
from src.functions import (
    categorize_temp_change,
    adjust_update_time_based_on_temp_category,
    update_temp,
    print_nominal_temp,
    set_relay,
    open_relays,
    check_buttons,
    update_timer,
    wait_start,
)

# ==================================================
# setup
# ==================================================

# init led
init_led()

# init lcd
init_lcd()

# connect wifi
connect_wifi()

# run webserver
run_webserver()

# init relays
init_relays()

# update temp
update_temp()
set_value("tempAtLastMeasurement", get_float_value("current_temp", -127.0))

# print nominal temp
print_nominal_temp()

# wait start
wait_start(get_int_value("delay_before_start_1"))
set_relay(
    get_int_value("RELAY_CLOSE_PIN", 15), get_int_value("init_relay_time", 2000)
)  # open relay initial
wait_start(get_int_value("delay_before_start_2"))


# ==================================================
# main
# ==================================================
def main():
    previous_millis = 0
    interval = get_int_value("interval")
    update_time = get_int_value("update_time")

    while True:
        current_millis = time.ticks_ms()

        # adjust temp category
        if current_millis - int(
            get_int_value("temp_last_measurement_time")
            >= get_int_value("temp_sampling_interval")
        ):
            update_temp()
            temp_change = get_float_value("current_temp", -127.0) - get_float_value(
                "temp_last_measurement"
            )

            # categorize temp change
            categorize_temp_change(temp_change)

            # update last measurement temp
            set_value("temp_last_measurement", get_float_value("current_temp", -127.0))

            # update last measurement temp time
            set_value("temp_last_measurement_time", current_millis)

        # main
        if current_millis - previous_millis > interval:
            # update time
            if update_time >= 0:
                update_timer(update_time)
                update_time -= 1

            # check buttons
            check_buttons()

            # update temp on temp update interval
            if update_time % get_int_value("temp_update_interval") == 0:
                update_temp()

            if update_time == 0:
                # open relay
                open_relays()

                # set and adjust update_time based on temp category
                update_time = adjust_update_time_based_on_temp_category()

                # create config backup
                create_config_backup()

                # connect wifi if wifi is not connected
                if not check_wifi_isconnected():
                    connect_wifi()

            # update previous millis
            previous_millis = current_millis


if __name__ == "__main__":
    main()
