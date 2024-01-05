# imports
import gc  # https://docs.micropython.org/en/latest/library/gc.html
import re  # https://docs.micropython.org/en/latest/library/re.html
from io import StringIO
import uasyncio as asyncio  # https://docs.micropython.org/en/latest/library/asyncio.html

# load config
from src.config import load_config, save_config
from src.lcd import get_lcd_list

# setup file_name
file_name_präfix = "../web/"

# ==================================================
# functions
# ==================================================


# convert html
def convert_html(string=""):
    return string.replace(" ", "&nbsp;")


# load file
def load_file(file_name, mode="r"):
    try:
        with open(file_name_präfix + file_name, mode) as file:
            return file.read()
    except OSError:
        return "<h1>Fehler beim Laden der Datei: " + file_name + "</h1>"


# get lcd lines
def get_lcd_lines():
    lcd_lines = get_lcd_list()
    buffer = StringIO()
    for line in lcd_lines:
        buffer.write("<div class='lcd-line'>" + convert_html(line) + "</div>")
    return buffer.getvalue()


# get index.html
def get_index_html():
    content = load_file("index.html")
    content = content.replace("<!--LCD_LINES-->", get_lcd_lines())
    content = replace_placeholder(content)
    return content


# parse for data
def parse_form_data(body):
    print(body)
    parsed_data = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, value = pair.split("=")
            parsed_data[key] = value
    return parsed_data


# handle index.html
def handle_post(request_str):
    # find start of body
    content_start = request_str.find("\r\n\r\n") + 4
    body = request_str[content_start:]

    # parse form data
    form_data = parse_form_data(body)

    # load current config
    config = load_config()

    # update config
    for key in form_data:
        if key in config:
            config[key] = form_data[key]
        else:
            print("WARN: key " + key + " not found in config.json")

    # save config
    save_config(new_config=config)

    response_content = f"INFO: config.json successfully updated"
    print(response_content)
    return response_content


# replace placeholder
def replace_placeholder(content=""):
    config = load_config()

    placeholders = {
        "wifi_ssid": str,
        "wifi_country": str,
        "wifi_max_attempts": int,
        "delay_before_start_1": int,
        "delay_before_start_2": int,
        "init_relay_time": int,
        "update_time": int,
        "relay_time": int,
        "nominal_min_temp": float,
        "nominal_max_temp": float,
        "temp_update_interval": int,
        "lcd_i2c_backlight": int,
        "sensor_resolution_bit": int,
        "previous_millis": int,
        "interval": int,
        "current_temp": float,
        "temp_last_measurement": float,
        "temp_last_measurement_time": int,
        "temp_sampling_interval": int,
        "temp_change_category": str,
        "temp_change_high_threshold": float,
        "temp_change_medium_threshold": float,
        "TEMP_SENSOR_PIN": int,
        "TEMP_SENSOR_RESOLUTION_BIT": int,
        "LCD_PIN_SDA": int,
        "LCD_PIN_SCL": int,
        "LCD_ADDR": str,
        "LCD_FREQ": int,
        "LCD_COLS": int,
        "LCD_ROWS": int,
        "RELAY_OPEN_PIN": int,
        "RELAY_CLOSE_PIN": int,
        "BUTTON_TEMP_UP_PIN": int,
        "BUTTON_TEMP_DOWN_PIN": int,
        "LED": int,
    }

    for key, value_type in placeholders.items():
        placeholder = f"<!--{key}-->"
        value = config.get(key, "")
        content = content.replace(placeholder, str(value))

    return content


# handle client
async def handle_client(reader, writer):
    # get request
    request = await reader.read(1024)

    # prepare print message
    match = re.search(b"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) /[^ ]*", request)
    if match:
        result = match.group(0)
    else:
        result = b""
    print(f"handle_client() - {result}")

    # format request
    request_str = str(request, "utf-8")
    response_content = ""
    content_type = "text/html"
    requested_path = request_str.split(" ")[1]

    # index.html
    if requested_path == "/" or requested_path == "/index.html":
        response_content = get_index_html()

    # save_config
    elif requested_path == "/save_config" and "POST" in request_str.split(" ")[0]:
        response_content = handle_post(request_str)

    # styles.css
    elif requested_path == "/styles.css":
        response_content = load_file("styles.css")
        content_type = "text/css"

    # send response
    response = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n" + response_content
    writer.write(response.encode("utf-8"))
    gc.collect()
    await writer.drain()
    await writer.wait_closed()


# run webserver
async def run_webserver():
    host = "0.0.0.0"
    port = 80
    print(f"INFO: run_webserver({host}, {port})")
    server = await asyncio.start_server(handle_client, host, port)  # type: ignore
