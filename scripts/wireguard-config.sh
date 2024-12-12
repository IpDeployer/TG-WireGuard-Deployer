#!/bin/bash

set -eu

# Ensure all environment variables are set or use default values
wg_root="./wg_temp"
wg_client_dir="${wg_root}/clients.d"
wg_repo_dir="${wg_root}/repo.d"

# Use the environment variables defined in the workflow or fall back to defaults
wg_int_net=$(awk -F. '{print $1 "." $2 "." $3}' <<< ${wg_ip})

# Ensure the necessary directories exist
mkdir -p "${wg_client_dir}"
mkdir -p "${wg_repo_dir}"

# Function to generate keypair
function gen_keypair ()
{
    if [ ! -f "${1}/${2}.privkey" ]
    then
        wg genkey > "${1}/${2}.privkey" 2>/dev/null
    fi

    chmod 0600 "${1}/${2}.privkey"
    wg pubkey < "${1}/${2}.privkey" > "${1}/${2}.pubkey"
    chmod 0644 "${1}/${2}.pubkey"
}

# Function to generate preshared key (PSK)
function gen_psk ()
{
    if [ ! -f "${1}/${2}.psk" ]
    then
        wg genpsk > "${1}/${2}.psk"
    fi

    chmod 0600 "${1}/${2}.psk"
}

# Generate server configuration file
gen_keypair "${wg_root}" server

cat << EOF > "${wg_root}/wg0.conf"
[Interface]
PrivateKey = $(cat "${wg_root}/server.privkey")
Address = ${wg_int_net}.1/24
ListenPort = ${wg_port}
EOF

# Generate client configurations and related files
for (( i=1; i<=${wg_clients}; i++ ))
do
    gen_keypair "${wg_client_dir}" $((i+1))
    gen_psk "${wg_client_dir}" $((i+1))

    cat << EOF >> "${wg_root}/wg0.conf"
[Peer]
PublicKey = $(cat "${wg_client_dir}/$((i+1)).pubkey")
PresharedKey = $(cat "${wg_client_dir}/$((i+1)).psk")
AllowedIPs = ${wg_int_net}.$((i+1))/32
EOF

    cat << EOF > "${wg_client_dir}/$((i+1)).conf"
[Interface]
PrivateKey = $(cat "${wg_client_dir}/$((i+1)).privkey")
Address = ${wg_int_net}.$((i+1))/24
DNS = ${wg_dns}

[Peer]
PublicKey = $(cat "${wg_root}/server.pubkey")
PresharedKey = $(cat "${wg_client_dir}/$((i+1)).psk")
Endpoint = ${wg_endpoint}:${wg_port}
PersistentKeepalive = 30
EOF

    case ${wg_tunnel} in
        split)
            echo "AllowedIPs = ${wg_int_net}.0/24" >> "${wg_client_dir}/$((i+1)).conf"
            ;;
        full)
            echo "AllowedIPs = 0.0.0.0/0" >> "${wg_client_dir}/$((i+1)).conf"
            ;;
        *)
            echo "Error! Invalid tunnel type: ${wg_tunnel}"
            exit 1
    esac

    cat "${wg_client_dir}/$((i+1)).conf" | qrencode -t PNG -o "${wg_client_dir}/$((i+1)).png"
    chmod 0600 "${wg_client_dir}/$((i+1)).conf"
    chmod 0600 "${wg_client_dir}/$((i+1)).png"
done

# Optionally, you can handle publishing the configuration to a remote repository or other actions
# For example, you could push the generated files to a git repo here
# If using GitHub, uncomment and modify below for git actions
# git add -A
# git commit -m "Generated WireGuard configurations"
# git push

# Restart the WireGuard service (ensure you have a proper wg-quick service)
systemctl restart wg-quick@wg0.service