import json
import codecs

with codecs.open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

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

    SFTP_HOST = config_data['SFTP_HOST']
    SFTP_PORT = config_data['SFTP_PORT']
    SFTP_USER = config_data['SFTP_USER']
    SFTP_PASSWORD = config_data['SFTP_PASSWORD']
    SFTP_REMOTE_PATH = config_data['SFTP_REMOTE_PATH']

    ABOUT_COVER_URL = config_data['ABOUT_COVER_URL']
    ABOUT_COVER_AMOUNT = config_data['ABOUT_COVER_AMOUNT']

    # ABOUT_COVER_URL: Set the URL pattern for the about cover images. If ABOUT_COVER_AMOUNT is more than 1,
    # include the keyword "{index}" in the URL where the random number should be placed.
    # Example: "https://url.to/image-{index}.png"
except KeyError as e:
    raise KeyError(f"Missing required key in config.json: {e}")
