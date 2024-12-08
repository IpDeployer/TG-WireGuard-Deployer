import os
import json
import random
import requests
import subprocess
from pyrogram import Client

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def generate_wireguard_config(json_url, public_ip):
    # Fetch IP:Port list from GitHub raw URL
    response = requests.get(json_url)
    ip_port_list = response.json()
    
    # Choose random IP:Port
    endpoint = random.choice(ip_port_list)

    # Generate private and public keys
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public_key = subprocess.check_output(["echo", private_key, "|", "wg", "pubkey"], shell=True).decode().strip()

    # Generate local address
    local_address = f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}/24"

    # Create WireGuard config
    wg_config = f"""
[Interface]
PrivateKey = {private_key}
Address = {local_address}
MTU = 1280
Reserved = 

[Peer]
PublicKey = {public_ip}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    # Save to file
    with open("wireguard.conf", "w") as file:
        file.write(wg_config)

    return wg_config, private_key

def generate_v2ray_uri(public_ip):
    # Example V2Ray URI format
    return f"v2ray://{public_ip}"

def send_to_telegram(message, file_path):
    app = Client("telegram_bot", bot_token=TELEGRAM_TOKEN)

    with app:
        app.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        app.send_document(chat_id=TELEGRAM_CHAT_ID, document=file_path)

if name == "main":
    try:
        # Inputs
        json_url = "https://raw.githubusercontent.com/<username>/<repo>/main/ip_ports.json"
        public_ip = "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo="

        # Generate configurations
        wg_config, private_key = generate_wireguard_config(json_url, public_ip)
        v2ray_uri = generate_v2ray_uri(public_ip)

        # Send to Telegram
        message = f"WireGuard Config:\n{wg_config}\n\nV2Ray URI:\n{v2ray_uri}"
        send_to_telegram(message, "wireguard.conf")
    except Exception as e:
        print(f"Error: {e}")
