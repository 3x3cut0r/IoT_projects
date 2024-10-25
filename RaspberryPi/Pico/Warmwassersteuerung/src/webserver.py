# imports
import gc  # https://docs.micropython.org/en/latest/library/gc.html
import re  # https://docs.micropython.org/en/latest/library/re.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from machine import (
    reset,
)  # https://docs.micropython.org/en/latest/library/machine.html#machine.reset
from src.log import log
from src.config import config  # Config() instance
from src.functions import print_nominal_temp, set_relay
from src.lcd import get_lcd_line, set_backlight
from src.wifi import connect_wifi, check_wifi_isconnected


# ==================================================
# functions
# ==================================================


# convert html
def convert_html(string=""):
    return string.replace(" ", "&nbsp;")


# get lcd line
def get_lcd_html_line(line):
    lcd_line = get_lcd_line(line)
    return convert_html(lcd_line)


# return " checked", if value is true
def is_checked(value):
    return " checked" if str(value).lower() in ["true", "1", "yes", "on"] else ""


# return "true", if value is true
def is_true(value):
    return "true" if str(value).lower() in ["true", "1", "yes", "on"] else "false"


# replace placeholder
def replace_placeholder(content="", line_number=0):
    # assign line numbers to placeholders and their keys
    line_to_placeholder = {
        # LCD LINE NUMBERS
        13: ("LCD_LINE_1", get_lcd_html_line(0)),
        14: ("LCD_LINE_2", get_lcd_html_line(1)),
        15: ("LCD_LINE_3", get_lcd_html_line(2)),
        16: ("LCD_LINE_4", get_lcd_html_line(3)),
        # MANUAL CONTROL
        21: (
            "highlighted",
            (
                " highlighted"
                if config.get_float_value("current_temp", -127.0)
                > config.get_float_value("nominal_max_temp", 57.0)
                else ""
            ),
        ),
        22: ("manual_relay_time", config.get_value("manual_relay_time", "")),
        23: (
            "highlighted",
            (
                " highlighted"
                if config.get_float_value("current_temp", -127.0)
                < config.get_float_value("nominal_min_temp", 42.0)
                else ""
            ),
        ),
        # CONFIGURATION
        29: ("nominal_min_temp", config.get_value("nominal_min_temp", "")),
        31: ("nominal_max_temp", config.get_value("nominal_max_temp", "")),
        33: ("delay_before_start_1", config.get_value("delay_before_start_1", "")),
        35: ("init_relay_time", config.get_value("init_relay_time", "")),
        37: ("delay_before_start_2", config.get_value("delay_before_start_2", "")),
        39: ("relay_time", config.get_value("relay_time", "")),
        41: ("update_time", config.get_value("update_time", "")),
        43: ("temp_update_interval", config.get_value("temp_update_interval", "")),
        45: (
            "lcd_i2c_backlight",
            is_checked(config.get_value("lcd_i2c_backlight", "false")),
        ),
        47: (
            "lcd_i2c_backlight",
            is_true(config.get_value("lcd_i2c_backlight", "false")),
        ),
        48: (
            "buttons_activated",
            is_checked(config.get_value("buttons_activated", "false")),
        ),
        50: (
            "buttons_activated",
            is_true(config.get_value("buttons_activated", "false")),
        ),
        52: (
            "log_level_OFF",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "OFF"
                else ""
            ),
        ),
        53: (
            "log_level_ERROR",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "ERROR"
                else ""
            ),
        ),
        54: (
            "log_level_WARN",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "WARN"
                else ""
            ),
        ),
        55: (
            "log_level_INFO",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "INFO"
                else ""
            ),
        ),
        56: (
            "log_level_VERBOSE",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "VERBOSE"
                else ""
            ),
        ),
        59: ("interval", config.get_value("interval", "")),
        61: ("temp_sampling_interval", config.get_value("temp_sampling_interval", "")),
        63: (
            "temp_change_high_threshold_temp",
            config.get_float_value("temp_change_high_threshold_temp", 1.0),
        ),
        65: (
            "temp_change_high_threshold_relay_time_multiplier",
            config.get_float_value(
                "temp_change_high_threshold_relay_time_multiplier", 1.5
            ),
        ),
        67: (
            "temp_change_high_threshold_update_time_multiplier",
            config.get_float_value(
                "temp_change_high_threshold_update_time_multiplier", 0.5
            ),
        ),
        69: ("wifi_max_attempts", config.get_value("wifi_max_attempts", "")),
        # INFO
        73: ("wifi_ssid", config.get_value("wifi_ssid", "")),
        75: ("previous_millis", config.get_value("previous_millis", "")),
        77: (
            "temp_last_measurement_time",
            config.get_value("temp_last_measurement_time", ""),
        ),
        79: ("current_temp", config.get_value("current_temp", "")),
        81: ("temp_last_measurement", config.get_value("temp_last_measurement", "")),
        83: ("temp_increasing", config.get_value("temp_increasing", "")),
        85: ("temp_change_category", config.get_value("temp_change_category", "")),
        88: ("TEMP_SENSOR_PIN", config.get_value("TEMP_SENSOR_PIN", "")),
        90: ("TEMP_SENSOR_2_PIN", config.get_value("TEMP_SENSOR_2_PIN", "")),
        92: (
            "TEMP_SENSOR_RESOLUTION_BIT",
            config.get_value("TEMP_SENSOR_RESOLUTION_BIT", ""),
        ),
        94: ("LCD_PIN_SDA", config.get_value("LCD_PIN_SDA", "")),
        96: ("LCD_PIN_SCL", config.get_value("LCD_PIN_SCL", "")),
        98: ("LCD_ADDR", config.get_value("LCD_ADDR", "")),
        100: ("LCD_FREQ", config.get_value("LCD_FREQ", "")),
        102: ("LCD_COLS", config.get_value("LCD_COLS", "")),
        104: ("LCD_ROWS", config.get_value("LCD_ROWS", "")),
        106: ("RELAY_OPEN_PIN", config.get_value("RELAY_OPEN_PIN", "")),
        108: ("RELAY_CLOSE_PIN", config.get_value("RELAY_CLOSE_PIN", "")),
        110: ("BUTTON_TEMP_UP_PIN", config.get_value("BUTTON_TEMP_UP_PIN", "")),
        112: ("BUTTON_TEMP_DOWN_PIN", config.get_value("BUTTON_TEMP_DOWN_PIN", "")),
        # HIDDEN
        115: ("manual_relay_time", config.get_value("manual_relay_time", "")),
        # RESET
        120: (
            "boot_normal",
            (
                " checked"
                if str(config.get_value("boot_normal", "false")).lower()
                in ["true", "1", "yes", "on"]
                else ""
            ),
        ),
        122: (
            "boot_normal",
            (
                "true"
                if str(config.get_value("boot_normal", "false")).lower()
                in ["true", "1", "yes", "on"]
                else "false"
            ),
        ),
    }

    # replace keys
    if line_number in line_to_placeholder:
        key, value = line_to_placeholder[line_number]
        placeholder = f"!!!--{key}--!!!"
        content = content.replace(placeholder, str(value))

    return content


