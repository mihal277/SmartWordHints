import configparser
from os import environ
from pathlib import Path

from smart_word_hints_api.app.constants import (
    CONFIG_DEBUG_SECTION,
    CONFIG_FILENAME,
    CONFIG_PROD_SECTION,
    DEBUG_MODE_ENV_VAR,
)


def get_config():
    config_path = Path(__file__).parent.parent / CONFIG_FILENAME
    api_config = configparser.ConfigParser()
    api_config.read(config_path)
    debug_mode = environ.get(DEBUG_MODE_ENV_VAR, "no")
    if debug_mode == "yes":
        return api_config[CONFIG_DEBUG_SECTION]
    if debug_mode == "no":
        return api_config[CONFIG_PROD_SECTION]
    raise ValueError(f"{DEBUG_MODE_ENV_VAR} must be yes or no")


config = get_config()
