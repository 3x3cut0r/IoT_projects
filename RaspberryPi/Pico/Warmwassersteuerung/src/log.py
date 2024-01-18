from src.config import config  # Config() instance


# log messages to console
def log(level="INFO", message=""):
    level = level.upper()
    levels = {"OFF": 0, "ERROR": 1, "WARN": 2, "VERBOSE": 3, "INFO": 4}
    log_level = config.get_value("log_level", "OFF").upper()
    if log_level not in levels:
        log_level = "OFF"
    if level == "VERBOSE":
        level = "INFO"
    if log_level != "OFF" and levels[level] <= levels[log_level]:
        print(f"{level}: {message}")
