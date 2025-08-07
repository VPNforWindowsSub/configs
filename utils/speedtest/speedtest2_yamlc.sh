echo "Downloading Mihomo v1.19.12 binary..."
wget -O mihomo.gz https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz

gunzip -c mihomo.gz > clash

echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

echo "Setting up ProxyChains using local config file..."
sudo apt-get install proxychains -y
sudo mv -f ./utils/speedtest/proxychains.conf /etc/proxychains.conf

echo "Starting Mihomo with local multi-provider config..."
chmod +x ./clash
sudo pkill -f clash
./clash -f ./utils/speedtest/clash_config_eu.yml &
sleep 5

echo "Running LiteSpeedTest with local config and local proxy list..."
chmod +x ./lite-linux-amd64
sudo nohup proxychains ./lite-linux-amd64 --config ./utils/speedtest/lite_config_yaml.json --test ./sub/sub_merge_yaml.yml > speedtest.log 2>&1 &
