# imports
import network
import time
from src.config import get_value
from src.lcd import print_lcd

wifi = network.WLAN(network.STA_IF)
show_message = 1

# ==================================================
# functions
# ==================================================


# connect wifi
def connect_wifi():
    global show_message
    ssid = get_value("wifi_ssid")
    password = get_value("wifi_password")

    wifi.active(True)
    wifi.connect(ssid, password)

    # wait until conneciton is established
    attempts = 0
    max_attempts = int(get_value("max_attempts"))
    while not wifi.isconnected() and attempts < max_attempts:
        time.sleep(1)
        attempts += 1
        # print("Verbinde mit WLAN...")
        print_lcd(3, 0, "WLAN wird verbunden ")

    if wifi.isconnected():
        if show_message >= 1:
            # print("WLAN verbunden:", wifi.ifconfig())
            print_lcd(3, 0, "WLAN wurde verbunden")
            time.sleep(3)
        show_message = 0
    else:
        # print("WLAN-Verbindung fehlgeschlagen!")
        print_lcd(3, 0, "WLAN nicht verbunden")
        time.sleep(3)


# check wifi connection
def check_wifi_isconnected():
    return wifi.isconnected()
