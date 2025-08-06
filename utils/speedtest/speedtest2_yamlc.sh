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

echo "Downloading latest LiteSpeedTest..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/latest/download/lite-linux-amd64.gz
gunzip lite-linux-amd64.gz
LITE_BINARY_NAME=$(find . -name "lite-linux-amd64*")
mv "$LITE_BINARY_NAME" lite-linux-amd64


echo "Downloading configuration files..."
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml
wget -O proxychains.conf https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/proxychains.conf
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json


echo "Setting up ProxyChains..."
sudo apt-get update
sudo apt-get install -y proxychains
sudo chmod 777 /etc/proxychains.conf
sudo mv -f proxychains.conf /etc/proxychains.conf

chmod +x ./clash
chmod +x ./lite-linux-amd64

sudo pkill -f clash

echo "Starting Clash as gateway proxy..."
./clash -f clash_config.yml &
sleep 5 

echo "Running LiteSpeedTest through the proxy chain..."
sudo nohup proxychains ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_yaml.yml > speedtest.log 2>&1 &