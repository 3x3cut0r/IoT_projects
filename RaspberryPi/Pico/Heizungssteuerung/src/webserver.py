# imports
import socket
from src.config import get_value
from src.lcd import get_lcd_list

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))  # listen on all interfaces
s.listen(5)  # accept up to 5 connections

# setup file_name
file_name_präfix = "../web/"
file_name = "index.html"
file_path = file_name_präfix + file_name

# ==================================================
# functions
# ==================================================


# load index.html
def load_index_html():
    try:
        with open(file_path, "r") as file:
            return file.read()
    except OSError:
        return "<h1>Fehler beim Laden der Datei: " + file_name + "</h1>"


# get lcd lines
def get_lcd_lines():
    lcd_lines = get_lcd_list()
    return "".join(["<div class='lcd-line'>" + line + "</div>" for line in lcd_lines])


# run webserver
def run_webserver():
    # open connection
    conn, addr = s.accept()
    request = conn.recv(1024)
    request_str = str(request)

    # process form data
    # if "POST /submit" in request_str:
    # ...

    # send index.html
    index_html_content = load_index_html()
    index_html_content = index_html_content.replace(
        "<!--LCD_LINES_PLACEHOLDER-->", get_lcd_lines()
    )

    response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + index_html_content
    conn.send(response)

    # close connection
    conn.close()
