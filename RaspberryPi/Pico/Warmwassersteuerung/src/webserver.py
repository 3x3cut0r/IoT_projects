# imports
import gc  # https://docs.micropython.org/en/latest/library/gc.html
import re  # https://docs.micropython.org/en/latest/library/re.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from machine import (
    reset,
)  # https://docs.micropython.org/en/latest/library/machine.html#machine.reset
from src.log import log
from src.config import config  # Config() instance
from src.functions import print_nominal_temp
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


# replace placeholder
def replace_placeholder(content="", line_number=0):
    # assign line numbers to placeholders and their keys
    line_to_placeholder = {
        # LCD LINE NUMBERS
        13: ("LCD_LINE_1", get_lcd_html_line(0)),
        14: ("LCD_LINE_2", get_lcd_html_line(1)),
        15: ("LCD_LINE_3", get_lcd_html_line(2)),
        16: ("LCD_LINE_4", get_lcd_html_line(3)),
        # CONFIGURATION
        21: ("nominal_min_temp", config.get_value("nominal_min_temp", "")),
        23: ("nominal_max_temp", config.get_value("nominal_max_temp", "")),
        25: ("delay_before_start_1", config.get_value("delay_before_start_1", "")),
        27: ("init_relay_time", config.get_value("init_relay_time", "")),
        29: ("delay_before_start_2", config.get_value("delay_before_start_2", "")),
        31: ("relay_time", config.get_value("relay_time", "")),
        33: ("update_time", config.get_value("update_time", "")),
        35: ("temp_update_interval", config.get_value("temp_update_interval", "")),
        37: (
            "lcd_i2c_backlight",
            (
                " checked"
                if str(config.get_value("lcd_i2c_backlight", "false")).lower()
                in ["true", "1", "yes", "on"]
                else ""
            ),
        ),
        39: (
            "lcd_i2c_backlight",
            (
                "true"
                if str(config.get_value("lcd_i2c_backlight", "false")).lower()
                in ["true", "1", "yes", "on"]
                else "false"
            ),
        ),
        40: (
            "buttons_activated",
            (
                " checked"
                if str(config.get_value("buttons_activated", "false")).lower()
                in ["true", "1", "yes", "on"]
                else ""
            ),
        ),
        42: (
            "buttons_activated",
            (
                "true"
                if str(config.get_value("buttons_activated", "false")).lower()
                in ["true", "1", "yes", "on"]
                else "false"
            ),
        ),
        44: (
            "log_level_OFF",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "OFF"
                else ""
            ),
        ),
        45: (
            "log_level_ERROR",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "ERROR"
                else ""
            ),
        ),
        46: (
            "log_level_WARN",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "WARN"
                else ""
            ),
        ),
        47: (
            "log_level_INFO",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "INFO"
                else ""
            ),
        ),
        48: (
            "log_level_VERBOSE",
            (
                " selected"
                if str(config.get_value("log_level", "OFF")).upper() == "VERBOSE"
                else ""
            ),
        ),
        51: ("interval", config.get_value("interval", "")),
        53: ("temp_sampling_interval", config.get_value("temp_sampling_interval", "")),
        55: (
            "temp_change_high_threshold_temp",
            config.get_float_value("temp_change_high_threshold_temp", 1.0),
        ),
        57: (
            "temp_change_high_threshold_relay_time_multiplier",
            config.get_float_value(
                "temp_change_high_threshold_relay_time_multiplier", 1.5
            ),
        ),
        59: (
            "temp_change_high_threshold_update_time_multiplier",
            config.get_float_value(
                "temp_change_high_threshold_update_time_multiplier", 0.5
            ),
        ),
        61: ("wifi_max_attempts", config.get_value("wifi_max_attempts", "")),
        # INFO
        65: ("wifi_ssid", config.get_value("wifi_ssid", "")),
        67: ("previous_millis", config.get_value("previous_millis", "")),
        69: (
            "temp_last_measurement_time",
            config.get_value("temp_last_measurement_time", ""),
        ),
        71: ("current_temp", config.get_value("current_temp", "")),
        73: ("temp_last_measurement", config.get_value("temp_last_measurement", "")),
        75: ("temp_increasing", config.get_value("temp_increasing", "")),
        77: ("temp_change_category", config.get_value("temp_change_category", "")),
        80: ("TEMP_SENSOR_PIN", config.get_value("TEMP_SENSOR_PIN", "")),
        82: ("TEMP_SENSOR_2_PIN", config.get_value("TEMP_SENSOR_2_PIN", "")),
        84: (
            "TEMP_SENSOR_RESOLUTION_BIT",
            config.get_value("TEMP_SENSOR_RESOLUTION_BIT", ""),
        ),
        86: ("LCD_PIN_SDA", config.get_value("LCD_PIN_SDA", "")),
        88: ("LCD_PIN_SCL", config.get_value("LCD_PIN_SCL", "")),
        90: ("LCD_ADDR", config.get_value("LCD_ADDR", "")),
        92: ("LCD_FREQ", config.get_value("LCD_FREQ", "")),
        94: ("LCD_COLS", config.get_value("LCD_COLS", "")),
        96: ("LCD_ROWS", config.get_value("LCD_ROWS", "")),
        98: ("RELAY_OPEN_PIN", config.get_value("RELAY_OPEN_PIN", "")),
        100: ("RELAY_CLOSE_PIN", config.get_value("RELAY_CLOSE_PIN", "")),
        102: ("BUTTON_TEMP_UP_PIN", config.get_value("BUTTON_TEMP_UP_PIN", "")),
        104: ("BUTTON_TEMP_DOWN_PIN", config.get_value("BUTTON_TEMP_DOWN_PIN", "")),
        111: (
            "boot_normal",
            (
                " checked"
                if str(config.get_value("boot_normal", "false")).lower()
                in ["true", "1", "yes", "on"]
                else ""
            ),
        ),
        113: (
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
        placeholder = f"<!--{key}-->"
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


# handle post from index.html
def handle_post(body, requested_path="/save_config"):
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

    # /save_config
    if requested_path == "/save_config":
        if error:
            response_content = f'<span style="color: orange;">WARN: Konfiguration nur teilweise aktualisiert: {error}</span>'
            log("WARN", f"config.json partially updated: {error}")
        else:
            response_content = f'<span style="color: green;">INFO: Konfiguration erfolgreich aktualisiert</span>'
            log("INFO", "config.json successfully updated")

        # add back button and return script
        response_content += """
            <br /><br />
            <a href="/"><button type="button">zur&uuml;ck</button></a>
            <script>
                setTimeout(function() {
                    window.location.href = '/';
                }, 3000); // 3000 Millisekunden = 3 Sekunden
            </script>
        """

    # /reset
    elif requested_path == "/reset":
        if error:
            response_content = f'<span style="color: orange;">WARN: Boot Normal Option wurde nicht richtig &uuml;bermittelt und bleibt unber&uuml;hrt: {error}</span>'
            log("WARN", f"boot_normal NOT updated: {error}")
        else:
            response_content = f'<span style="color: green;">INFO: Reset erkannt. Starte neu ...</span>'
            log("INFO", "reset()")

        # add back button and return script
        response_content += """
            <br /><br />
            <a href="/"><button type="button">zur&uuml;ck</button></a>
            <script>
                setTimeout(function() {
                    window.location.href = '/';
                }, 30000); // 30000 Millisekunden = 30 Sekunden
            </script>
        """

    return response_content


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

    content_type = "text/html"
    requested_path = request_header.split(" ")[1]

    # /index.html
    if requested_path == "/" or requested_path == "/index.html":
        writer.write(
            f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8")
        )
        await get_index_html(writer)

    # /save_config
    elif requested_path == "/save_config" and "POST" in request_header.split(" ")[0]:
        writer.write(
            f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8")
        )
        response_content = handle_post(request_body, requested_path)
        await writer.awrite(response_content.encode("utf-8"))

    # /reset
    elif requested_path == "/reset" and "POST" in request_header.split(" ")[0]:
        writer.write(
            f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8")
        )
        response_content = handle_post(request_body, requested_path)
        await writer.awrite(response_content.encode("utf-8"))
        reset_pico = True

    # /styles.css
    elif requested_path == "/styles.css":
        content_type = "text/css"
        writer.write(
            f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8")
        )
        await stream_file(writer, "styles.css", chunk_size=1024)
        content_type = "text/css"

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
