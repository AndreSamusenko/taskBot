from configparser import ConfigParser

FILENAME = "config.ini"

parser = ConfigParser()
parser.read(FILENAME)

PYTHON_PATH = parser["SETTINGS"]["PYTHON_PATH"]

BOT_TOKEN = parser["TOKENS"]["BOT_TOKEN"]
GIST_TOKEN = parser["TOKENS"]["GIST_TOKEN"]

print(BOT_TOKEN)