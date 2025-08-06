
echo "Downloading Mihomo v1.19.12 binary..."
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz
gunzip mihomo-linux-amd64-v1.19.12.gz
mv mihomo-linux-amd64 clash

# Download the Lite Speed Tester
echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# --- CONFIGURATION ---
echo "Downloading LiteSpeedTest config..."
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json

# --- EXECUTION ---
echo "Starting Mihomo with local multi-provider config..."
chmod +x ./clash
./clash -f ./utils/speedtest/clash_config_eu.yml &
sleep 5

echo "Running LiteSpeedTest..."
chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_yaml.yml > speedtest.log 2>&1 &