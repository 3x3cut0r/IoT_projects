# ==================================================
# Heizungssteuerung
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
    get_value,
    set_value,
)
from src.lcd import init_lcd
from src.relay import init_relays, open_relay, close_relay
from src.wifi import connect_wifi, check_wifi_isconnected
from src.functions import (
    categorize_temp_change,
    adjust_update_time_based_on_temp_category,
    update_temp,
    print_nominal_temp,
    open_relay,
    check_buttons,
    update_timer,
    wait_start,
)

# ==================================================
# setup
# ==================================================

# init config
init_config()

# init lcd
init_lcd()

# connect wifi
connect_wifi()

# init relays
init_relays()

# update temp
update_temp()
set_value("tempAtLastMeasurement", get_value("current_temp"))

# print nominal temp
print_nominal_temp()

# wait start
wait_start(get_value("delay_before_start_1"))
close_relay(get_value("init_relay_time"))  # open relay initial
wait_start(get_value("delay_before_start_2"))


# ==================================================
# main
# ==================================================
def main():
    previous_millis = 0
    interval = 1000

    while True:
        current_millis = time.ticks_ms()

        # adjust temp category
        if current_millis - int(
            get_value("temp_last_measurement_time")
            >= int(get_value("temp_sampling_interval"))
        ):
            update_temp()
            temp_change = float(get_value("current_temp")) - float(
                get_value("temp_last_measurement")
            )

            # categorize temp change
            categorize_temp_change(temp_change)

            # update last measurement temp
            set_value("temp_last_measurement", float(get_value("current_temp")))

            # update last measurement temp time
            set_value("temp_last_measurement_time", current_millis)

        # main
        if current_millis - previous_millis > interval:
            # update time
            if int(get_value("update_time")) >= 0:
                update_timer(int(get_value("update_time")))
                set_value("update_time", (int(get_value("update_time")) - 1))

            # check buttons
            check_buttons()

            # update temp on temp update interval
            if (
                int(get_value("update_time")) % int(get_value("temp_update_interval"))
                == 0
            ):
                update_temp()

            if int(get_value("update_time")) == 0:
                # open relay
                open_relay(int(get_value("relay_time")))

                # set and adjust update time based on temp category
                set_value("update_time", adjust_update_time_based_on_temp_category())

                # create config backup
                create_config_backup()

                # connect wifi if wifi is not connected
                if not check_wifi_isconnected():
                    connect_wifi()

            # update previous millis
            previous_millis = current_millis


if __name__ == "__main__":
    main()
