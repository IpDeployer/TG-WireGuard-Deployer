import os
import subprocess
from telegram import Bot, InputFile
from telegram.error import TelegramError
import logging

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
        public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).decode().strip()

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
            temp_file_path = 'wg_config.conf'
            with open(temp_file_path, 'w') as f:
                f.write(config)

            with open(temp_file_path, 'rb') as f:
                bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=InputFile(f, temp_file_path))
            logger.info("WireGuard config sent successfully.")
        except TelegramError as e:
            logger.error(f"Error sending WireGuard config: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)  # Clean up the temporary file
    else:
        logger.error("No WireGuard config to send.")

def main():
    """
    Main function to initialize the bot and send the configuration.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variables.")
        return

    bot = Bot(token=TELEGRAM_TOKEN)

    # Generate WireGuard config
    config = generate_wireguard_config()

    # Send the config to Telegram
    send_config_to_telegram(bot, config)

if __name__ == "__main__":
    main()