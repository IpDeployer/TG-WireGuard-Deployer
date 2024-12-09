import os
import time
import requests
import json

# Load secrets from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Environment variables TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are required")


def generate_configuration():
    """
    Simulate generating a WireGuard configuration for Cloudflare Warp.
    Replace this function with your actual configuration generation logic.
    """
    config = {
        "peer_public_key": "samplePublicKey",
        "server": "sample.server.com",
        "server_port": 51820,
        "private_key": "samplePrivateKey",
        "mtu": 1420,
        "local_address": ["192.0.2.1/24"]
    }
    return json.dumps(config, indent=4)


def send_to_telegram(message):
    """
    Send the given message to the specified Telegram channel.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.text}")


if __name__ == "__main__":
    while True:
        config = generate_configuration()
        send_to_telegram(f"Generated Configuration:\n{config}")
        time.sleep(300)  # Wait for 5 minutes (300 seconds)