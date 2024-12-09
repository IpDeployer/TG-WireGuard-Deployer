import os
from telegram import Bot
from telegram.error import TelegramError

def send_config_to_channel(bot_token, channel_id, config_file):
    try:
        bot = Bot(token=bot_token)
        with open(config_file, 'rb') as file:
            bot.send_document(chat_id=channel_id, document=file)
    except TelegramError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bot_token = os.environ['BOT_TOKEN']
    channel_id = os.environ['CHANNEL_ID']
    config_file = 'path/to/generated/config.conf'  # Adjust this path
    send_config_to_channel(bot_token, channel_id, config_file)