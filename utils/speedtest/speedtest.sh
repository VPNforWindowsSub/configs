
echo "Downloading working Clash binary..."
wget https://github.com/Kuingsmile/clash-core/releases/download/1.18/clash-linux-amd64-v1.18.0.gz
gunzip clash-linux-amd64-v1.18.0.gz
mv clash-linux-amd64-v1.18.0 clash

echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz


echo "Setting up ProxyChains..."
sudo apt-get install proxychains -y

sudo mv -f ./utils/speedtest/proxychains.conf /etc/proxychains.conf

# --- EXECUTION ---

echo "Starting Clash with local multi-provider config..."
chmod +x ./clash
./clash -f ./utils/speedtest/clash_config.yml &
sleep 5

echo "Running LiteSpeedTest..."
chmod +x ./lite-linux-amd64

sudo nohup proxychains ./lite-linux-amd64 --config ./utils/speedtest/lite_config.json --test ./sub/sub_merge_base64.txt > speedtest.log 2>&1 &