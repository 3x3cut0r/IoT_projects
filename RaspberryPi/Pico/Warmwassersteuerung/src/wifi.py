# imports
import network
import time
from src.config import get_value, get_int_value
from src.lcd import print_lcd

wifi = network.WLAN(network.STA_IF)
network.country(get_value("wifi_country", "DE"))
show_message = 1

# ==================================================
# functions
# ==================================================


# connect wifi
def connect_wifi():
    global show_message
    ssid = get_value("wifi_ssid")
    if ssid is not None:
        password = get_value("wifi_password", "password")

        # connect wifi
        wifi.active(True)
        try:
            wifi.connect(ssid, password)
        except OSError as error:
            print(f"wifi module error: {error}")

        # wait until conneciton is established
        attempts = 0
        max_attempts = get_int_value("wifi_max_attempts", 10)
        while not wifi.isconnected() and attempts < max_attempts:
            time.sleep(1)
            attempts += 1
            # print("Verbinde mit WLAN...")
            print_lcd(0, 0, "verbinde WLAN ... {:02d}".format(attempts))

        if wifi.isconnected():
            if show_message >= 1:
                # print("WLAN verbunden:", wifi.ifconfig())
                print_lcd(0, 0, "WLAN wurde verbunden")
                time.sleep(3)
            show_message = 0
        else:
            # print("WLAN-Verbindung fehlgeschlagen!")
            print_lcd(0, 0, "WLAN nicht verbunden")
            time.sleep(3)
    else:
        # print("keine SSID gefunden")
        print_lcd(0, 0, "keine SSID gefunden!")
        time.sleep(3)


# check wifi connection
def check_wifi_isconnected():
    try:
        return wifi.isconnected()
    except:
        return False
