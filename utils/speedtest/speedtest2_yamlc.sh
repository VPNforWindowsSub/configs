# --- SETUP ---

# Download the Lite Speed Tester
echo "Downloading LiteSpeedTest binary..."
wget -O lite-linux-amd64.gz https://github.com/xxf098/LiteSpeedTest/releases/download/v0.14.1/lite-linux-amd64-v0.14.1.gz
gzip -d lite-linux-amd64.gz

# --- EXECUTION ---

# Run the speed test tool directly.
# It will read its config, see there is no proxy gateway,
# and connect directly to the nodes in the --test file.
echo "Running LiteSpeedTest directly..."
chmod +x ./lite-linux-amd64
sudo ./lite-linux-amd64 --config ./utils/speedtest/lite_config_yaml.json --test ./sub/sub_merge_base64.txt 2>&1 | tee speedtest.log