#!/bin/zsh
ampy --port /dev/cu.usbmodem11301 ls
echo "deleting files ..."
ampy --port /dev/cu.usbmodem11301 rm boot.py
ampy --port /dev/cu.usbmodem11301 rm main.py
ampy --port /dev/cu.usbmodem11301 rm config.json
ampy --port /dev/cu.usbmodem11301 rm config_backup.json
ampy --port /dev/cu.usbmodem11301 rmdir src
ampy --port /dev/cu.usbmodem11301 rmdir web
echo "deleting files ... DONE"
ampy --port /dev/cu.usbmodem11301 ls
