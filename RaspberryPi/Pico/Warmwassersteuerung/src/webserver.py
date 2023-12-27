# imports
import socket
import time
from src.config import get_value
from src.lcd import get_lcd_list
from src.wifi import connect_wifi, check_wifi_isconnected

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


# run webserver (should be startet in a new thread)
def run_webserver():
    print("run_webserver()")

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 80))  # listen on all interfaces
    s.listen(5)  # accept up to 5 connections

    # run webserver
    while True:
        # connect wifi, if not connected
        if not check_wifi_isconnected():
            print("connect_wifi()")
            connect_wifi()

        else:
            print("warte auf Verbindung...")

            # open connection
            conn, addr = s.accept()
            request = conn.recv(1024)
            request_str = str(request)
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

            # 404
            else:
                conn.send("HTTP/1.1 404 Not Found\n\n")
                conn.close()
                continue

            # process form data
            # if "POST /submit" in request_str:
            # ...

            # set response
            response = (
                f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n" + response_content
            )

            # send response
            conn.sendall(response)

            # close connection
            conn.close()

        # sleep 1
        time.sleep(1)
