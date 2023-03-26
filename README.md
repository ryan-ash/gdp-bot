# GDP Telegram Bot

[Demo](https://t.me/GameDevPornBot) | [Creation Log](https://drive.google.com/file/d/1G34F4wTs2C2XSudk7t8WWfTqbrLythuA/view?usp=sharing)

The GDP Telegram Bot is a useful utility designed to provide users with updates from a specified Telegram channel. The bot allows users to subscribe and customize their preferences, ensuring they only receive content that matches their interests.

This bot was primarily developed by GPT-4, an AI language model by OpenAI.

## Features

The GDP Telegram Bot offers the following features:

1. **Subscribe/Unsubscribe:** Users can easily subscribe or unsubscribe from receiving updates.

2. **Set Schedule:** Users can set a custom schedule for receiving updates, ensuring that they receive content at their preferred times.

3. **Set Filters:** Users can apply filters to only receive updates containing specific keywords or phrases.

4. **Fetch Post:** Users can request a post from the channel that matches their filters on-demand.

5. **About Information:** Users can view information about the bot and its functionality, as well as a list of commands.

## Commands

The following commands are available for users to interact with the bot:

- `/gdp_sub`: Subscribe to receive updates from the channel.
- `/gdp_unsub`: Unsubscribe from receiving updates.
- `/gdp_schedule`: Set a custom schedule for receiving updates.
- `/gdp_filter`: Set filters to customize the content you receive.
- `/gdp_fetch`: Fetch a post from the channel that matches your filters.
- `/gdp_about`: Show information about the bot and its commands.

## Database

The bot uses SQLite for storing user subscription data, filters, and schedules. The database is organized into two tables:

1. `subscriptions`: Stores information about user subscriptions, including chat_id, active status, filters, and schedules.
2. `posts`: Stores content from the Telegram channel for easy access and filtering.

The bot also includes a script for retrieving statistics about active subscriptions, total subscriptions, and a breakdown of users and groups.

## Setup

1. Clone the repository and install the required dependencies.
2. Set up the bot on the Telegram Bot API and obtain your bot token.
3. Create a Telegram app to get your `api_id` and `api_hash` by following the instructions on [Telegram's website](https://my.telegram.org/auth).
4. Create `config.json` from `config.json.bak` and replace the placeholder values with your bot token, channel username, api_id, and api_hash.
5. Run the bot and enjoy receiving customized updates from your favorite Telegram channel.

## Additional Scripts

1. `sync_posts.py`: This script synchronizes the posts from the Telegram channel to the local SQLite database. It then syncs the local db to remote server where your production bot is deployed. This is done to avoid triggering telegram protection for logging in from weird places that will log you out from your current clients.
2. `search_post.py`: This script allows you to search for a post containing a specific string in the local SQLite database.
3. `stats.py`: This script provides statistics about the bot's subscriptions, including the number of active subscriptions, total subscriptions, and a breakdown of users and groups. Run the script to get a human-readable output of these statistics.

To use these scripts, simply run them from the command line after setting up the bot.
