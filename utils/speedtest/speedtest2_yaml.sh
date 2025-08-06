# Download new Clash v1.18.0 from the backup repo with the correct tag
wget https://github.com/Kuingsmile/clash-core/releases/download/1.18/clash-linux-amd64-v1.18.0.gz

# Unzip it
gunzip clash-linux-amd64-v1.18.0.gz

# Rename the unzipped file to 'clash' for easy use
mv clash-linux-amd64-v1.18.0 clash

# Download the Lite Speed Tester
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# Download configs
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml

# Initialize Clash
chmod +x ./clash
./clash -f clash_config.yml &
sleep 5 # Wait for Clash to start

# Run LiteSpeedTest
chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_yaml.yml > speedtest.log 2>&1 &