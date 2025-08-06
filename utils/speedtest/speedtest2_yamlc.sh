# Download new Clash v1.18.0 from the backup repo
wget https://github.com/Kuingsmile/clash-core/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz

# Unzip it
gunzip clash-linux-amd64-v1.18.0.gz

# Rename the unzipped file to 'clash' for easy use
mv clash-linux-amd64-v1.18.0 clash

# Download the Lite Speed Tester
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# Download configs and proxychains setup
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml
wget -O proxychains.conf https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/proxychains.conf
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json

# Initialize Clash
chmod +x ./clash && ./clash &

# Install and configure proxychains
sudo apt-get install proxychains
sudo chmod 777 /etc/proxychains.conf
mv -f proxychains.conf /etc/proxychains.conf

# Start Clash
sudo pkill -f clash
./clash -f clash_config.yml &

# Run LiteSpeedTest through the proxy chain
sleep 5
chmod +x ./lite-linux-amd64
sudo nohup proxychains ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_yaml.yml > speedtest.log 2>&1 &
