# imports
import ujson  # https://docs.micropython.org/en/latest/library/json.html


# ==================================================
# class Config
# ==================================================
class Config:
    def __init__(self, file_name="config.json", file_name_backup="config_backup.json"):
        self.root_path = "/"
        self.file_name = self.root_path + file_name
        self.file_name_backup = self.root_path + file_name_backup
        self.config = {}
        self.load_config()
        self.reset_config()

    # file path
    def file_path(self, backup=False):
        return self.file_name_backup if backup else self.file_name

    # load config
    def load_config(self):
        # try loading config.json
        try:
            with open(self.file_path(), "r", encoding="utf-8") as file:
                self.config = ujson.load(file)
                return self.config
        except OSError:
            # try loading config_backup.json
            try:
                with open(self.file_path(backup=True), "r", encoding="utf-8") as file:
                    self.config = ujson.load(file)
                    return self.config
            except OSError:
                # set empty object
                self.config = {}
                return self.config

    # reset config
    def reset_config(self):
        self.config["temp_last_measurement"] = 0
        self.config["temp_last_measurement_time"] = 0
        self.config["temp_change_category"] = "LOW"

    # save config
    def save_config(self, backup=False):
        try:
            with open(self.file_path(backup), "w", encoding="utf-8") as file:
                ujson.dump(self.config, file)
        except OSError as e:
            print(f"ERROR: writing to {self.file_name}: {e}")

    # create config backup
    def create_config_backup(self):
        self.save_config(backup=True)

    # get value
    def get_value(self, key, default=None):
        return self.config.get(key, default)

    # get bool value
    def get_bool_value(self, key, default=False):
        try:
            value = self.config.get(str(key), bool(default))
            if isinstance(value, bool):
                return value
            if isinstance(value, int):
                if value >= 1:
                    return True
                else:
                    return False
            if isinstance(value, str):
                if value.lower() in ["true", "1", "yes", "on"]:
                    return True
                elif value.lower() in ["false", "0", "no", "off", None]:
                    return False
            return False
        except (ValueError, TypeError):
            return bool(default)

    # get int value
    def get_int_value(self, key, default=0):
        try:
            value = self.config.get(str(key), int(default))
            return int(value)
        except (ValueError, TypeError):
            return int(default)

    # get float value
    def get_float_value(self, key, default=0.0, decimal=None):
        try:
            value = self.config.get(str(key), float(default))
            float_value = float(value)
            if decimal is not None:
                return round(float_value, int(decimal))
            return float_value
        except (ValueError, TypeError):
            return float(default)

    # set value
    def set_value(self, key, value):
        self.config[str(key)] = value


# instance Config()
config = Config()
