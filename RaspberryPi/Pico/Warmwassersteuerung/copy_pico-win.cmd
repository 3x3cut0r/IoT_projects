@echo off
REM copy_pico-win.cmd COM10

if "%1"=="" (
    set PORT=COM10
) else (
    set PORT=%1
)

ampy --port %PORT% ls 2>NUL
echo deleting files...
ampy --port %PORT% rm boot.py 2>NUL
ampy --port %PORT% rm main.py 2>NUL
ampy --port %PORT% rm config.json 2>NUL
ampy --port %PORT% rm config_backup.json 2>NUL
ampy --port %PORT% rm error.log 2>NUL
ampy --port %PORT% rmdir src 2>NUL
ampy --port %PORT% rmdir web 2>NUL
ampy --port %PORT% rmdir .old 2>NUL
echo deleting files... DONE 2>NUL
ampy --port %PORT% ls 2>NUL
echo copying files...
ampy --port %PORT% put main.py main.py 2>NUL
ampy --port %PORT% put config.json config.json 2>NUL
ampy --port %PORT% mkdir src 2>NUL
ampy --port %PORT% put src/button.py src/button.py 2>NUL
ampy --port %PORT% put src/config.py src/config.py 2>NUL
ampy --port %PORT% put src/functions.py src/functions.py 2>NUL
ampy --port %PORT% put src/lcd_api.py src/lcd_api.py 2>NUL
ampy --port %PORT% put src/lcd.py src/lcd.py 2>NUL
ampy --port %PORT% put src/led.py src/led.py 2>NUL
ampy --port %PORT% put src/log.py src/log.py 2>NUL
ampy --port %PORT% put src/machine_i2c_lcd.py src/machine_i2c_lcd.py 2>NUL
ampy --port %PORT% put src/relay.py src/relay.py 2>NUL
ampy --port %PORT% put src/temp.py src/temp.py 2>NUL
ampy --port %PORT% put src/webserver.py src/webserver.py 2>NUL
ampy --port %PORT% put src/wifi.py src/wifi.py 2>NUL
ampy --port %PORT% mkdir web 2>NUL
ampy --port %PORT% put web/index.html web/index.html 2>NUL
ampy --port %PORT% put web/styles.css web/styles.css 2>NUL
echo copying files... DONE
ampy --port %PORT% ls 2>NUL
ampy --port %PORT% ls src 2>NUL
ampy --port %PORT% ls web 2>NUL
