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
gunzip clash.gz
mv mihomo clash

wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/latest/download/lite-linux-amd64.gz
gunzip lite-linux-amd64.gz
LITE_BINARY_NAME=$(find . -name "lite-linux-amd64*")
mv "$LITE_BINARY_NAME" lite-linux-amd64

wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml

chmod +x ./clash
./clash -f clash_config.yml &
sleep 5

chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_yaml.yml > speedtest.log 2>&1 &