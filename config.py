import json

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError("Config file 'config.json' not found in the root directory.")
    except json.JSONDecodeError:
        raise ValueError("The 'config.json' file is not a valid JSON.")

def get_config_value(config_data, key):
    if key in config_data:
        return config_data[key]
    else:
        raise KeyError(f"Key '{key}' not found in 'config.json'.")

config_data = load_config()

try:
    TOKEN = get_config_value(config_data, 'GDP_BOT_TOKEN')
    ADMIN_CHAT_ID = get_config_value(config_data, 'GDP_BOT_ADMIN_CHAT_ID')
    API_ID = get_config_value(config_data, 'GDP_BOT_API_ID')
    API_HASH = get_config_value(config_data, 'GDP_BOT_API_HASH')
    CHANNEL_LINK = get_config_value(config_data, 'GDP_BOT_CHANNEL_LINK')
    PHONE = get_config_value(config_data, 'GDP_BOT_PHONE')
except KeyError as error:
    print("Error:", error)
    raise
