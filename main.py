import os
import subprocess
from telegram import Bot
from telegram.error import TelegramError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load secrets from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def generate_wireguard_config():
    try:
        private_key = subprocess.check_output(['wg', 'genkey']).decode().strip()
        public_key = subprocess.check_output(['echo', private_key, '|', 'wg', 'pubkey'], shell=True).decode().strip()
        
        config = f"""[Interface]
PrivateKey = {private_key}
Address = 10.0.0.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = {public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = your.vpn.server:51820
PersistentKeepalive = 25
"""
        return config
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating WireGuard config: {e}")
        return None

def send_config_to_telegram(bot, config):
    try:
        bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=config.encode(), filename="wg_config.conf")
        logger.info("WireGuard config sent successfully.")
    except TelegramError as e:
        logger.error(f"An error occurred while sending to Telegram: {e}")

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    config = generate_wireguard_config()
    if config:
        send_config_to_telegram(bot, config)
    else:
        logger.error("Failed to generate WireGuard config.")

if __name__ == "__main__":
    main()