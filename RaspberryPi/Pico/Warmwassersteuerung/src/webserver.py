# imports
import uasyncio as asyncio  # https://docs.micropython.org/en/v1.14/library/uasyncio.html

# from src.config import get_value
from src.lcd import get_lcd_list

# setup file_name
file_name_präfix = "../web/"

# ==================================================
# functions
# ==================================================


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
    return "".join(["<div class='lcd-line'>" + line + "</div>" for line in lcd_lines])


# handle client
async def handle_client(reader, writer):
    print(f"handle_client()")
    request = await reader.read(1024)
    # print("Received:", request)

    request_str = str(request, "utf-8")
    response_content = ""
    content_type = "text/html"
    requested_path = request_str.split(" ")[1]

    # index.html
    if requested_path == "/" or requested_path == "index.html":
        response_content = load_file("index.html")
        response_content = response_content.replace(
            "<!--LCD_LINES_PLACEHOLDER-->", get_lcd_lines()
        )

    # styles.css
    elif requested_path == "/styles.css":
        response_content = load_file("styles.css")
        content_type = "text/css"

    # Response
    response = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n" + response_content
    writer.write(response.encode("utf-8"))
    await writer.drain()
    await writer.wait_closed()


# run webserver
async def run_webserver():
    print(f"INFO: run_webserver()")
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