# parse for data
def parse_form_data(body):
    parsed_data = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            parsed_data[key] = value
        else:
            parsed_data[pair] = None
    return parsed_data


# manage wifi connection
async def manage_wifi_connection():
    while True:
        await asyncio.sleep(30)
        if not check_wifi_isconnected():
            await connect_wifi()


# stream file
async def stream_file(writer, file_name, chunk_size=1024):
    file_name_präfix = "../web/"
    try:
        with open(file_name_präfix + file_name, "rb", encoding="utf-8") as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                await writer.awrite(chunk)
    except OSError as e:
        log("ERROR", f"while reading file: {e}")


# get index.html
async def get_index_html(writer):
    web_path = "/web/"
    file_path = web_path + "index.html"
    line_number = 0

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line_number += 1
            line = replace_placeholder(line, line_number)
            await writer.awrite(line.encode("utf-8"))


# handle relay action
async def handle_relay_action(action, manual_relay_time, error_msg, pin_key):
    if error_msg:
        response_content = (
            f'<span style="color: orange;">WARN: {action} failed: {error_msg}</span>'
        )
    elif config.get_int_value("timer") <= 10:
        response_content = f'<span style="color: orange;">WARN: {action} failed: Timer is below 10.</span>'
    else:
        response_content = f'<span style="color: green;">INFO: {action} for {manual_relay_time}ms successful.</span>'
        await set_relay(config.get_int_value(pin_key), manual_relay_time)
    return response_content


