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
echo "Setting up ProxyChains..."
sudo apt-get install proxychains -y
sudo mv -f ./utils/speedtest/proxychains.conf /etc/proxychains.conf

# --- EXECUTION ---
echo "Starting Mihomo with local multi-provider config..."
chmod +x ./clash
./clash -f ./utils/speedtest/clash_config.yml &
sleep 5

echo "Running LiteSpeedTest..."
chmod +x ./lite-linux-amd64
sudo nohup proxychains ./lite-linux-amd64 --config ./utils/speedtest/lite_config.json --test ./sub/sub_merge_base64.txt > speedtest.log 2>&1 &