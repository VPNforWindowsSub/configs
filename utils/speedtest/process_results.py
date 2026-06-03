import json
import base64
import geoip2.database
import os
import socket
import re

# --- Configuration ---
META_FILE = 'meta.json'
GEOIP_DB = 'utils/GeoLite2-Country.mmdb'
BLOCKED_COUNTRIES = ['IR', 'IL', 'BH']

# Output files
FULL_OUTPUT_FILE = 'full.txt'
FULL_OUTPUT_BASE64_FILE = 'full_base64.txt'
ETERNITY_OUTPUT_FILE = 'Eternity.txt'
ETERNITY_OUTPUT_BASE64_FILE = 'Eternity'
ETERNITY_BASE_FILE = 'EternityBase'
LOG_INFO_FILE = 'LogInfo.txt'

# Additional Outputs (re-added based on edge cases)
SPLITTED_OUTPUT_DIR = "./sub/splitted/"
SUB_ALL_FILE = "./sub/sub_merge.txt"
SUB_ALL_BASE64_FILE = "./sub/sub_merge_base64.txt"

# --- Parameters ---
ETERNITY_LIST_SIZE = 165
TOP_POOL_SIZE = 1000
NODES_PER_COUNTRY = 1
COUNTRY_NODE_LIMITS = {
    'TR': 4,
    'CN': 2
}

def is_ip_address(address):
    if not isinstance(address, str):
        return False
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address))

def get_ip_from_node(node):
    server_address = node.get('server', '')
    if not server_address:
        return ''
    if is_ip_address(server_address):
        return server_address
    try:
        return socket.gethostbyname(server_address)
    except socket.gaierror:
        return ''

def ensure_empty_files():
    """Create empty files if everything fails to prevent workflow breakdown."""
    files_to_touch = [
        FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE,
        ETERNITY_OUTPUT_BASE64_FILE, ETERNITY_BASE_FILE, LOG_INFO_FILE,
        SUB_ALL_FILE, SUB_ALL_BASE64_FILE
    ]
    for f in files_to_touch:
        open(f, 'w').close()
    
    os.makedirs(SPLITTED_OUTPUT_DIR, exist_ok=True)
    for p in ['vmess.txt', 'vless.txt', 'trojan.txt', 'ss.txt']:
        open(os.path.join(SPLITTED_OUTPUT_DIR, p), 'w').close()