# handle post from index.html
async def handle_post(body, requested_path="/save_config"):
    # response_content
    response_content = ""

    # parse form data
    form_data = parse_form_data(body)
    log("INFO", f"POST request: data:\n{form_data}")

    error = False

    # update config
    for key in form_data:
        if config.get_value(key) is not None:
            config.set_value(key, form_data[key])
        else:
            error = "key " + key + " not found in config.json"

    # save config
    config.save_config()

    # print nominal temp
    print_nominal_temp()

    # set lcd backlight
    set_backlight(config.get_bool_value("lcd_i2c_backlight"))

    # /open_relay
    if requested_path == "/open_relay":
        current_temp = config.get_float_value("current_temp", -127.0)
        manual_relay_time = config.get_int_value("manual_relay_time", 1200)
        if manual_relay_time > 10000:
            manual_relay_time = 10000
        timer = config.get_int_value("timer")
        puffer_time = (manual_relay_time / 1000) + 3
        if error:
            response_content = f'<span style="color: orange;">WARN: Ventil wurde nicht ge&ouml;ffnet: {error}</span>'
            log(
                "WARN",
                f"open_relay({manual_relay_time}): manual trigger failed: {error}",
            )
        elif timer <= puffer_time:
            response_content = f'<span style="color: orange;">WARN: Ventil wurde nicht ge&ouml;ffnet: der Timer ist zu nahe an 0.</span>'
            log(
                "ERROR",
                f"open_relay({manual_relay_time}): manual trigger failed: Timer near by 0.",
            )
        elif not (0 < current_temp <= 120):
            response_content = f'<span style="color: red;">ERROR: Ventil wurde nicht ge&ouml;ffnet: Temp Fehler!</span>'
            log(
                "ERROR",
                f"open_relay({manual_relay_time}): manual trigger failed: temp error.",
            )
        else:
            response_content = f'<span style="color: green;">INFO: Ventil wird f&uuml;r {manual_relay_time}ms ge&ouml;ffnet.</span>'
            log("INFO", f"open_relay({manual_relay_time}): manual trigger")
            relay_open_pin = config.get_int_value("RELAY_OPEN_PIN", 14)
            await set_relay(relay_open_pin, manual_relay_time)

    # /close_relay
    if requested_path == "/close_relay":
        current_temp = config.get_float_value("current_temp", -127.0)
        manual_relay_time = config.get_int_value("manual_relay_time", 1200)
        if manual_relay_time > 10000:
            manual_relay_time = 10000
        timer = config.get_int_value("timer")
        puffer_time = (manual_relay_time / 1000) + 3
        if error:
            response_content = f'<span style="color: orange;">WARN: Ventil wurde nicht geschlossen: {error}</span>'
            log(
                "WARN",
                f"close_relay({manual_relay_time}): manual trigger failed: {error}",
            )
        elif timer <= puffer_time:
            response_content = f'<span style="color: orange;">WARN: Ventil wurde nicht geschlossen: der Timer ist zu nahe an 0.</span>'
            log(
                "ERROR",
                f"close_relay({manual_relay_time}): manual trigger failed: Timer near by 0.",
            )
        elif not (0 < current_temp <= 120):
            response_content = f'<span style="color: red;">ERROR: Ventil wurde nicht geschlossen: Temp Fehler!</span>'
            log(
                "ERROR",
                f"close_relay({manual_relay_time}): manual trigger failed: temp error.",
            )
        else:
            response_content = f'<span style="color: green;">INFO: Ventil wird f&uuml;r {manual_relay_time}ms geschlossen.</span>'
            log("INFO", f"close_relay({manual_relay_time}): manual trigger")
            relay_close_pin = config.get_int_value("RELAY_CLOSE_PIN", 15)
            await set_relay(relay_close_pin, manual_relay_time)

    # /save_config
    elif requested_path == "/save_config":
        if error:
            response_content = f'<span style="color: orange;">WARN: Konfiguration nur teilweise aktualisiert: {error}</span>'
            log("WARN", f"config.json partially updated: {error}")
        else:
            response_content = f'<span style="color: green;">INFO: Konfiguration erfolgreich aktualisiert</span>'
            log("INFO", "config.json successfully updated")

    # /reset
    elif requested_path == "/reset":
        if error:
            response_content = f'<span style="color: orange;">WARN: Boot Normal Option wurde nicht richtig &uuml;bermittelt und bleibt unber&uuml;hrt: {error}</span>'
            log("WARN", f"boot_normal NOT updated: {error}")
        else:
            response_content = f'<span style="color: green;">INFO: Reset erkannt. Starte neu ...</span>'
            log("INFO", "reset()")

    # add back button and return script
    if requested_path in ["/open_relay", "/close_relay", "/save_config", "/reset"]:
        response_content += """
            <br /><br />
            <a href="/"><button type="button">zur&uuml;ck</button></a>
            <script>
                setTimeout(function() {
                    window.location.href = '/';
                }, 4000); // 4000 Millisekunden = 4 Sekunden
            </script>
        """

    return response_content


