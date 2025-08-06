# --- SETUP ---

# Download the Mihomo binary to a predictable filename 'mihomo.gz'
echo "Downloading Mihomo v1.19.12 binary..."
wget -O mihomo.gz https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz

# FIX: Unzip the contents directly into a file named 'clash'.
gunzip -c mihomo.gz > clash

# Download the Lite Speed Tester
echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# --- CONFIGURATION ---
echo "Downloading configs and setting up ProxyChains..."
wget -O proxychains.conf https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/proxychains.conf
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json

sudo apt-get install proxychains -y
sudo mv -f proxychains.conf /etc/proxychains.conf

# --- EXECUTION ---
echo "Starting Mihomo with local multi-provider config..."
chmod +x ./clash
sudo pkill -f clash
./clash -f ./utils/speedtest/clash_config_eu.yml &
sleep 5

echo "Running LiteSpeedTest..."
chmod +x ./lite-linux-amd64
sudo nohup proxychains ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_yaml.yml > speedtest.log 2>&1 &