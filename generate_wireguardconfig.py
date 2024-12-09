import os
import subprocess
from datetime import datetime
import requests
import base64

# Function to generate WireGuard configuration
def generate_config():
    private_key = subprocess.check_output(['wg', 'genkey']).decode('utf-8').strip()
    public_key = subprocess.check_output(['echo', private_key, '|', 'wg', 'pubkey'], shell=True).decode('utf-8').strip()
    
    config = f"[Interface]\nPrivateKey = {private_key}\nAddress = 10.0.0.2/24\nListenPort = 51820\n\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = 0.0.0.0/0\nEndpoint = example.com:51820"
    
    # Convert to base64 for sending in a similar format to .conf.cobf
    encoded_config = base64.b64encode(config.encode()).decode()
    
    with open('wg_config.conf', 'w') as f:
        f.write(config)

    return encoded_config

# Function to send to Telegram
def send_to_telegram(message):
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    token = os.environ.get('TELEGRAM_TOKEN')
    if not chat_id or not token:
        print("Telegram CHAT_ID or TOKEN not set in environment variables.")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": f"WireGuard Config (base64 encoded):\n```\n{message}\n```",
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message to Telegram: {response.status_code}")

if __name__ == "__main__":
    config = generate_config()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Updated at {timestamp}: {config}"
    send_to_telegram(message)