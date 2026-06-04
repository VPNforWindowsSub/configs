import json
import base64
import geoip2.database
import os
import socket
import re
import math
import urllib.parse
import concurrent.futures
import random

# --- Configuration ---
META_FILE = 'meta.json'
GEOIP_DB = 'utils/GeoLite2-Country.mmdb'
BLOCKED_COUNTRIES = ['IR', 'IL', 'BH', 'RU']

# Output files
FULL_OUTPUT_FILE = 'full.txt'
FULL_OUTPUT_BASE64_FILE = 'full_base64.txt'
ETERNITY_OUTPUT_FILE = 'Eternity.txt'
ETERNITY_OUTPUT_BASE64_FILE = 'Eternity'
ETERNITY_BASE_FILE = 'EternityBase'
LOG_INFO_FILE = 'LogInfo.txt'

# Additional Outputs
SPLITTED_OUTPUT_DIR = "./sub/splitted/"

EMOJI = {
    'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬', 'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
    'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹', 'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
    'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪', 'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
    'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳', 'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
    'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾', 'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
    'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮', 'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
    'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻', 'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
    'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲', 'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
    'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸', 'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯',
    'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷', 'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪',
    'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮', 'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵',
    'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹', 'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰',
    'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹', 'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱',
    'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶', 'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪',
    'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪', 'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲',
    'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼', 'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧',
    'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷', 'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻',
    'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩', 'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭',
    'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳', 'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷',
    'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻', 'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿',
    'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫', 'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴',
    'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿', 'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫',
    'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱', 'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸',
    'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦', 'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺',
    'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨', 'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭',
    'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱', 'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷',
    'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽', 'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩',
    'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯', 'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳',
    'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻', 'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬',
    'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿', 'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
    'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫', 'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹',
    'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼', 'RELAY': '🏁', 'NOWHERE': '🇦🇶'
}

COUNTRY_NAME_MAPPING = {
    'United States': 'USA',
    'United Kingdom': 'UK',
    'Russian Federation': 'Russia',
    'The Netherlands': 'Netherlands',
    'Türkiye': 'Turkey',
    'United Arab Emirates': 'Emirates'
}

# --- Parameters ---
ETERNITY_LIST_SIZE = 165
VLESS_TARGET_PERCENT = 0.55
VLESS_TARGET_SIZE = math.ceil(ETERNITY_LIST_SIZE * VLESS_TARGET_PERCENT)
TOP_POOL_SIZE = 1000
NODES_PER_COUNTRY = 1
COUNTRY_NODE_LIMITS = {
    'TR': 4,
    'CN': 2
}

# Maximum allowed nodes that share the exact same UUID/Password.
MAX_SAME_UUID = 5 

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
    return '' # We will pre-resolve these concurrently instead

def get_proxy_signature(link):
    if '#' in link:
        return link.split('#')[0]
    return link

def is_cloudflare_ip(ip):
    """Checks if an IP falls into Cloudflare Anycast CDN ranges."""
    if not ip: return False
    try:
        octets = [int(o) for o in ip.split('.')]
        if len(octets) != 4: return False
        
        # 104.16.0.0/12 (104.16.0.0 - 104.31.255.255)
        if octets[0] == 104 and (16 <= octets[1] <= 31): return True
        # 172.64.0.0/13 (172.64.0.0 - 172.71.255.255)
        if octets[0] == 172 and (64 <= octets[1] <= 71): return True
        # 162.159.0.0/16
        if octets[0] == 162 and octets[1] == 159: return True
        # 188.114.96.0/20 (188.114.96.0 - 188.114.111.255)
        if octets[0] == 188 and octets[1] == 114 and (96 <= octets[2] <= 111): return True
        # 108.162.192.0/18
        if octets[0] == 108 and octets[1] == 162 and (192 <= octets[2] <= 255): return True
        # 198.41.128.0/17
        if octets[0] == 198 and octets[1] == 41 and (128 <= octets[2] <= 255): return True
    except:
        pass
    return False

def get_uuid(link):
    """Safely extracts the UUID or Password from a proxy link to track spam."""
    try:
        if link.startswith('vless://') or link.startswith('trojan://'):
            return link.split('://')[1].split('@')[0]
        elif link.startswith('vmess://'):
            b64 = link.split('://')[1].split('#')[0]
            b64 += '=' * (-len(b64) % 4)
            b64 = b64.replace('-', '+').replace('_', '/')
            j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
            return str(j.get('id', ''))
        elif link.startswith('ss://'):
            parsed = urllib.parse.urlparse(link)
            if parsed.username:
                up = urllib.parse.unquote(parsed.username)
                if ':' not in up:
                    up = base64.b64decode(up + '=' * (-len(up) % 4)).decode('utf-8', errors='ignore')
                return up.split(':', 1)[1]
            else:
                decoded = base64.b64decode(parsed.netloc + '=' * (-len(parsed.netloc) % 4)).decode('utf-8', errors='ignore')
                return decoded.split('@')[0].split(':', 1)[1]
    except:
        return None

