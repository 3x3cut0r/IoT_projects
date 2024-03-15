ampy --port COM10 ls
echo "deleting files ..."
ampy --port COM10 rm boot.py
ampy --port COM10 rm main.py
ampy --port COM10 rm config.json
ampy --port COM10 rm config_backup.json
ampy --port COM10 rmdir src
ampy --port COM10 rmdir web
echo "deleting files ... DONE"
ampy --port COM10 ls
