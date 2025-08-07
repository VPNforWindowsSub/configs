echo "Downloading Mihomo v1.19.12 binary..."
wget -O mihomo.gz https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz
gunzip -c mihomo.gz > clash

echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

echo "Starting Mihomo with local multi-provider config..."
chmod +x ./clash
sudo pkill -f clash
./clash -f ./utils/speedtest/clash_config_eu.yml &
sleep 5

echo "Running LiteSpeedTest via Mihomo API..."
chmod +x ./lite-linux-amd64
sudo ./lite-linux-amd64 --config ./utils/speedtest/lite_config_yaml.json --test subs 2>&1 | tee speedtest.log
