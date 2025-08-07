echo "Downloading Mihomo v1.19.12 binary..."
wget -O mihomo.gz https://github.com/MetaCubeX/mihomo/releases/download/v1.19.12/mihomo-linux-amd64-v1.19.12.gz
gunzip -c mihomo.gz > clash

echo "Starting Mihomo with the dedicated test configuration..."
chmod +x ./clash
sudo pkill -f clash
./clash -f ./utils/speedtest/clash_test_config.yml &
sleep 10

echo "Running API-based speed test using Python script..."
python3 ./utils/speedtest/api_speedtest.py 2>&1 | tee speedtest.log