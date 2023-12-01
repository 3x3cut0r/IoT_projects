# imports
import ujson  # https://docs.micropython.org/en/latest/library/json.html

# setup file_name
file_name_präfix = "../"
file_name = file_name_präfix + "config.json"
file_name_backup = file_name_präfix + "config_backup.json"

# config
config = {}

# ==================================================
# functions
# ==================================================


# load config
def load_config(file_name=file_name):
    global config

    # try loading config.json
    try:
        with open(file_name, "r") as file:
            config = ujson.load(file)

    except OSError:
        # try loading config_backup.json instead
        try:
            with open(file_name_backup, "r") as file:
                config = ujson.load(file)

        except OSError:
            # set empty object
            config = {}


# init config
def init_config():
    global config
    load_config()
    config["temp_last_measurement"] = 0
    config["temp_last_measurement_time"] = 0
    config["temp_change_category"] = "LOW"


# save config
def save_config(file_name=file_name):
    global config

    # write config to file
    try:
        with open(file_name, "w") as file:
            ujson.dump(config, file)

    except OSError as e:
        print("error while writing to " + str(file_name) + ": ", e)


# create config backup
def create_config_backup():
    save_config(file_name_backup)


# get value
def get_value(key):
    return config[str(key)]


# set value
def set_value(key, value):
    global config
    config[key] = value
