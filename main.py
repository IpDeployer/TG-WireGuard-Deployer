import os
import subprocess
from telegram import Bot, InputFile
from telegram.error import TelegramError
import logging
import time

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load secrets from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def generate_wireguard_config():
    """
    Generate a WireGuard configuration file with a new key pair.
    
    Returns:
        str: WireGuard configuration string
    """
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
Endpoint = your.vpn.server:51820  # Replace with your actual server endpoint
PersistentKeepalive = 25
"""
        return config
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate WireGuard keys: {e}")
        return None

def send_config_to_telegram(bot, config):
    """
    Send the WireGuard configuration to the specified Telegram chat.

    Args:
        bot (Bot): Telegram bot instance
        config (str): WireGuard configuration to send
    """
    if config:
        try:
            # Create a temporary file to send as a document
            with open('wg_config.conf', 'w') as f:
                f.write(config)
            
            with open('wg_config.conf', 'rb') as f:
                bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=InputFile(f, 'wg_config.conf'))
            logger.info("WireGuard config sent successfully.")
        except TelegramError as e:
            logger.error(f"Error sending WireGuard config: {e}")
    else:
        logger.error("No WireGuard config to send.")

def main():
    """
    Main function to initialize the bot and send the configuration.
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    
    # Generate WireGuard config
    config = generate_wireguard_config()
    
    # Send the config to Telegram
    send_config_to_telegram(bot, config)

if __name__ == "__main__":
    main()