def process_and_save_results():
    try:
        with open(META_FILE, 'r', encoding='utf-8') as f:
            nodes = json.load(f)
        print(f"Successfully read {len(nodes)} nodes from {META_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Could not read or parse {META_FILE}. Details: {e}")
        ensure_empty_files()
        return

    # Filter and score
    for node in nodes:
        speed = node.get('avg_speed', 0)
        delay = node.get('delay', 9999)
        speed_mb = speed / 1_000_000

        if delay > 0 and delay < 5000:
            latency_score = max(0, 100 - (delay / 10))
        else:
            latency_score = 0

        node['health_score'] = (speed_mb * 7) + (latency_score * 0.3)

    working_nodes = [node for node in nodes if node.get('health_score', 0) > 0]
    if not working_nodes:
        print("No working nodes found with health_score > 0. Output files will be empty.")
        ensure_empty_files()
        return
    
    print(f"Found {len(working_nodes)} working nodes.")
    working_nodes.sort(key=lambda x: x.get('health_score', 0), reverse=True)

    processed_nodes = []
    if os.path.exists(GEOIP_DB):
        with geoip2.database.Reader(GEOIP_DB) as reader:
            for node in working_nodes:
                ip_address = get_ip_from_node(node)
                country_code = 'XX'
                if ip_address:
                    try:
                        country_iso_code = reader.country(ip_address).country.iso_code
                        if country_iso_code:
                            country_code = country_iso_code
                    except (geoip2.errors.AddressNotFoundError, ValueError):
                        pass

                link = node.get('link')
                if link:
                    processed_nodes.append({
                        'link': link, 'ip': ip_address,
                        'tag': node.get('tag', 'N/A'),
                        'speed': node.get('avg_speed', 0),
                        'delay': node.get('delay', 9999),
                        'health_score': node.get('health_score', 0),
                        'country': country_code
                    })
    else:
        print("Warning: GeoIP DB not found. Skipping country lookup and filtering.")
        for node in working_nodes:
            link = node.get('link')
            if link:
                processed_nodes.append({
                    'link': link, 'ip': '', 'tag': node.get('tag', 'N/A'),
                    'speed': node.get('avg_speed', 0),
                    'delay': node.get('delay', 9999),
                    'health_score': node.get('health_score', 0),
                    'country': 'XX'
                })

    initial_count = len(processed_nodes)
    processed_nodes = [node for node in processed_nodes if node.get('country') not in BLOCKED_COUNTRIES]
    removed_count = initial_count - len(processed_nodes)
    if removed_count > 0:
        print(f"Filtered out {removed_count} nodes from blocked countries ({', '.join(BLOCKED_COUNTRIES)}).")

    print("Deduplicating proxies by configuration...")
    def get_proxy_signature(link):
        if '#' in link:
            return link.split('#')[0]
        return link

    seen_signatures = {}
    for node in processed_nodes:
        signature = get_proxy_signature(node['link'])

        if signature not in seen_signatures:
            seen_signatures[signature] = node
        else:
            if node['health_score'] > seen_signatures[signature]['health_score']:
                seen_signatures[signature] = node

    dup_removed_count = len(processed_nodes) - len(seen_signatures)
    processed_nodes = list(seen_signatures.values())
    print(f"Removed {dup_removed_count} duplicate configurations, keeping highest health_score instances.")

    if not processed_nodes:
        print("No valid nodes left after filtering. Aborting.")
        ensure_empty_files()
        return

    # --- Write Output Files ---
    full_links = [p['link'] for p in processed_nodes]
    full_links_str = '\n'.join(full_links)
    
    with open(FULL_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    with open(FULL_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(full_links_str.encode()).decode())
    with open(ETERNITY_BASE_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    
    # Restoring old sub_merge files behavior
    with open(SUB_ALL_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    with open(SUB_ALL_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(full_links_str.encode()).decode())

    # Restoring splitted files logic
    os.makedirs(SPLITTED_OUTPUT_DIR, exist_ok=True)
    vmess_outputs, vless_outputs, trojan_outputs, ss_outputs = [], [], [], []
    for link in full_links:
        if link.startswith("vmess://"): vmess_outputs.append(link)
        if link.startswith("vless://"): vless_outputs.append(link)
        if link.startswith("trojan://"): trojan_outputs.append(link)
        if link.startswith("ss://"): ss_outputs.append(link)

    with open(os.path.join(SPLITTED_OUTPUT_DIR, "vmess.txt"), 'w') as f: f.write("\n".join(vmess_outputs))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "vless.txt"), 'w') as f: f.write("\n".join(vless_outputs))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "trojan.txt"), 'w') as f: f.write("\n".join(trojan_outputs))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "ss.txt"), 'w') as f: f.write("\n".join(ss_outputs))
    
    print("✅ Saved full lists and splitted categories.")

    # Logging
    log_output_list = []
    for item in processed_nodes:
        speed_mb = item.get("speed", 0) / 1_048_576
        info = f"name: {item['tag']} | type: unknown | avg_speed: {speed_mb:.3f} MB | delay: {item['delay']} ms\n"
        log_output_list.append(info)
    with open(LOG_INFO_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log_output_list)
    print(f"✅ Saved Speedtest Logs to {LOG_INFO_FILE}.")

    # --- Geo-Balancing ---
    print("\n--- Starting Geo-Balancing for 'Eternity' list ---")
    source_pool = processed_nodes[:TOP_POOL_SIZE]

    nodes_by_country = {}
    for node in source_pool:
        country_code = node['country']
        if country_code not in nodes_by_country:
            nodes_by_country[country_code] = []
        nodes_by_country[country_code].append(node)

    eternity_nodes = []
    selected_links = set()
    for country in sorted(nodes_by_country.keys()):
        limit = COUNTRY_NODE_LIMITS.get(country, NODES_PER_COUNTRY)
        nodes_to_take = min(limit, len(nodes_by_country[country]))

        for i in range(nodes_to_take):
            node = nodes_by_country[country][i]
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])

    if len(eternity_nodes) < ETERNITY_LIST_SIZE:
        needed = ETERNITY_LIST_SIZE - len(eternity_nodes)
        for node in source_pool:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE: break
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])

    eternity_nodes.sort(key=lambda x: x['health_score'], reverse=True)

    eternity_links = [p['link'] for p in eternity_nodes]
    eternity_links_str = '\n'.join(eternity_links)
    with open(ETERNITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(eternity_links_str)
    with open(ETERNITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(eternity_links_str.encode()).decode())
    print(f"✅ Saved 'Eternity' list of {len(eternity_links)} proxies.")

if __name__ == '__main__':
    process_and_save_results()
