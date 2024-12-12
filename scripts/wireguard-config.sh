#!/bin/bash

set -eu

# Set umask to ensure secure file permissions
umask 0777

# Ensure the temporary directory structure exists and is writable
mkdir -p "./wg_temp/clients.d"
mkdir -p "./wg_temp/repo.d"
chmod -R 0777 "./wg_temp"

# Define WireGuard variables
export wg_ip="10.0.0.1"
export wg_port="51820"
export wg_clients=5
export wg_dns="8.8.8.8,8.8.4.4"
export wg_endpoint="example.com"
export wg_tunnel="full"
export wg_users="user1,user2,user3,user4,user5"

# Define the WireGuard directory structure
export wg_root="./wg_temp"
export wg_client_dir="${wg_root}/clients.d"
export wg_repo_dir="${wg_root}/repo.d"

# Calculate network prefix
wg_int_net=$(awk -F. '{print $1 "." $2 "." $3}' <<< ${wg_ip})

# Ensure necessary directories exist
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

# Ensure the server config file is created with the right permissions
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

# Skip system service restart in GitHub Actions
# systemctl restart wg-quick@wg0.service