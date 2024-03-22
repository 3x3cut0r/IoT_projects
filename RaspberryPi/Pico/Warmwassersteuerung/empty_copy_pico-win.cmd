ampy --port COM10 ls
echo "deleting files ..."
ampy --port COM10 rm boot.py
ampy --port COM10 rm main.py
ampy --port COM10 rm config.json
ampy --port COM10 rm config_backup.json
ampy --port COM10 rmdir src
ampy --port COM10 rmdir web
ampy --port COM10 rmdir .old
echo "deleting files ... DONE"
ampy --port COM10 ls
echo "copying files ..."
ampy --port COM10 put main.py :main.py
ampy --port COM10 put config.json :config.json
ampy --port COM10 mkdir src
ampy --port COM10 put src/button.py :src/button.py
ampy --port COM10 put src/config.py :src/config.py 
ampy --port COM10 put src/functions.py :src/functions.py 
ampy --port COM10 put src/lcd_api.py :src/lcd_api.py 
ampy --port COM10 put src/lcd.py :src/lcd.py 
ampy --port COM10 put src/led.py :src/led.py 
ampy --port COM10 put src/log.py :src/log.py 
ampy --port COM10 put src/machine_i2c_lcd.py :src/machine_i2c_lcd.py 
ampy --port COM10 put src/relay.py :src/relay.py 
ampy --port COM10 put src/temp.py :src/temp.py 
ampy --port COM10 put src/webserver.py :src/webserver.py 
ampy --port COM10 put src/wifi.py :src/wifi.py 
ampy --port COM10 mkdir web
ampy --port COM10 put web/index.html :web/index.html
ampy --port COM10 put web/styles.css :web/styles.css
echo "copying files ... DONE"
ampy --port COM10 ls
