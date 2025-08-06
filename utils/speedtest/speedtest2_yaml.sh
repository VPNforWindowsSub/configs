# In file: utils/speedtest/speedtest2_yaml.sh
# Replace the entire file content with this:

# Clash - This is the missing part
wget -O clash.gz https://github.com/Dreamacro/clash/releases/download/v1.11.8/clash-linux-amd64-v1.11.8.gz
gunzip clash.gz

# Lite Speed Tester
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# Configs
wget -O lite_config.json https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/lite_config_yaml.json
wget -O clash_config.yml https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/utils/speedtest/clash_config_eu.yml

#初始化 Clash
chmod +x ./clash
./clash -f clash_config.yml &
sleep 5 # Wait for Clash to start

#运行 LiteSpeedTest
chmod +x ./lite-linux-amd64
sudo nohup ./lite-linux-amd64 --config ./lite_config.json --test https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/sub_merge_yaml.yml > speedtest.log 2>&1 &