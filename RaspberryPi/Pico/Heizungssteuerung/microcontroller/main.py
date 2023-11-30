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
    load_config,
    create_config_backup,
    get_value,
    set_value,
)
from src.lcd import init_lcd
from src.relay import init_relays, open_relay, close_relay
from src.wifi import connect_wifi, check_wifi_isconnected
from src.functions import (
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
    while True:
        # load config
        config = load_config()

        previous_millis = 0
        current_millis = time.ticks_ms()
        interval = 1000

        if current_millis - previous_millis > interval:
            # update time
            if int(config["update_time"]) >= 0:
                update_timer(int(config["update_time"]))
                config["update_time"] -= 1

            # check buttons
            check_buttons()

            # update temp on temp update interval
            if int(config["update_time"]) % int(config["temp_update_interval"]) == 0:
                update_temp()

            if int(config["update_time"]) == 0:
                # open relay
                open_relay(int(config["relay_time"]))

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
