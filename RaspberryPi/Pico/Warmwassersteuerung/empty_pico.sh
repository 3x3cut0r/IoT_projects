#!/bin/zsh
ampy --port /dev/cu.usbmodem11301 ls
echo "deleting files ..."
ampy --port /dev/cu.usbmodem11301 rm boot.py 2>/dev/null
ampy --port /dev/cu.usbmodem11301 rm main.py 2>/dev/null
ampy --port /dev/cu.usbmodem11301 rm config.json 2>/dev/null
ampy --port /dev/cu.usbmodem11301 rm config_backup.json 2>/dev/null
ampy --port /dev/cu.usbmodem11301 rmdir src 2>/dev/null
ampy --port /dev/cu.usbmodem11301 rmdir web 2>/dev/null
echo "deleting files ... DONE"
ampy --port /dev/cu.usbmodem11301 ls
