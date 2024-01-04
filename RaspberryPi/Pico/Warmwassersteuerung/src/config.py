# imports
import ujson  # https://docs.micropython.org/en/latest/library/json.html

# config
config = {}

# file_name
file_name_präfix = "../"
file_name = "config.json"
file_name_backup = "config_backup.json"

# file_path
file_path = file_name_präfix + file_name
file_path_backup = file_name_präfix + file_name_backup

# ==================================================
# functions
# ==================================================


# load config
def load_config(file_path=file_path):
    global config

    # try loading config.json
    try:
        with open(file_path, "r") as file:
            config = ujson.load(file)
            return config

    except OSError:
        # try loading config_backup.json instead
        try:
            with open(file_path_backup, "r") as file:
                config = ujson.load(file)
                return config

        except OSError:
            # set empty object
            config = {}
            return config


# reset config
def reset_config():
    global config
    config["temp_last_measurement"] = 0
    config["temp_last_measurement_time"] = 0
    config["temp_change_category"] = "LOW"


# init config
def init_config():
    load_config()
    reset_config()


# save config
def save_config(file_path=file_path):
    global config

    # write config to file
    try:
        with open(file_path, "w") as file:
            ujson.dump(config, file)

    except OSError as e:
        print("error while writing to " + str(file_name) + ": ", e)


# create config backup
def create_config_backup():
    save_config(file_path_backup)


# get value
def get_value(key, default=None):
    try:
        return config[str(key)]
    except:
        if default is not None:
            return default
        else:
            return None


# get int value
def get_int_value(key, default=0):
    try:
        return int(config[str(key)])
    except:
        return int(default)


# get float value
def get_float_value(key, default=0.0, decimal=None):
    try:
        if decimal is not None:
            return round(float(config[str(key)]), int(decimal))
        else:
            return float(config[str(key)])
    except:
        return float(default)


# set value
def set_value(key, value):
    global config
    config[key] = value
