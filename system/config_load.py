try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from system.crypto_functions import random_string

config_path = "./configuration/settings.ini"

def config_dict():
    config = configparser.ConfigParser()
    config.read("./configuration/settings.ini")
    return config

def change_secret_key():
    config = configparser.ConfigParser()
    config.read("./configuration/settings.ini")
    config.set('main', 'secret', random_string(20))
    with open("./configuration/settings.ini", 'w') as configfile:
        config.write(configfile)
    return

def recover_config():
    pass
    # TODO
