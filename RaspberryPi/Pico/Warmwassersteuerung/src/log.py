from src.config import config  # Config() instance


# log messages to console
def log(level="INFO", message=""):
    level = level.upper()
    levels = {"OFF": 0, "ERROR": 1, "WARN": 2, "INFO": 3, "VERBOSE": 4}
    log_level = config.get_value("log_level", "OFF").upper()

    # disable log, if log_level is not valid
    if log_level not in levels:
        log_level = "OFF"

    if log_level != "OFF" and levels[level] <= levels[log_level]:
        # convert VERBOSE to INFO
        if level == "VERBOSE":
            level = "INFO"

        # print log
        print(f"{level}: {message}")
