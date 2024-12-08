import json
import base64
import os

def generate_wireguard_config():
    config = {
        "local_address": [
            "172.16.0.2/32",
            "2606:4700:110:8a6d:21bd:c9c1:a8:747a/128"
        ],
        "mtu": 1280,
        "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
        "private_key": base64.b64encode(os.urandom(32)).decode(),  # Generate a new private key
        "reserved": [
            149, 94, 161
        ],
        "server": "engage.cloudflareclient.com",
        "server_port": 2408
    }

    wg_url = f"wireguard://{config['private_key'].replace('/', '%2F').replace('+', '%2B').replace('=', '%3D')}@{config['server']}:{config['server_port']}?address={','.join(config['local_address']).replace('/', '%2F').replace(':', '%3A')}&reserved={','.join(map(str, config['reserved']))}&publickey={config['peer_public_key'].replace('/', '%2F').replace('+', '%2B').replace('=', '%3D')}&mtu={config['mtu']}#Warp"

    return json.dumps(config, indent=2), wg_url

if __name__ == "__main__":
    config_json, config_url = generate_wireguard_config()
    print(config_json)
    print(config_url)