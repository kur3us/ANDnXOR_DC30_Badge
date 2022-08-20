import ujson as json

CONFIG_FILE = "/config.json"

KEY_NAME = 'name'
KEY_OFFSET = 'offset'
KEY_WIFI_SSID = 'wifi_ssid'
KEY_WIFI_PWD = 'wifi_pwd'
KEY_INVERTED = 'inverted'
KEY_CURRENT = 'current'

DEFAULT_NAME = 'Ma77D@m0n'
# Vegas is PST, DEFCON is during daylight savings
DEFAULT_OFFSET = -7 

DEFAULT_INVERTED = False

DEFAULT_WIFI_SSID = 'Matt Damon'
DEFAULT_WIFI_PWD = 'WEmustSAVEhim'

DEFAULT_CURRENT = False

config = {}

def load(): 
    global config
    try:
        with open(CONFIG_FILE) as cfg_file:
            config = json.load(cfg_file)

        # Make sure this value is in config, it's special since it was added late
        # during development and some prototypes won't have it
        if not KEY_CURRENT in config:
            config[KEY_CURRENT] = DEFAULT_CURRENT
    except:
        print("CONFIG: Unable to open config file, going with defaults, this is okay! See rtfm.md.")
        save()

def reset():
    config[KEY_NAME] = DEFAULT_NAME
    config[KEY_OFFSET] = DEFAULT_OFFSET
    config[KEY_WIFI_SSID] = DEFAULT_WIFI_SSID
    config[KEY_WIFI_PWD] = DEFAULT_WIFI_PWD
    config[KEY_INVERTED] = DEFAULT_INVERTED
    config[KEY_CURRENT] = DEFAULT_CURRENT

def save():
    with open(CONFIG_FILE, 'w') as cfg_file:
        json.dump(config, cfg_file)

# ensure factory defaults on load
reset()