# imports
import network
import time
from src.config import config  # Config() instance
from src.lcd import print_lcd

wifi = network.WLAN(network.STA_IF)
network.country(config.get_value("wifi_country", "DE"))
show_message = 1
wifi_is_activated = True

# ==================================================
# functions
# ==================================================


# connect wifi
def connect_wifi():
    global wifi_is_activated
    if wifi_is_activated:
        global show_message
        ssid = config.get_value("wifi_ssid")
        print(f"INFO: connect_wifi(ssid = {ssid})")

        if ssid is not None:
            password = config.get_value("wifi_password", "password")

            # activate and connect wifi
            try:
                wifi.active(True)
                wifi.connect(ssid, password)
            except OSError as error:
                print(f"ERROR: wifi module error: {error}\nINFO: disable wifi()")
                wifi_is_activated = False

            # wait until conneciton is established
            attempts = 0
            max_attempts = config.get_int_value("wifi_max_attempts", 10)
            while (
                wifi_is_activated and not wifi.isconnected() and attempts < max_attempts
            ):
                time.sleep(1)
                attempts += 1
                print_lcd(0, 0, "verbinde WLAN ... {:02d}".format(attempts))

            if wifi.isconnected():
                if show_message >= 1:
                    print("INFO: wifi connected:", wifi.ifconfig())
                    print_lcd(0, 0, "WLAN wurde verbunden")
                    time.sleep(3)
                show_message = 0
            else:
                print(f"WARN: wifi connection failed!")
                print_lcd(0, 0, "WLAN nicht verbunden")
        else:
            print(f"ERROR: no SSID found!")
            print_lcd(0, 0, "keine SSID gefunden!")
            wifi_is_activated = False


# check wifi is active
def check_wifi_isactivated():
    return wifi_is_activated


# check wifi connection
def check_wifi_isconnected():
    try:
        return wifi.isconnected()
    except:
        return False
