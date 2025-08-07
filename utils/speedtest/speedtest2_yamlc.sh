# Clean up any previous binaries
rm -f mihomo.gz clash lite-linux-amd64.gz lite-linux-amd64

echo "Downloading SingTools binary..."
wget -O singtools_linux32.tar.gz https://github.com/Kdwkakcs/singtools/releases/download/vv0.2.0/singtools_linux32.tar.gz

echo "Extracting SingTools..."
tar -zxvf singtools_linux32.tar.gz
chmod +x ./singtools

echo "Running SingTools speed test..."
# The -i flag specifies the input file with the proxy nodes.
# sub_merge_yaml.yml is the file containing the collected proxies in a format SingTools can likely parse.
# The default output is out.json, which is what the subsequent output.py script expects.
./singtools test -i ./sub/sub_merge_yaml.yml -c ./utils/speedtest/singtools_config.json 2>&1 | tee speedtest.log