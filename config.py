import json
import codecs

with codecs.open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)
    print(config_data)

try:
    TOKEN = config_data['TOKEN']
    ADMIN_CHAT_ID = config_data['ADMIN_CHAT_ID']
    API_ID = config_data['API_ID']
    API_HASH = config_data['API_HASH']
    CHANNEL_LINK = config_data['CHANNEL_LINK']
    CHANNEL_USERNAME = config_data['CHANNEL_USERNAME']
    PHONE = config_data['PHONE']
    IGNORED_POSTS = config_data['IGNORED_POSTS']
    MENU = config_data['MENU']
    RECOMMENDED_FILTERS = config_data['RECOMMENDED_FILTERS']
except KeyError as e:
    raise KeyError(f"Missing required key in config.json: {e}")
