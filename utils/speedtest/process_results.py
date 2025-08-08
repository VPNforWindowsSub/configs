import json
import base64
import urllib.parse
import geoip2.database
import os
import socket
import re

# --- Configuration ---
META_FILE = 'meta.json'
TAG_MAP_FILE = 'tag_map.json'
GEOIP_DB = 'utils/GeoLite2-Country.mmdb'
BLOCKED_COUNTRIES = ['IR', 'CN']

# Output files
FULL_OUTPUT_FILE = 'full.txt'
FULL_OUTPUT_BASE64_FILE = 'full_base64.txt'
ETERNITY_OUTPUT_FILE = 'Eternity.txt'
ETERNITY_OUTPUT_BASE64_FILE = 'Eternity'

# --- Parameters ---
ETERNITY_LIST_SIZE = 165
TOP_POOL_SIZE = 1000
# --- THIS IS THE FIX: Define default and country-specific limits ---
NODES_PER_COUNTRY = 1  # Default for all countries
COUNTRY_NODE_LIMITS = {
    'TR': 4  # Special limit for Turkey
}
# --- END OF FIX ---

def is_ip_address(address):
    """Checks if a string is a valid IPv4 address."""
    if not isinstance(address, str):
        return False
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address))

def reconstruct_link(node_config_str, tag_map):
    """
    Reconstructs the original proxy link from the sing-box config object string.
    """
    try:
        config = json.loads(node_config_str)
        proxy_type = config.get('type')
        
        safe_tag = config.get('tag', '')
        tag_to_use = tag_map.get(safe_tag, safe_tag)
        tag = urllib.parse.quote(tag_to_use)

        if proxy_type == 'vless':
            uuid = config.get('uuid')
            server = config.get('server')
            port = config.get('server_port')
            server_is_ip = is_ip_address(server)

            params = {'type': config.get('transport', {}).get('type', 'tcp')}
            if config.get('tls', {}).get('enabled'):
                params['security'] = 'tls'
                if not server_is_ip:
                    params['sni'] = config.get('tls', {}).get('server_name', server)
                else:
                    params['allowInsecure'] = '1'

            if params['type'] == 'ws':
                ws_opts = config.get('transport', {})
                params['path'] = urllib.parse.quote(ws_opts.get('path', '/'))
                if not server_is_ip:
                    params['host'] = ws_opts.get('headers', {}).get('Host', server)

            query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v})
            return f"vless://{uuid}@{server}:{port}?{query_string}#{tag}"

        elif proxy_type == 'vmess':
            vmess_details = {
                "v": "2", "ps": tag_to_use, "add": config.get('server'),
                "port": config.get('server_port'), "id": config.get('uuid'),
                "aid": config.get('alter_id', 0), "net": config.get('transport', {}).get('type', 'tcp'),
                "type": "none", "host": "", "path": "",
                "tls": "tls" if config.get('tls', {}).get('enabled') else ""
            }
            if vmess_details["tls"] == 'tls':
                 vmess_details["sni"] = config.get('tls', {}).get('server_name', config.get('server'))
            if vmess_details["net"] == 'ws':
                vmess_details["path"] = config.get('transport', {}).get('path', '/')
                vmess_details["host"] = config.get('transport', {}).get('headers', {}).get('Host', config.get('server'))
            
            vmess_details_clean = {k: v for k, v in vmess_details.items() if v}
            encoded_json = base64.b64encode(json.dumps(vmess_details_clean, separators=(',', ':')).encode()).decode().strip()
            return f"vmess://{encoded_json}"

        elif proxy_type == 'shadowsocks':
            method = config.get('method')
            password = config.get('password')
            server = config.get('server')
            port = config.get('server_port')
            encoded_part = base64.b64encode(f"{method}:{password}".encode()).decode().strip()
            return f"ss://{encoded_part}@{server}:{port}#{tag}"
        
        elif proxy_type == 'trojan':
            server = config.get('server')
            server_is_ip = is_ip_address(server)
            params = {}
            if config.get('tls', {}).get('enabled'):
                if not server_is_ip:
                    params['sni'] = config.get('tls', {}).get('server_name', server)
            query_string = urllib.parse.urlencode(params)
            return f"trojan://{config.get('password')}@{server}:{config.get('server_port')}?{query_string}#{tag}"

        return None
    except Exception:
        return None

def get_ip_from_node(node):
    """
    Extracts the server address from the node's config and resolves it to an IP.
    """
    try:
        config = json.loads(node.get('config', '{}'))
        server_address = config.get('server')
        if not server_address:
            return ''
        if is_ip_address(server_address):
            return server_address
        try:
            return socket.gethostbyname(server_address)
        except socket.gaierror:
            return ''
    except json.JSONDecodeError:
        return ''