# send_response
async def send_response(writer, content_type, content=None):
    writer.write(f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8"))
    if content:
        await writer.awrite(content.encode("utf-8"))


# handle post request
async def handle_post_request(writer, request_body, requested_path):
    response_content = await handle_post(request_body, requested_path)
    await send_response(writer, "text/html", response_content)


# handle client
async def handle_client(reader, writer):
    reset_pico = False

    # get request
    request_lines = []
    content_length = 0
    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break
        request_lines.append(line.decode("utf-8"))
        if line.lower().startswith(b"content-length:"):
            content_length = int(line.decode().split()[1])

    # get request header
    request_header = "".join(request_lines)

    # read body if present
    request_body = ""
    if content_length > 0:
        remaining_length = content_length
        while remaining_length > 0:
            chunk = await reader.read(min(remaining_length, 1024))
            if not chunk:
                break
            request_body += chunk.decode("utf-8")
            remaining_length -= len(chunk)

    # process request
    match = re.search(
        r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) /[^ ]*", request_header
    )
    if match:
        result = match.group(0)
    else:
        result = ""
    log("INFO", f"handle_client() - {result}")

    requested_path = request_header.split(" ")[1]

    # /index.html
    if requested_path in ["/", "/index.html"]:
        await send_response(writer, "text/html")
        await get_index_html(writer)

    # /open_relay, /close_relay, /save_config
    elif (
        requested_path in ["/open_relay", "/close_relay", "/save_config"]
        and "POST" in request_header.split(" ")[0]
    ):
        await handle_post_request(writer, request_body, requested_path)

    # /reset
    elif requested_path == "/reset" and "POST" in request_header.split(" ")[0]:
        await handle_post_request(writer, request_body, requested_path)
        reset_pico = True

    # /styles.css
    elif requested_path == "/styles.css":
        await send_response(writer, "text/css")
        await stream_file(writer, "styles.css", chunk_size=1024)

    # 404 Not Found
    else:
        response = "HTTP/1.1 404 Not Found\n\n"
        await writer.awrite(response.encode("utf-8"))

    # clean up and close
    await writer.drain()
    await writer.wait_closed()

    # release memory
    gc.collect()

    # reset pico
    if reset_pico:
        reset()


# run webserver
async def run_webserver():
    try:
        host = "0.0.0.0"
        port = 80
        asyncio.create_task(manage_wifi_connection())
        log("INFO", f"run_webserver({host}, {port})")
        server = await asyncio.start_server(handle_client, host, port)  # type: ignore

    except Exception as e:
        # print error message
        message = f"ERROR: webserver.py: {str(e)}\n"
        print(message)

        # write error.log
        with open("/error.log", "w", encoding="utf-8") as file:
            file.write(message)


if __name__ == "__main__":
    # create asyncio event loop
    loop = asyncio.get_event_loop()

    # run webserver() as task
    loop.create_task(run_webserver())

    # run event loop forever
    loop.run_forever()
