ampy --port COM10 ls
echo "deleting files ..."
ampy --port COM10 rm boot.py 2>/dev/null
ampy --port COM10 rm main.py 2>/dev/null
ampy --port COM10 rm config.json 2>/dev/null
ampy --port COM10 rm config_backup.json 2>/dev/null
ampy --port COM10 rmdir src 2>/dev/null
ampy --port COM10 rmdir web 2>/dev/null
echo "deleting files ... DONE"
ampy --port COM10 ls
