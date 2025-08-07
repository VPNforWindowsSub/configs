# Clean up any previous binaries
rm -f mihomo.gz clash lite-linux-amd64.gz lite-linux-amd64 singtools_linux32.tar.gz singtools

echo "--- Network Connectivity Check ---"
echo "Checking connection to Ping URL..."
curl -v http://clients3.google.com/generate_204
echo "Checking connection to Download URL..."
# We use -o /dev/null to discard the download, we only care about the connection and headers
curl -v http://cachefly.cachefly.net/100mb.test -o /dev/null
echo "------------------------------------"

echo "Downloading SingTools binary..."
wget -O singtools_linux32.tar.gz https://github.com/Kdwkakcs/singtools/releases/download/vv0.2.0/singtools_linux32.tar.gz

echo "Extracting SingTools..."
tar -zxvf singtools_linux32.tar.gz
chmod +x ./singtools

echo "Running SingTools speed test with DEBUG logging..."
# Added '-e debug' to get detailed logs for each node test.
./singtools test -i ./sub/sub_merge_base64.txt -c ./utils/speedtest/singtools_config.json -m out.json -e debug 2>&1 | tee speedtest.log