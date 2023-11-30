# imports
import ujson  # https://docs.micropython.org/en/latest/library/json.html

# setup file_name
file_name_präfix = "../"
file_name = file_name_präfix + "config.json"
file_name_backup = file_name_präfix + "config_backup.json"

# ==================================================
# functions
# ==================================================


# load config
def load_config(file_name=file_name):
    # try loading config.json
    try:
        with open(file_name, "r") as file:
            return ujson.load(file)

    except OSError:
        # try loading config_backup.json instead
        try:
            with open(file_name_backup, "r") as file:
                return ujson.load(file)

        except OSError:
            # return empty object
            return {}


# save config
def save_config(config, file_name=file_name):
    # write config to file
    try:
        with open(file_name, "w") as file:
            ujson.dump(config, file)

    except OSError as e:
        print("error while writing to config.json: ", e)


# create config backup
def create_config_backup():
    try:
        with open(file_name, "r") as config_file:
            with open(file_name_backup, "w") as backup_file:
                ujson.dump(ujson.load(config_file), backup_file)
    except OSError as e:
        print("error while writing to config_backup.json: ", e)


# get value
def get_value(key):
    config = load_config()
    return config[str(key)]


# set value
def set_value(key, value, file_name=file_name):
    # load config
    config = load_config(file_name)

    # replace value from key
    config[key] = value

    # save config
    save_config(config)
