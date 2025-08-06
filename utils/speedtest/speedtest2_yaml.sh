#!/bin/bash
# Exit immediately if any command fails
set -e

echo "--- Starting Speedtest Script ---"

# 1. Download Mihomo
echo "[1/4] Downloading Mihomo v1.19.12 binary..."
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz

# 2. Unzip Mihomo
echo "[2/4] Unzipping Mihomo..."
gunzip mihomo-linux-amd64-v1.19.12.gz
echo "--- Files after unzip ---"
ls -la # DEBUG: Show the exact name of the unzipped file

# 3. Rename the binary to 'clash'
# FIX: Use the correct source filename 'mihomo-linux-amd64'
echo "[3/4] Renaming 'mihomo-linux-amd64' to 'clash'..."
mv mihomo-linux-amd64 clash
echo "--- Files after rename ---"
ls -la # DEBUG: Confirm 'clash' now exists

# 4. Download other tools and configs
echo "[4/4] Downloading other tools and configs..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json

# --- EXECUTION ---
echo "--- Starting Mihomo and running speed test ---"
chmod +x ./clash
./clash -f ./utils/speedtest/clash_config_eu.yml &
sleep 5

chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_yaml.yml > speedtest.log 2>&1 &