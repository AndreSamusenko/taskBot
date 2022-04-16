from configparser import ConfigParser


class ConfigData:
    FILENAME = "scr/config.ini"

    def __init__(self):
        parser = ConfigParser()
        parser.read(self.FILENAME)

        self.PYTHON_PATH = parser["SETTINGS"]["PYTHON_PATH"]
        self.BOT_TOKEN = parser["TOKENS"]["BOT_TOKEN"]
        self.GIST_TOKEN = parser["TOKENS"]["GIST_TOKEN"]