def ensure_empty_files():
    files_to_touch = [
        FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE,
        ETERNITY_OUTPUT_BASE64_FILE, ETERNITY_BASE_FILE, LOG_INFO_FILE
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

    # --- NEW CONCURRENT DNS RESOLVER ---
    # We resolve all domains in parallel using 100 threads to bypass GitHub UDP limits.
    unique_servers = list(set([node.get('server', '') for node in working_nodes if node.get('server')]))
    resolved_ips = {}
    print(f"Resolving {len(unique_servers)} unique domains concurrently...", flush=True)

    def resolve_domain(server):
        if is_ip_address(server):
            return server, server
        try:
            return server, socket.gethostbyname(server)
        except:
            return server, ''

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(resolve_domain, unique_servers)
        for server, ip in results:
            resolved_ips[server] = ip
    print("Concurrent DNS Resolution complete.", flush=True)

    # 1. Resolve and tag working nodes using concurrent DNS results
    raw_processed = []
    if os.path.exists(GEOIP_DB):
        with geoip2.database.Reader(GEOIP_DB) as reader:
            for node in working_nodes:
                server = node.get('server', '')
                ip_address = resolved_ips.get(server, '')
                country_code = 'XX'
                country_name = 'Unknown'
                
                # Intercept Cloudflare Anycast IPs and force them to 'RELAY' directly
                if is_cloudflare_ip(ip_address):
                    country_code = 'RELAY'
                    country_name = 'Relay'
                elif ip_address:
                    try:
                        res_country = reader.country(ip_address)
                        country_code = res_country.country.iso_code or 'XX'
                        country_name = res_country.country.name or 'Unknown'
                    except:
                        pass

                if country_code in ['CLOUDFLARE', 'PRIVATE']:
                    country_code = 'RELAY'
                    country_name = 'Relay'

                # Graceful UI fallback: replace unmappable codes with 'RELAY'
                if country_code == 'XX':
                    country_code = 'RELAY'
                    country_name = 'Relay'

                link = node.get('link')
                if link:
                    raw_processed.append({
                        'link': link, 'ip': ip_address,
                        'tag': node.get('tag', 'N/A'),
                        'speed': node.get('avg_speed', 0),
                        'delay': node.get('delay', 9999),
                        'health_score': node.get('health_score', 0),
                        'country': country_code,
                        'country_name': country_name
                    })
    else:
        print("Warning: GeoIP DB not found. Skipping country lookup.")
        for node in working_nodes:
            link = node.get('link')
            if link:
                raw_processed.append({
                    'link': link, 'ip': '', 'tag': node.get('tag', 'N/A'),
                    'speed': node.get('avg_speed', 0),
                    'delay': node.get('delay', 9999),
                    'health_score': node.get('health_score', 0),
                    'country': 'RELAY',
                    'country_name': 'Relay'
                })

    # 2. Filter blocked countries
    raw_processed = [node for node in raw_processed if node.get('country') not in BLOCKED_COUNTRIES]

    # 3. Deduplicate
    print("Deduplicating proxies by configuration...")
    seen_signatures = {}
    for node in raw_processed:
        signature = get_proxy_signature(node['link'])

        if signature not in seen_signatures:
            seen_signatures[signature] = node
        else:
            if node['health_score'] > seen_signatures[signature]['health_score']:
                seen_signatures[signature] = node

    unique_nodes = list(seen_signatures.values())
    unique_nodes.sort(key=lambda x: x.get('health_score', 0), reverse=True)

    # --- 3.5 UUID Anti-Spam Filtering ---
    print(f"Filtering out UUID spam (Max {MAX_SAME_UUID} instances per UUID)...")
    uuid_counts = {}
    filtered_unique_nodes = []
    for node in unique_nodes:
        uuid = get_uuid(node['link'])
        if not uuid:
            filtered_unique_nodes.append(node)
            continue
            
        if uuid_counts.get(uuid, 0) < MAX_SAME_UUID:
            filtered_unique_nodes.append(node)
            uuid_counts[uuid] = uuid_counts.get(uuid, 0) + 1

    spam_removed = len(unique_nodes) - len(filtered_unique_nodes)
    unique_nodes = filtered_unique_nodes
    total_proxies = len(unique_nodes)
    print(f"UUID filtering complete. Removed {spam_removed} cloned nodes. Remaining unique nodes: {total_proxies}")

    # 4. Apply sequential naming directly to link URI (using randomized suffix indices)
    processed_nodes = []
    random_numbers = [random.randint(100, 999) for _ in range(total_proxies)]

    for index, node in enumerate(unique_nodes):
        country_code = node['country']
        country_name = node['country_name']
        
        name_emoji = EMOJI.get(country_code, EMOJI['NOWHERE'])
        country_name_to_use = COUNTRY_NAME_MAPPING.get(country_name, country_name)
        country_name_formatted = country_name_to_use.replace(' ', '-')

        pretty_name = f'{name_emoji} {country_name_formatted}-{random_numbers[index]}'

        link = node['link']
        if link.startswith("vmess://"):
            try:
                # VMess protocol does not natively support '#' fragments.
                # The name must be embedded directly inside the Base64 JSON payload's "ps" key.
                b64 = link.replace("vmess://", "").split('#')[0]
                b64 += '=' * (-len(b64) % 4)
                b64 = b64.replace('-', '+').replace('_', '/')
                j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
                
                j['ps'] = pretty_name # Inject the pretty name inside the payload
                
                new_b64 = base64.b64encode(json.dumps(j, separators=(',', ':')).encode('utf-8')).decode('ascii')
                node['link'] = f"vmess://{new_b64}"
            except Exception:
                base_link = link.split('#')[0]
                node['link'] = f"{base_link}#{pretty_name}"
        else:
            # VLESS, Trojan, and Shadowsocks natively support '#' fragments
            base_link = link.split('#')[0]
            node['link'] = f"{base_link}#{pretty_name}"

        node['tag'] = pretty_name
        processed_nodes.append(node)

    # 5. Write Output Files (Completely randomized to protect against speed-sorting fingerprinting)
    full_links = [p['link'] for p in processed_nodes]
    random.shuffle(full_links) # Completely scramble full list
    full_links_str = '\n'.join(full_links)

    with open(FULL_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    print(f"✅ Saved full list of {len(full_links)} proxies to {FULL_OUTPUT_FILE}.")

    with open(FULL_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(full_links_str.encode()).decode())
    print(f"✅ Saved Base64 encoded full list to {FULL_OUTPUT_BASE64_FILE}.")
    
    with open(ETERNITY_BASE_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    print(f"✅ Saved Eternity Base list to {ETERNITY_BASE_FILE}.")

    # --- Write Splitted Files ---
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
    print("✅ Saved splitted categories.")

    # Write log file
    log_output_list = []
    for item in processed_nodes:
        speed_mb = item.get("speed", 0) / 1_048_576
        info = f"name: {item['tag']} | type: unknown | avg_speed: {speed_mb:.3f} MB | delay: {item['delay']} ms\n"
        log_output_list.append(info)
    with open(LOG_INFO_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log_output_list)
    print(f"✅ Saved Speedtest Logs to {LOG_INFO_FILE}.")

    # --- Geo-Balancing & Protocol Prioritization for Eternity ---
    print("\n--- Starting Geo-Balancing and VLESS Quota for 'Eternity' list ---")
    source_pool = processed_nodes[:TOP_POOL_SIZE]
    print(f"Using a source pool of top {len(source_pool)} nodes for balancing.")

    # Sort each country's pool so that VLESS nodes are prioritized first, then speed.
    nodes_by_country = {}
    for node in source_pool:
        country_code = node['country']
        if country_code not in nodes_by_country:
            nodes_by_country[country_code] = []
        nodes_by_country[country_code].append(node)

    for country in nodes_by_country:
        nodes_by_country[country].sort(key=lambda x: (0 if x['link'].startswith('vless://') else 1, -x['health_score']))

    eternity_nodes = []
    selected_links = set()
    current_vless_count = 0

    print(f"Selecting nodes based on country-specific limits (VLESS prioritized)...")
    for country in sorted(nodes_by_country.keys()):
        limit = COUNTRY_NODE_LIMITS.get(country, NODES_PER_COUNTRY)
        nodes_to_take = min(limit, len(nodes_by_country[country]))

        for i in range(nodes_to_take):
            node = nodes_by_country[country][i]
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])
                if node['link'].startswith('vless://'):
                    current_vless_count += 1

    print(f"Selected {len(eternity_nodes)} nodes after geographic distribution. Current VLESS count: {current_vless_count}")

    # Pass 1: If VLESS count is under 55% quota (91 nodes), fill strictly with VLESS nodes first
    if current_vless_count < VLESS_TARGET_SIZE:
        print(f"Aggressively filling VLESS nodes up to quota of {VLESS_TARGET_SIZE}...")
        for node in processed_nodes:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE:
                break
            if current_vless_count >= VLESS_TARGET_SIZE:
                break
            if node['link'].startswith('vless://') and node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])
                current_vless_count += 1

    # Pass 2: Fill any remaining slots up to 165 total nodes with fastest overall nodes (any protocol)
    if len(eternity_nodes) < ETERNITY_LIST_SIZE:
        needed = ETERNITY_LIST_SIZE - len(eternity_nodes)
        print(f"Filling remaining {needed} slots with top-health nodes of any protocol...")
        for node in processed_nodes:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE:
                break
            if node['link'] not in selected_links:
                eternity_nodes.append(node)
                selected_links.add(node['link'])

    # Shuffling the final Eternity output lists completely before saving to avoid speed-based order signatures
    eternity_links = [p['link'] for p in eternity_nodes]
    random.shuffle(eternity_links) # Scramble Eternity list
    eternity_links_str = '\n'.join(eternity_links)

    with open(ETERNITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(eternity_links_str)
    with open(ETERNITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(eternity_links_str.encode()).decode())
    
    final_vless_count = sum(1 for n in eternity_nodes if n['link'].startswith('vless://'))
    print(f"✅ Saved 'Eternity' list of {len(eternity_links)} proxies (contains {final_vless_count} highly-resilient VLESS nodes).")

if __name__ == '__main__':
    process_and_save_results()
