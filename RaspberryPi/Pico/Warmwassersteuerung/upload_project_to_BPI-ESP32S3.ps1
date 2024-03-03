# .\upload_project_to_BPI-ESP32S3.ps1 -port COM1 -config

param(
    [string]$port,
    [switch]$config
)

# Überprüft, ob ein COM-Port als Parameter übergeben wurde
if (-not $port) {
    Write-Host "Bitte geben Sie einen COM-Port mit '-port COM1' an."
    exit
}

Write-Host "Entferne Projektdateien..."
python -m mpremote connect $port rm :boot.py
python -m mpremote connect $port rm :main.py
if ($config) {
    python -m mpremote connect $port rm :config.py
}
python -m mpremote connect $port rm :src/button.py
python -m mpremote connect $port rm :src/config.py
python -m mpremote connect $port rm :src/functions.py
python -m mpremote connect $port rm :src/lcd_api.py
python -m mpremote connect $port rm :src/lcd.py
python -m mpremote connect $port rm :src/led.py
python -m mpremote connect $port rm :src/log.py
python -m mpremote connect $port rm :src/machine_i2c_lcd.py
python -m mpremote connect $port rm :src/relay.py
python -m mpremote connect $port rm :src/temp.py
python -m mpremote connect $port rm :src/webserver.py
python -m mpremote connect $port rm :src/wifi.py
python -m mpremote connect $port rm :web/index.html
python -m mpremote connect $port rm :web/styles.css

Write-Host "Kopiere Projektdateien..."
python -m mpremote connect $port cp ./main.py :main.py
if ($config) {
    python -m mpremote connect $port cp ./config.py :config.py
}
python -m mpremote connect $port cp ./src/button.py :src/button.py
python -m mpremote connect $port cp ./src/config.py :src/config.py
python -m mpremote connect $port cp ./src/functions.py :src/functions.py
python -m mpremote connect $port cp ./src/lcd_api.py :src/lcd_api.py
python -m mpremote connect $port cp ./src/lcd.py :src/lcd.py
python -m mpremote connect $port cp ./src/led.py :src/led.py
python -m mpremote connect $port cp ./src/log.py :src/log.py
python -m mpremote connect $port cp ./src/machine_i2c_lcd.py :src/machine_i2c_lcd.py
python -m mpremote connect $port cp ./src/relay.py :src/relay.py
python -m mpremote connect $port cp ./src/temp.py :src/temp.py
python -m mpremote connect $port cp ./src/webserver.py :src/webserver.py
python -m mpremote connect $port cp ./src/wifi.py :src/wifi.py
python -m mpremote connect $port cp ./web/index.html :web/index.html
python -m mpremote connect $port cp ./web/styles.css :web/styles.css

Write-Host "Liste Projektdateien..."
python -m mpremote connect $port ls
