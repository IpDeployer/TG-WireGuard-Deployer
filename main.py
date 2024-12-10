import os
import subprocess
from telegram import Bot
from telegram.error import TelegramError
import time
import random

# Load secrets from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def generate_wireguard_config():
    # Generate WireGuard key pair
    private_key = subprocess.check_output(['wg', 'genkey']).decode().strip()
    public_key = subprocess.check_output(['echo', private_key, '|', 'wg', 'pubkey'], shell=True).decode().strip()
    
    # Configuration template
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

def send_config_to_telegram(bot, config):
    try:
        bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=config.encode(), filename="wg_config.conf")
    except TelegramError as e:
        print(f"An error occurred: {e}")

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Manual sending
    if os.environ.get('MANUAL_SEND', 'false').lower() == 'true':
        config = generate_wireguard_config()
        print("Sending WireGuard config manually.")
        send_config_to_telegram(bot, config)
    
    # Automatic sending every 10 minutes
    while True:
        config = generate_wireguard_config()
        print("Sending WireGuard config automatically.")
        send_config_to_telegram(bot, config)
        time.sleep(600)  # 10 minutes in seconds

if __name__ == "__main__":
    main()