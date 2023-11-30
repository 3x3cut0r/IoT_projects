# imports
import network
import time
from src.config import get_value

wifi = network.WLAN(network.STA_IF)

# ==================================================
# functions
# ==================================================


# connect wifi
def connect_wifi():
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
        print("Verbinde mit WLAN...")

    if wifi.isconnected():
        print("WLAN verbunden:", wifi.ifconfig())
    else:
        print("WLAN-Verbindung fehlgeschlagen!")


# check wifi connection
def check_wifi_isconnected():
    return wifi.isconnected()