def process_and_save_results():
    """
    Reads singtools metadata, filters, sorts by speed, performs geo-balancing,
    and writes the final lists to output files.
    """
    try:
        with open(META_FILE, 'r', encoding='utf-8') as f:
            nodes = json.load(f)
        print(f"Successfully read {len(nodes)} nodes from {META_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Could not read or parse {META_FILE}. Details: {e}")
        for f in [FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE, ETERNITY_OUTPUT_BASE64_FILE]: open(f, 'w').close()
        return

    try:
        with open(TAG_MAP_FILE, 'r', encoding='utf-8') as f:
            tag_map = json.load(f)
        print(f"Successfully loaded tag map from {TAG_MAP_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: Tag map file '{TAG_MAP_FILE}' not found. Final links may have generic names.")
        tag_map = {}

    working_nodes = [node for node in nodes if node.get('avg_speed', 0) > 0]
    if not working_nodes:
        print("No working nodes found with speed > 0. Output files will be empty.")
        for f in [FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE, ETERNITY_OUTPUT_BASE64_FILE]: open(f, 'w').close()
        return
    print(f"Found {len(working_nodes)} working nodes.")

    working_nodes.sort(key=lambda x: x.get('avg_speed', 0), reverse=True)

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
                
                link = reconstruct_link(node.get('config'), tag_map)
                if link:
                    processed_nodes.append({
                        'link': link, 'ip': ip_address,
                        'tag': tag_map.get(node.get('tag'), node.get('tag', 'N/A')),
                        'speed': node.get('avg_speed', 0), 'country': country_code
                    })
    else:
        print("Warning: GeoIP DB not found. Skipping country lookup and filtering.")
        for node in working_nodes:
            link = reconstruct_link(node.get('config'), tag_map)
            if link:
                processed_nodes.append({
                    'link': link, 'ip': '', 'tag': tag_map.get(node.get('tag'), node.get('tag', 'N/A')),
                    'speed': node.get('avg_speed', 0), 'country': 'XX'
                })

    initial_count = len(processed_nodes)
    processed_nodes = [node for node in processed_nodes if node.get('country') not in BLOCKED_COUNTRIES]
    removed_count = initial_count - len(processed_nodes)
    if removed_count > 0:
        print(f"Filtered out {removed_count} nodes from blocked countries ({', '.join(BLOCKED_COUNTRIES)}).")
    
    if not processed_nodes:
        print("No valid nodes left after filtering. Aborting.")
        for f in [FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE, ETERNITY_OUTPUT_BASE64_FILE]: open(f, 'w').close()
        return

    full_links = [p['link'] for p in processed_nodes]
    with open(FULL_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(full_links))
    print(f"✅ Saved full list of {len(full_links)} proxies to {FULL_OUTPUT_FILE}.")
    
    with open(FULL_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(full_links).encode()).decode())
    print(f"✅ Saved Base64 encoded full list to {FULL_OUTPUT_BASE64_FILE}.")

    print("\n--- Starting Geo-Balancing for 'Eternity' list ---")
    source_pool = processed_nodes[:TOP_POOL_SIZE]
    print(f"Using a source pool of top {len(source_pool)} nodes for balancing.")
    
    nodes_by_country = {}
    for node in source_pool:
        country_code = node['country']
        if country_code not in nodes_by_country:
            nodes_by_country[country_code] = []
        nodes_by_country[country_code].append(node)
    
    eternity_nodes = []
    selected_links = set()
    print(f"Selecting nodes based on country-specific limits...")
    for country in sorted(nodes_by_country.keys()):
        # --- THIS IS THE FIX: Use the specific limit for the current country, or the default ---
        limit = COUNTRY_NODE_LIMITS.get(country, NODES_PER_COUNTRY)
        nodes_to_take = min(limit, len(nodes_by_country[country]))
        # --- END OF FIX ---
        
        for i in range(nodes_to_take):
            node = nodes_by_country[country][i]
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])
    
    print(f"Selected {len(eternity_nodes)} nodes after geographic distribution.")
    if len(eternity_nodes) < ETERNITY_LIST_SIZE:
        needed = ETERNITY_LIST_SIZE - len(eternity_nodes)
        print(f"Filling remaining {needed} slots with top-speed nodes...")
        for node in source_pool:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE: break
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])

    eternity_nodes.sort(key=lambda x: x['speed'], reverse=True)

    eternity_links = [p['link'] for p in eternity_nodes]
    with open(ETERNITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(eternity_links))
    print(f"✅ Saved 'Eternity' list of {len(eternity_links)} proxies to {ETERNITY_OUTPUT_FILE}.")

    with open(ETERNITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(eternity_links).encode()).decode())
    print(f"✅ Saved Base64 encoded 'Eternity' list to {ETERNITY_OUTPUT_BASE64_FILE}.")

if __name__ == '__main__':
    process_and_save_results()
