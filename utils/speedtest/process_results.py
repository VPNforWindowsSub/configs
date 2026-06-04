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
DIVERSITY_OUTPUT_FILE = 'Diversity.txt'
DIVERSITY_OUTPUT_BASE64_FILE = 'Diversity'
RESILIENCE_OUTPUT_FILE = 'Resilience.txt'
RESILIENCE_OUTPUT_BASE64_FILE = 'Resilience_base64.txt'
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

# --- Domain Fronting Configuration ---
TRUSTED_DOMAINS = [
    "www.hcaptcha.com", "unpkg.com", "cdn.jsdelivr.net", "hcaptcha.com", "www.w3.org", "ietf.org",
    "www.icann.org", "registry.npmjs.org", "nodejs.org", "digitalocean.com", "www.digitalocean.com",
    "about.gitlab.com", "hub.docker.com", "api.openai.com", "chat.openai.com", "platform.openai.com",
    "postman.com", "www.postman.com", "www.udemy.com", "www.bitwarden.com", "udemy.com", "www.fiverr.com",
    "www.glassdoor.com", "www.upwork.com", "www.canva.com", "hubspot.com", "calendly.com", "medium.com",
    "www.medium.com", "patreon.com", "www.patreon.com", "genius.com", "www.okx.com", "coingecko.com",
    "kraken.com", "trustwallet.com", "metamask.io", "investing.com", "icook.hk"
]
CF_PORTS = [443, 2053, 2083, 2087, 2096, 8443]

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
    return ''

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
        
        if octets[0] == 104 and (16 <= octets[1] <= 31): return True
        if octets[0] == 172 and (64 <= octets[1] <= 71): return True
        if octets[0] == 162 and octets[1] == 159: return True
        if octets[0] == 188 and octets[1] == 114 and (96 <= octets[2] <= 111): return True
        if octets[0] == 108 and octets[1] == 162 and (192 <= octets[2] <= 255): return True
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
        ETERNITY_OUTPUT_BASE64_FILE, LOG_INFO_FILE,
        DIVERSITY_OUTPUT_FILE, DIVERSITY_OUTPUT_BASE64_FILE,
        RESILIENCE_OUTPUT_FILE, RESILIENCE_OUTPUT_BASE64_FILE
    ]
    for f in files_to_touch:
        open(f, 'w').close()
    
    os.makedirs(SPLITTED_OUTPUT_DIR, exist_ok=True)
    for p in ['vmess.txt', 'vless.txt', 'trojan.txt', 'ss.txt']:
        open(os.path.join(SPLITTED_OUTPUT_DIR, p), 'w').close()

