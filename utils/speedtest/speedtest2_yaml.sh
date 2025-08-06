#!/bin/bash

# --- 1. Download Core Binaries ---

# Fetch the latest mihomo (Clash.Meta core)
echo "Fetching latest mihomo release URL..."
MIHOMO_URL=$(curl -s "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest" | grep "browser_download_url.*mihomo-linux-amd64-v1-.*\.gz" | cut -d '"' -f 4 | head -n 1)

if [ -z "$MIHOMO_URL" ]; then
    echo "Failed to get mihomo download URL. Trying legacy name..."
    MIHOMO_URL=$(curl -s "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest" | grep "browser_download_url.*mihomo-linux-amd64-compatible.*\.gz" | cut -d '"' -f 4 | head -n 1)
    if [ -z "$MIHOMO_URL" ]; then
        echo "Failed to get mihomo download URL on fallback. Exiting."
        exit 1
    fi
fi

echo "Downloading mihomo from: $MIHOMO_URL"
wget -O clash.gz "$MIHOMO_URL"
# FIX 1: Decompress the archive and directly output the contents to a file named 'clash'
gunzip -c clash.gz > clash


# Fetch the latest LiteSpeedTest
echo "Fetching latest LiteSpeedTest release URL..."
LITE_URL=$(curl -s "https://api.github.com/repos/xxf098/LiteSpeedTest/releases/latest" | grep "browser_download_url.*lite-linux-amd64.*\.gz" | cut -d '"' -f 4 | head -n 1)

if [ -z "$LITE_URL" ]; then
    echo "Failed to get LiteSpeedTest download URL. Exiting."
    exit 1
fi

echo "Downloading LiteSpeedTest from: $LITE_URL"
wget -O lite-linux-amd64.gz "$LITE_URL"
# FIX 2: Apply the same robust method to LiteSpeedTest
gunzip -c lite-linux-amd64.gz > lite-linux-amd64


# --- 2. Download Configuration Files ---
echo "Downloading configuration files..."
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml


# --- 3. Execute Clash and Speed Test ---
# Make binaries executable
chmod +x ./clash
chmod +x ./lite-linux-amd64

# Start Clash (mihomo) to act as the test engine
echo "Starting Clash (mihomo) engine..."
./clash -f clash_config.yml &
sleep 5 # Wait for Clash to initialize

# Run LiteSpeedTest
echo "Running LiteSpeedTest..."
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_yaml.yml > speedtest.log 2>&1 &
