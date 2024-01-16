# imports
import re  # https://docs.micropython.org/en/latest/library/re.html
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html
from src.config import config  # Config() instance
from src.functions import print_nominal_temp
from src.lcd import get_lcd_line, set_backlight

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
        11: ("LCD_LINE_1", get_lcd_html_line(0)),
        12: ("LCD_LINE_2", get_lcd_html_line(1)),
        13: ("LCD_LINE_3", get_lcd_html_line(2)),
        14: ("LCD_LINE_4", get_lcd_html_line(3)),
        # CONFIGURATION
        20: ("nominal_min_temp", config.get_value("nominal_min_temp", "")),
        22: ("nominal_max_temp", config.get_value("nominal_max_temp", "")),
        24: ("delay_before_start_1", config.get_value("delay_before_start_1", "")),
        26: ("delay_before_start_2", config.get_value("delay_before_start_2", "")),
        28: ("init_relay_time", config.get_value("init_relay_time", "")),
        30: ("update_time", config.get_value("update_time", "")),
        32: ("relay_time", config.get_value("relay_time", "")),
        34: ("temp_update_interval", config.get_value("temp_update_interval", "")),
        36: ("lcd_i2c_backlight", config.get_value("lcd_i2c_backlight", "")),
        38: (
            "temp_change_high_threshold",
            config.get_value("temp_change_high_threshold", ""),
        ),
        40: (
            "temp_change_medium_threshold",
            config.get_value("temp_change_medium_threshold", ""),
        ),
        42: ("wifi_max_attempts", config.get_value("wifi_max_attempts", "")),
        # INFO
        46: ("wifi_ssid", config.get_value("wifi_ssid", "")),
        48: ("previous_millis", config.get_value("previous_millis", "")),
        50: ("interval", config.get_value("interval", "")),
        52: ("current_temp", config.get_value("current_temp", "")),
        54: ("temp_last_measurement", config.get_value("temp_last_measurement", "")),
        56: (
            "temp_last_measurement_time",
            config.get_value("temp_last_measurement_time", ""),
        ),
        58: ("temp_sampling_interval", config.get_value("temp_sampling_interval", "")),
        60: ("temp_change_category", config.get_value("temp_change_category", "")),
        63: ("TEMP_SENSOR_PIN", config.get_value("TEMP_SENSOR_PIN", "")),
        65: (
            "TEMP_SENSOR_RESOLUTION_BIT",
            config.get_value("TEMP_SENSOR_RESOLUTION_BIT", ""),
        ),
        67: ("LCD_PIN_SDA", config.get_value("LCD_PIN_SDA", "")),
        69: ("LCD_PIN_SCL", config.get_value("LCD_PIN_SCL", "")),
        71: ("LCD_ADDR", config.get_value("LCD_ADDR", "")),
        73: ("LCD_FREQ", config.get_value("LCD_FREQ", "")),
        75: ("LCD_COLS", config.get_value("LCD_COLS", "")),
        77: ("LCD_ROWS", config.get_value("LCD_ROWS", "")),
        79: ("RELAY_OPEN_PIN", config.get_value("RELAY_OPEN_PIN", "")),
        81: ("RELAY_CLOSE_PIN", config.get_value("RELAY_CLOSE_PIN", "")),
        83: ("BUTTON_TEMP_UP_PIN", config.get_value("BUTTON_TEMP_UP_PIN", "")),
        85: ("BUTTON_TEMP_DOWN_PIN", config.get_value("BUTTON_TEMP_DOWN_PIN", "")),
    }

    # replace keys
    if line_number in line_to_placeholder:
        key, value = line_to_placeholder[line_number]
        placeholder = f"<!--{key}-->"
        content = content.replace(placeholder, str(value))

    return content


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
        print("ERROR: while reading file: ", e)


# get index.html
async def get_index_html(writer):
    file_name_präfix = "../web/"
    file_path = file_name_präfix + "index.html"
    line_number = 0

    with open(file_path, "r") as file:
        for line in file:
            line_number += 1
            line = replace_placeholder(line, line_number)
            await writer.awrite(line.encode("utf-8"))


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


# handle post from index.html
def handle_post(body):
    # parse form data
    form_data = parse_form_data(body)
    print(f"INFO: POST request: data:\n{form_data}")

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

    if error:
        response_content = f'<span style="color: orange;">WARN: Konfiguration nur teilweise aktualisiert: {error}</span>'
        print(f"WARN: config.json partially updated: {error}")
    else:
        response_content = f'<span style="color: green;">INFO: Konfiguration erfolgreich aktualisiert</span>'
        print(f"INFO: config.json successfully updated")

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

    return response_content


# handle client
async def handle_client(reader, writer):
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
    print(f"handle_client() - {result}")

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
        response_content = handle_post(request_body)
        await writer.awrite(response_content.encode("utf-8"))

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


# run webserver
async def run_webserver():
    host = "0.0.0.0"
    port = 80
    print(f"INFO: run_webserver({host}, {port})")
    server = await asyncio.start_server(handle_client, host, port)  # type: ignore
