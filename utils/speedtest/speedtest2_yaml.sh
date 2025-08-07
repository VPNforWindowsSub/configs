echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

echo "Running LiteSpeedTest with local config and local proxy list..."
chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./utils/speedtest/lite_config_yaml.json --test ./sub/sub_merge_yaml.yml > speedtest.log 2>&1 &
