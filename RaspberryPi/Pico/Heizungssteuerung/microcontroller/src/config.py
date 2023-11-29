# imports
import ujson

# setup file_name
file_name_präfix = "../"
file_name = file_name_präfix + 'config.json'

# ==================================================
# functions
# ==================================================


# load config
def load_config(file_name = file_name):
    try:
        with open(file_name, 'r') as file:
            return ujson.load(file)
          
    except OSError:
      
        # return defaults
        # todo: load config defaults
        return {}


# save config
def save_config(config, file_name = file_name):
    # write config to file
    try:
        with open(file_name, 'w') as file:
            ujson.dump(config, file)
            
    except OSError as e:
        print("error while writing to config.json", e)


# get value
def get_value(key):
    config = load_config()
    return config[str(key)]


# set value
def set_value(key, value, file_name = file_name):
    # load config
    config = load_config(file_name)

    # replace value from key
    config[key] = value

    # save config
    save_config(config)
