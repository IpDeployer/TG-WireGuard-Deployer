import time
import requests
import json

# Load secrets from environment variables
TELEGRAM_TOKEN = "<your_telegram_bot_token>"  # Replace with the GitHub Actions secret name
TELEGRAM_CHAT_ID = "<your_channel_chat_id>"  # Replace with the GitHub Actions secret name

def generate_configuration():
    # Simulate the configuration generation process
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