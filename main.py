import os
import subprocess
from telegram import Bot
from telegram.error import TelegramError

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
        print("WireGuard config sent successfully.")
    except TelegramError as e:
        print(f"An error occurred: {e}")

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    config = generate_wireguard_config()
    send_config_to_telegram(bot, config)

if __name__ == "__main__":
    main()