def create_resilience_clone(node):
    """Deep parses CF nodes, injects Original Host/SNI, and swaps Address for a Trusted Domain."""
    link = node.get('link', '')
    ip = node.get('ip', '')
    
    if not is_cloudflare_ip(ip):
        return None

    trusted_domain = random.choice(TRUSTED_DOMAINS)
    
    if link.startswith('vless://') or link.startswith('trojan://'):
        try:
            scheme, rest = link.split('://', 1)
            user_server, query_name = rest.split('?', 1)
            user, server_port = user_server.split('@', 1)
            
            if ':' in server_port:
                server, port_str = server_port.split(':', 1)
                port = int(port_str)
            else:
                server = server_port
                port = 443
                
            if port not in CF_PORTS:
                return None
                
            if '#' in query_name:
                query, name = query_name.split('#', 1)
            else:
                query, name = query_name, "Proxy"
                
            params = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
            
            net = params.get('type', 'tcp')
            sec = params.get('security', 'none')
            
            if sec != 'tls': return None
            if net not in ['ws', 'grpc', 'httpupgrade']: return None
            
            if 'sni' not in params or not params['sni']:
                params['sni'] = server
            if net in ['ws', 'httpupgrade']:
                if 'host' not in params or not params['host']:
                    params['host'] = server
                    
            server = trusted_domain
            new_query = urllib.parse.urlencode(params)
            
            # Fix: Use raw unquoted UTF-8 string so clients read the emojis correctly
            new_name = urllib.parse.unquote(name) + " [🇮🇷]"
            
            clone = node.copy()
            clone['link'] = f"{scheme}://{user}@{server}:{port}?{new_query}#{new_name}"
            clone['tag'] = new_name
            return clone
        except Exception:
            return None
            
    elif link.startswith('vmess://'):
        try:
            b64 = link[8:].split('#')[0]
            b64 += '=' * (-len(b64) % 4)
            b64 = b64.replace('-', '+').replace('_', '/')
            j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
            
            port = int(j.get('port', 443))
            if port not in CF_PORTS: return None
                
            net = str(j.get('net', 'tcp'))
            tls = str(j.get('tls', 'none'))
            
            if tls != 'tls': return None
            if net not in ['ws', 'grpc', 'httpupgrade']: return None
                
            original_add = str(j.get('add', ''))
            if 'sni' not in j or not j['sni']:
                j['sni'] = original_add
            if net in ['ws', 'httpupgrade']:
                if 'host' not in j or not j['host']:
                    j['host'] = original_add
                    
            j['add'] = trusted_domain
            j['ps'] = str(j.get('ps', 'Proxy')) + " [🇮🇷]"
            
            # Fix: ensure_ascii=False prevents emojis from turning into \uXXXX
            new_b64 = base64.b64encode(json.dumps(j, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).decode('ascii')
            
            clone = node.copy()
            clone['link'] = f"vmess://{new_b64}"
            clone['tag'] = j['ps']
            return clone
        except Exception:
            return None
            
    return None

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

                # --- DYNAMIC GEOGRAPHIC RUNNER BIAS COMPENSATION ---
                sim_delay = node.get('delay', 9999)
                sim_speed = node.get('avg_speed', 0)
                
                # Apply penalty ONLY to US/CA nodes tested natively from US GitHub runners
                if country_code in ['US', 'CA']:
                    # Sliding scale penalty: Pushes unnaturally low pings (<120ms) closer to 100ms+
                    # 10ms -> ~98ms | 40ms -> ~104ms | 61ms -> ~108ms | 100ms -> ~116ms | 120ms -> 120ms
                    if sim_delay < 120:
                        sim_delay = sim_delay + ((120 - sim_delay) * 0.8)
                    
                    # Apply a minor 10% speed reduction to account for physical ocean cable distance
                    sim_speed = int(sim_speed * 0.9)
                
                # Recalculate health score using the newly balanced, globally accurate metrics
                speed_mb = sim_speed / 1_000_000
                latency_score = max(0, 100 - (sim_delay / 10)) if 0 < sim_delay < 5000 else 0
                new_health = (speed_mb * 7) + (latency_score * 0.3)

                link = node.get('link')
                if link:
                    raw_processed.append({
                        'link': link, 'ip': ip_address,
                        'tag': node.get('tag', 'N/A'),
                        'speed': sim_speed,
                        'delay': int(sim_delay),
                        'health_score': new_health,
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

    # 4. Apply beautiful sequential naming directly to link URI
    all_processed_nodes = []
    random_numbers = [random.randint(100, 999) for _ in range(len(unique_nodes))]

    for index, node in enumerate(unique_nodes):
        country_code = node['country']
        country_name = node['country_name']
        
        name_emoji = EMOJI.get(country_code, EMOJI['NOWHERE'])
        country_name_to_use = COUNTRY_NAME_MAPPING.get(country_name, country_name)
        country_name_formatted = country_name_to_use.replace(' ', '-')

        pretty_name = f'{name_emoji} {country_name_formatted}-{random_numbers[index]}'
        quoted_pretty_name = urllib.parse.quote(pretty_name)

        link = node['link']
        if link.startswith("vmess://"):
            try:
                b64 = link.replace("vmess://", "").split('#')[0]
                b64 += '=' * (-len(b64) % 4)
                b64 = b64.replace('-', '+').replace('_', '/')
                j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
                
                j['ps'] = pretty_name 
                
                new_b64 = base64.b64encode(json.dumps(j, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).decode('ascii')
                node['link'] = f"vmess://{new_b64}"
            except Exception:
                base_link = link.split('#')[0]
                node['link'] = f"{base_link}#{quoted_pretty_name}"
        else:
            base_link = link.split('#')[0]
            node['link'] = f"{base_link}#{quoted_pretty_name}"

        node['tag'] = pretty_name
        all_processed_nodes.append(node)

    # ==========================================
    # --- WRITE RESILIENCE (IRAN DOMAIN FRONT) -
    # ==========================================
    print("\n--- Generating Domain-Fronted Resilience List (Max Cloudflare Candidates) ---")
    resilience_candidates = [p for p in all_processed_nodes if p['country'] not in BLOCKED_COUNTRIES]
    
    resilience_nodes = []
    for node in resilience_candidates:
        cloned_node = create_resilience_clone(node)
        if cloned_node:
            resilience_nodes.append(cloned_node)

    # --- IRAN PRIORITIZATION LOGIC ---
    def calculate_iran_score(node):
        score = node.get('health_score', 0)
        link = node.get('link', '')
        sni, port, path = "", 443, ""
        
        try:
            if link.startswith('vless://') or link.startswith('trojan://'):
                parsed = urllib.parse.urlparse(link)
                port = parsed.port if parsed.port else 443
                query = dict(urllib.parse.parse_qsl(parsed.query))
                sni = query.get('sni', '').lower()
                path = query.get('path', '').lower()
            elif link.startswith('vmess://'):
                b64 = link.split('://')[1].split('#')[0]
                b64 += '=' * (-len(b64) % 4)
                j = json.loads(base64.b64decode(b64.replace('-', '+').replace('_', '/')).decode('utf-8', errors='ignore'))
                port = int(j.get('port', 443))
                sni = str(j.get('sni', '')).lower()
                path = str(j.get('path', '')).lower()
        except:
            pass
            
        # 1. Penalize default subdomains, abused free TLDs, and known burned proxy farms
        burned_signatures = [
            'workers.dev', 'trycloudflare.com', 'pages.dev', 'eu.org', '.cc', 
            'multiplydose', 'calmloud', 'ignitelimit', 'gossipglove', 'calmlunch', 'creationlong'
        ]
        if any(b in sni for b in burned_signatures) or '/assignment' in path:
            score -= 2000
            
        # 2. Huge boost for non-443 ports (GFW heavily throttles/DPIs 443)
        if port != 443 and port in CF_PORTS:
            score += 1000
            
        # 3. Boost for Iranian custom domains (.ir) used as SNIs
        if '.ir' in sni or sni.endswith('.ir.'):
            score += 500
            
        return score

    # Sort nodes by the custom Iran score
    resilience_nodes.sort(key=calculate_iran_score, reverse=True)
    
    # Cap the list at exactly 1000 configs
    resilience_nodes = resilience_nodes[:1000]

    res_links = [p['link'] for p in resilience_nodes]
    random.shuffle(res_links) # Scramble so the app doesn't bunch all the 8443 ports together
    res_links_str = '\n'.join(res_links)

    with open(RESILIENCE_OUTPUT_FILE, 'w', encoding='utf-8') as f: 
        f.write(res_links_str)
    with open(RESILIENCE_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: 
        f.write(base64.b64encode(res_links_str.encode()).decode())
    print(f"✅ Saved 'Resilience' list of {len(res_links)} domain-fronted Cloudflare proxies.\n")

    # --- 3.5 UUID Anti-Spam Filtering (STANDARD LISTS) ---
    print(f"Filtering out UUID spam (Max {MAX_SAME_UUID} instances per UUID) for standard lists...")
    uuid_counts = {}
    filtered_unique_nodes = []
    for node in all_processed_nodes:
        uuid = get_uuid(node['link'])
        if not uuid:
            filtered_unique_nodes.append(node)
            continue
            
        if uuid_counts.get(uuid, 0) < MAX_SAME_UUID:
            filtered_unique_nodes.append(node)
            uuid_counts[uuid] = uuid_counts.get(uuid, 0) + 1

    spam_removed = len(all_processed_nodes) - len(filtered_unique_nodes)
    unique_nodes = filtered_unique_nodes
    total_proxies = len(unique_nodes)
    print(f"UUID filtering complete. Removed {spam_removed} cloned nodes. Remaining unique nodes: {total_proxies}")

    # ==========================================
    # --- WRITE EXCLUSIVE COUNTRY DIVERSITY FILE ---
    # ==========================================
    print("\n--- Starting Diversity-First list generation ---")
    diversity_nodes_by_country = {}
    for node in unique_nodes:
        country = node['country']
        # Do not include any obscure/unknown/relay countries (no RELAY or unmappable XX)
        if country in ['RELAY', 'XX']:
            continue
            
        # Target constraints: ping < 2000ms AND speed >= 50kb/s (50000 B/s)
        # Note: This list completely ignores the BLOCKED_COUNTRIES filter!
        if node['delay'] < 2000 and node['speed'] >= 50000:
            if country not in diversity_nodes_by_country:
                diversity_nodes_by_country[country] = []
            diversity_nodes_by_country[country].append(node)

    diversity_nodes = []
    for country, country_nodes in diversity_nodes_by_country.items():
        # Sort each country's pool by health score (speed) first
        country_nodes.sort(key=lambda x: x['health_score'], reverse=True)
        # Pick exactly 2 working configs from each country
        diversity_nodes.extend(country_nodes[:2])

    diversity_links = [p['link'] for p in diversity_nodes]
    random.shuffle(diversity_links) # Completely scrambled
    diversity_links_str = '\n'.join(diversity_links)

    with open(DIVERSITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: 
        f.write(diversity_links_str)
    with open(DIVERSITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: 
        f.write(base64.b64encode(diversity_links_str.encode()).decode())
    print(f"✅ Saved 'Diversity' list of {len(diversity_links)} proxies.")

    # ==========================================
    # --- WRITE CONVENTIONAL OUTPUT FILES ---
    # ==========================================
    # Note: These conventional files MUST still strictly filter out BLOCKED_COUNTRIES
    conventional_nodes = [p for p in unique_nodes if p['country'] not in BLOCKED_COUNTRIES]

    full_links = [p['link'] for p in conventional_nodes]
    random.shuffle(full_links) # Completely scramble full list
    full_links_str = '\n'.join(full_links)

    with open(FULL_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(full_links_str)
    print(f"✅ Saved full list of {len(full_links)} proxies to {FULL_OUTPUT_FILE}.")

    with open(FULL_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode(full_links_str.encode()).decode())
    print(f"✅ Saved Base64 encoded full list to {FULL_OUTPUT_BASE64_FILE}.")

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

    # Write log file (matching conventional nodes)
    log_output_list = []
    for item in conventional_nodes:
        speed_mb = item.get("speed", 0) / 1_048_576
        info = f"name: {item['tag']} | type: unknown | avg_speed: {speed_mb:.3f} MB | delay: {item['delay']} ms\n"
        log_output_list.append(info)
    with open(LOG_INFO_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log_output_list)
    print(f"✅ Saved Speedtest Logs to {LOG_INFO_FILE}.")

    # --- Geo-Balancing & Protocol Prioritization for Eternity ---
    print("\n--- Starting Geo-Balancing and VLESS Quota for 'Eternity' list ---")
    source_pool = conventional_nodes[:TOP_POOL_SIZE]
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
        for node in conventional_nodes:
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
        for node in conventional_nodes:
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
