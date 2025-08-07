# Clean up any previous binaries
rm -f mihomo.gz clash lite-linux-amd64.gz lite-linux-amd64 singtools_linux32.tar.gz singtools

echo "Downloading SingTools binary..."
wget -O singtools_linux32.tar.gz https://github.com/Kdwkakcs/singtools/releases/download/vv0.2.0/singtools_linux32.tar.gz

echo "Extracting SingTools..."
tar -zxvf singtools_linux32.tar.gz
chmod +x ./singtools

echo "Running SingTools speed test..."
# We use sub_merge_base64.txt as input, which is a standard format.
# The -m flag saves the detailed metadata (including speeds) to out.json, which is what the next script needs.
./singtools test -i ./sub/sub_merge_base64.txt -c ./utils/speedtest/singtools_config.json -m out.json 2>&1 | tee speedtest.log