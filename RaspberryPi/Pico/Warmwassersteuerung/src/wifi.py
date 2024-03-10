# imports
import network
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from src.log import log
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
async def connect_wifi():
    global wifi_is_activated
    if wifi_is_activated:
        global show_message
        ssid = config.get_value("wifi_ssid")
        log("INFO", f"connect_wifi(ssid = {ssid})")

        if ssid is not None:
            password = config.get_value("wifi_password", "password")

            # activate and connect wifi
            try:
                wifi.active(True)
                wifi.connect(ssid, password)
            except OSError as error:
                log("ERROR", f"wifi module error: {error}")
                log("ERROR", "disable wifi()")
                wifi_is_activated = False

            # wait until conneciton is established
            attempts = 0
            max_attempts = config.get_int_value("wifi_max_attempts", 10)
            while (
                wifi_is_activated and not wifi.isconnected() and attempts < max_attempts
            ):
                await asyncio.sleep(1)
                attempts += 1
                print_lcd(2, 0, "verbinde WLAN ... {:02d}".format(attempts))

            if wifi.isconnected():
                if show_message >= 1:
                    log("INFO", f"wifi connected: {wifi.ifconfig()}")
                    print_lcd(2, 0, "WLAN wurde verbunden")
                    await asyncio.sleep(3)
                show_message = 0
            else:
                log("WARN", "wifi connection failed!")
                print_lcd(2, 0, "WLAN nicht verbunden")
        else:
            log("ERROR", f"no SSID found!")
            print_lcd(2, 0, "keine SSID gefunden!")
            wifi_is_activated = False

        await asyncio.sleep(5)
        print_lcd(2, 0, " ")


# check wifi is active
def check_wifi_isactivated():
    return wifi_is_activated


# check wifi connection
def check_wifi_isconnected():
    try:
        return wifi.isconnected()
    except:
        return False
