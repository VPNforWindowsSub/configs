import requests
import json
import time
import concurrent.futures

# Mihomo API configuration
MIHOMO_API_URL = "http://127.0.0.1:9090"
# A standard, reliable file for speed testing
TEST_URL = "http://cachefly.cachefly.net/100mb.test"
# How many seconds to download for each test
TEST_DURATION = 8
# How many proxies to test concurrently
CONCURRENCY = 40

def get_proxies():
    """Fetches the list of all available proxies from the Mihomo API."""
    try:
        response = requests.get(f"{MIHOMO_API_URL}/proxies")
        response.raise_for_status()
        # We only care about the proxies under the 'local_proxies' provider
        return response.json()['proxies']['local_proxies']['all']
    except Exception as e:
        print(f"Error fetching proxies from Mihomo API: {e}")
        return []

def test_speed(proxy):
    """Tests a single proxy's download speed and latency."""
    proxy_name = proxy['name']
    print(f"Testing: {proxy_name}")

    # 1. Test Latency (delay)
    try:
        delay_response = requests.get(
            f"{MIHOMO_API_URL}/proxies/{proxy_name}/delay?timeout=5000&url=http://www.gstatic.com/generate_204"
        )
        delay_data = delay_response.json()
        latency = delay_data.get('delay', -1)
    except Exception:
        latency = -1

    if latency == -1:
        print(f"  -> Failed (Latency test failed)")
        return None

    # 2. Test Download Speed
    bytes_downloaded = 0
    max_speed = 0
    start_time = time.time()
    
    try:
        with requests.get(
            TEST_URL,
            proxies={"http": f"http://127.0.0.1:7890", "https": f"http://127.0.0.1:7890"},
            params={"proxy": proxy_name}, # Tell Mihomo to use this specific proxy
            stream=True,
            timeout=TEST_DURATION + 2, # Add a small buffer to the timeout
        ) as r:
            r.raise_for_status()
            chunk_start_time = time.time()
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                if time.time() - start_time > TEST_DURATION:
                    break
                bytes_downloaded += len(chunk)
                chunk_time = time.time() - chunk_start_time
                if chunk_time > 0:
                    current_speed = len(chunk) / chunk_time
                    if current_speed > max_speed:
                        max_speed = current_speed
                chunk_start_time = time.time()

    except requests.exceptions.RequestException as e:
        print(f"  -> Failed (Download error: {e})")
        return None

    end_time = time.time()
    duration = end_time - start_time
    avg_speed = bytes_downloaded / duration if duration > 0 else 0

    print(f"  -> Success! Ping: {latency}ms, Avg Speed: {avg_speed / 1024 / 1024:.2f} MB/s")

    # Mimic the output structure of LiteSpeedTest for compatibility with output.py
    return {
        "id": 0, # Placeholder ID
        "remarks": proxy_name,
        "protocol": proxy.get('type', 'unknown'),
        "ping": latency,
        "avg_speed": avg_speed,
        "max_speed": max_speed,
        "link": proxy.get('vless_link_placeholder', '') # This needs to be populated later
    }

def main():
    proxies = get_proxies()
    if not proxies:
        print("No proxies found to test.")
        return

    print(f"Found {len(proxies)} proxies. Starting speed test with concurrency {CONCURRENCY}...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        future_to_proxy = {executor.submit(test_speed, proxy): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                results.append(result)

    # The 'link' field is missing, so we need to add it back by matching names
    try:
        with open('./sub/sub_merge.txt', 'r', encoding='utf-8') as f:
            links = f.read().splitlines()
        
        link_map = {}
        for i, link in enumerate(links):
            # This is a simplified name extraction. It might need adjustment if names are complex.
            try:
                name = urllib.parse.unquote(link.split('#')[1])
                link_map[name] = link
            except:
                pass # Ignore links without a valid name fragment

        for res in results:
            # The API test renames proxies, so we need a robust way to match them back.
            # We'll match based on the core part of the name before the speed info is added.
            original_name = res['remarks'].split(' | ')[0].strip()
            if original_name in link_map:
                 res['link'] = link_map[original_name]

    except Exception as e:
        print(f"Warning: Could not map links back to results. 'link' field will be empty. Error: {e}")


    output_data = {"nodes": results}
    with open('out.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSpeed test complete. Results saved to out.json. Tested {len(results)} proxies successfully.")

if __name__ == "__main__":
    main()