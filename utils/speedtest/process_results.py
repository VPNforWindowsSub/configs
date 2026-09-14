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
import shutil
import ipaddress
import html
import time
import datetime
from collections import Counter

# --- Configuration ---
ENABLE_LOCAL_IRAN_PROBE = True
META_FILE = 'meta.json'
GEOIP_DB = 'utils/GeoLite2-Country.mmdb'
BLOCKED_COUNTRIES = ['IR', 'IL', 'BH', 'RU', 'IQ']
LOGS_DIR = 'Logs/'

# Output files
FULL_OUTPUT_FILE = 'full.txt'
FULL_OUTPUT_BASE64_FILE = 'full_base64.txt'
ETERNITY_OUTPUT_FILE = 'Eternity.txt'
ETERNITY_OUTPUT_BASE64_FILE = 'Eternity'
DIVERSITY_OUTPUT_FILE = 'Diversity.txt'
DIVERSITY_OUTPUT_BASE64_FILE = 'Diversity'
RESILIENCE_OUTPUT_FILE = 'Resilience.txt'
RESILIENCE_OUTPUT_BASE64_FILE = 'Resilience'
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

def get_sync_branch_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "IranProbeCoordinator"
    }

def get_file_from_branch(repo, branch, file_path, token):
    try:
        import requests
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
        resp = requests.get(url, headers=get_sync_branch_headers(token), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            sha = data.get('sha')
            content = data.get('content')
            if content:
                raw_text = base64.b64decode(content).decode('utf-8')
            else:
                raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
                raw_resp = requests.get(raw_url, headers=get_sync_branch_headers(token), timeout=15)
                raw_text = raw_resp.text
            return json.loads(raw_text), sha
    except Exception:
        pass
    return None, None

def put_file_to_branch(repo, branch, file_path, content_dict, token, sha=None):
    try:
        import requests
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        raw_bytes = json.dumps(content_dict, indent=2).encode('utf-8')
        payload = {
            "message": f"Sync probe: {content_dict.get('status', 'update')}",
            "content": base64.b64encode(raw_bytes).decode('ascii'),
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
        resp = requests.put(url, headers=get_sync_branch_headers(token), json=payload, timeout=15)
        return resp.status_code in [200, 201]
    except Exception:
        return False

def ensure_sync_branch(repo, branch, token):
    try:
        import requests
        headers = get_sync_branch_headers(token)
        ref_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{branch}"
        r = requests.get(ref_url, headers=headers, timeout=10)
        if r.status_code == 200:
            return True
        for candidate_branch in [os.environ.get("GITHUB_REF_NAME", "master"), "master", "main"]:
            branch_url = f"https://api.github.com/repos/{repo}/git/ref/heads/{candidate_branch}"
            mr = requests.get(branch_url, headers=headers, timeout=10)
            if mr.status_code == 200:
                sha = mr.json()['object']['sha']
                create_url = f"https://api.github.com/repos/{repo}/git/refs"
                cr = requests.post(create_url, headers=headers, json={"ref": f"refs/heads/{branch}", "sha": sha}, timeout=10)
                return cr.status_code == 201
    except Exception:
        pass
    return False

def coordinate_iran_probe(candidate_links):
    if not ENABLE_LOCAL_IRAN_PROBE:
        print("Local Iran probe is disabled via configuration toggle. Skipping.")
        return []
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo or not candidate_links:
        return []

    branch = "probe-sync"
    if not ensure_sync_branch(repo, branch, token):
        return []

    run_id = f"job-{int(time.time())}"
    job_payload = {
        "run_id": run_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "pending",
        "candidates": candidate_links[:3000]
    }

    current_data, current_sha = get_file_from_branch(repo, branch, "probe_job.json", token)
    if not put_file_to_branch(repo, branch, "probe_job.json", job_payload, token, current_sha):
        return []

    print(f"Dispatched {len(job_payload['candidates'])} candidates to local Iran probe. Waiting for client response...")
    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(10)
        data, _ = get_file_from_branch(repo, branch, "probe_job.json", token)
        if not data or data.get("run_id") != run_id:
            continue
        status = data.get("status")
        if status == "skipped":
            print("Local probe explicitly skipped this run.")
            return []
        elif status == "completed":
            verified = data.get("verified", [])
            print(f"Local probe completed successfully. Received {len(verified)} verified nodes from Iran.")
            return verified
        elif status == "testing":
            pass

    print("Local probe timed out after 10 minutes. Proceeding with cloud fallbacks.")
    return []

RESILIENCE_THEMES=["🌐 Grid","🏹 Barton","👻 Roach","🌙 Twilight","⚡ Zenitsu","🕸️ Shadow","🦅 Raptor","🏔️ Ridge","🔥 Inferno","🦁 CapeTown","⚔️ Zoro","🌙 Lunar","✈️ Spitfire","🗡️ Dagger","👻 Rayman","📡 Bandwidth","📡 Antenna","🌿 Amazon","🦊 MetaMask","⚖️ Gravity","🦇 Gotham","🗡️ Cloud","🧙 Dumbledore","👽 Stitch","🌲 Taiga","🏹 Hanzo","🕸️ Node","🌟 Zenith","🎤 Billie","☯️ Yin","🔫 Jules","🚀 Normandy","🕶️ JayZ","🐰 Bunny","🚢 Nelson","🌫️ Vapor","🦍 Gorilla","🖼️ NFT","⛏️ Steve","🏖️ Miami","📞 Tardis","🦾 Cyborg","🎩 Lincoln","☄️ Comet","🚘 CJ","🔪 Ripper","🦂 Scorpion","🏌️ Woods","👺 Ronin","🔥 Scorpion","🏇 Attila","🏝️ Bali","🔭 Optics","🥊 Ryu","🦖 Godzilla","🐰 Bugs","🕵️‍♀️ Kim","🧬 Helix","😈 Daemon","⚡ Kinetic","👾 Virus","🎤 Abel","🙏 Cleric","🌋 Tremor","📡 Beacon","☀️ Summer","🧩 Enigma","🌿 Jade","🌑 Blackhole","🚪 Gateway","📡 Proxy","🍔 Burger","☄️ Flare","🤠 Morgan","🛡️ Chief","🔶 Amber","⚖️ Anubis","🔭 Galileo","🧊 Sid","🌘 Eclipse","🏀 Bird","🏁 McLaren","🌌 Jupiter","🦅 Phoenix","🦾 Stark","🌌 Gurren","❄️ Frost","🚬 Noir","⚙️ Inertia","🔫 Flintlock","⚪ Silver","📡 Sonar","🚀 Soyuz","🧥 Armani","🛡️ Bastion","🤖 Daft","💥 Fission","🌑 MoonKnight","🔮 Oracle","🍸 Bond","🕷️ Parker","🌠 Asteroid","🍸 Martini","⚡ Fiber","🦅 Scout","🌑 Raven","🤖 C3PO","🧪 Chemistry","🐂 Minotaur","🌬️ Chicago","🚀 Saturn","🎹 Moog","♌ Leo","🌌 Fractal","🦾 MegaMan","🧘 Zen","🏹 Quiver","🏰 Gondor","🐈 Catwoman","🛡️ Rogers","💍 Crystal","🚬 Spike","🦄 Unicorn","🕌 Dubai","📓 Light","🤖 Gundam","🦅 Hawk","🍷 Speakeasy","🧵 Dior","🏛️ Aurelius","🐶 Inuyasha","🧬 Augment","🦍 Tarzan","🧚‍♀️ Tinkerbell","🦍 Beast","🌌 Mercury","🦅 Horus","🥞 Pancake","♔ King","❄️ Isotope","🏎️ Ferrari","🦍 Caesar","🦏 Rhinoceros","🤖 Shinji","🦅 Griffin","🍄 Mario","👑 Peach","💣 Claymore","🌳 Druid","✈️ Boeing","🎹 Chopin","🐉 Spyro","🐺 Geralt","✨ Aura","🍣 Sushi","🌐 Polygon","♍ Virgo","🎯 Darts","🦁 Simba","🕶️ Cypher","🌉 SF","🥊 Ken","🎸 Punk","🕵️ Stealth","🏎️ M3","🦅 Skyline","🌿 Solstice","🔴 Asuka","👦 Ben10","🎸 Zeppelin","💦 Aqua","⚔️ Jedi","🌅 Dawn","📉 Bear","⛵ Columbus","🦾 Genji","⚔️ Halberd","🚀 Moon","⚾ Ruth","🦒 Giraffe","♖ Rook","🍎 Newton","🦦 Otter","🌊 Hydro","🌌 Tatooine","🏎️ Veyron","💎 Onyx","🎀 Swift","✨ Topaz","🔨 Warhammer","🦖 Jurassic","🐷 Porky","💻 Matrix","🏎️ Leclerc","🕵️ Poirot","⚙️ Macro","🤖 AI","🌠 Orion","⚪ Pearl","🏀 Shaq","🔴 Garnet","👁️ Cyclops","✨ Quasar","🏀 Magic","🦁 Lion","🦁 Lannister","⛄ Snow","🌕 Moon","🎧 Skrillex","🥊 Drago","🔗 Ledger","💣 C4","🐉 Shenron","🎤 Mercury","📡 Radar","💻 Windows","🦇 Alucard","🏈 Manning","🌑 Pulsar","⚔️ Sora","🚗 Tesla","⚡ Speedster","🏐 Shoyo","🏛️ Sparta","🔥 Hades","🎸 Jagger","🕯️ Ritual","🛡️ Vanguard","🐼 Po","📏 Zenith","🛡️ Wakanda","⚡ Bolt","🍹 Mojito","💼 Vuitton","🍂 Autumn","🦇 Batgirl","🤖 Bender","⚡ ACDC","🌀 Karma","🦅 Hawkeye","⚔️ Maximus","🛡️ Leonidas","🐍 Kobe","⚔️ Sephiroth","🥊 Ali","🚙 Wrangler","💣 Grenade","🎸 Slash","✍️ Plato","📜 Aristotle","♏ Scorpio","🔥 Wildfire","🧽 Sponge","♑ Capricorn","🔗 Mesh","🐉 Targaryen","☁️ Cloud","🌀 Flux","🍀 Luck","🦇 Belmont","🎩 Gatsby","⚡ Static","🐍 Shelby","⚡ Sith","🐎 Knight","🕶️ Gojo","🐪 Camel","🗡️ Sasuke","🎯 Ballistic","❄️ Tundra","🧿 Ward","🔢 Algebra","🌟 Bowie","⚔️ Kenshin","🌌 Cosmos","🦅 Napoleon","✍️ Socrates","⚽ Henry","🖥️ Mainframe","🎱 Billiards","🍕 Milan","♈ Aries","🗽 NY","🌭 Dog","🦇 Nightwing","📜 Washington","🏹 Crossbow","🦅 Alexander","🌳 Jungle","🏀 Curry","🌟 Madonna","🐿️ Squirrel","🔱 Curry","🐺 Direwolf","👑 Drake","🛡️ Troy","🔥 Loki","👁️ Vision","🏝️ Island","🔌 Jack","🌌 Void","🏈 Brady","🔬 Mutation","💣 Torpedo","🌀 Cyclone","🚀 Shepard","♗ Bishop","🎧 Tiesto","⚽ Mbappe","🥚 Egg","💎 Tiffany","🏙️ Berlin","🥊 McGregor","⚔️ Berserker","🛹 Skateboard","💨 Sonic","🌌 Galaxy","🌿 Leon","♟️ Checkmate","🟥 Carnage","🦅 Hermes","🚀 Rover","🀄 Mahjong","🚁 Drone","🍩 Homer","🌐 Nexus","🌊 Tsunami","☔ Seattle","🔨 Hephaestus","🦈 Shark","🔫 Master","🦹‍♂️ Lex","🗡️ Guts","🛹 Mullen","🏰 Madrid","🌌 Pluto","🎾 Federer","🤖 WallE","🔥 Pyromancer","🎩 Mobster","🌑 NewMoon","🦸‍♂️ Incredible","🔊 Echo","🔨 Thor","🛳️ Cruise","🔵 Cobalt","🌋 Mustafar","⛏️ Miner","📐 Geometry","🌹 Nobara","🛰️ Sputnik","🗡️ Kirito","❄️ SubZero","🌿 Mantis","☀️ Apollo","✈️ Airbus","⚔️ Deadpool","🐉 Dovahkiin","♋ Cancer","🏎️ Senna","🐻 Grizzly","🌫️ Fog","🎤 Dua","💀 Diablo","💨 Gale","🧇 Waffle","😈 Dante","⚙️ Steel","🏹 Cupid","🛰️ Hubble","♠️ Syndicate","🦅 Robin","🎤 Ariana","🔵 Aquamarine","👁️ Strange","💣 Missile","☯️ Yang","🦂 Cobra","🧲 Magneto","💾 Cache","🐉 Smaug","🏍️ Ducati","⌚ Omega","🍵 Matcha","🍁 Fall","🌌 Kamina","🕴️ BabaYaga","✨ Opal","🔱 Trident","💥 Blast","🏎️ Hamilton","🐎 Mustang","💀 Punisher","🦈 Jaws","🌑 Midnight","👑 Caesar","☕ Mocha","🌬️ Breeze","👁️ Retina","🏎️ Schumacher","🌌 Venus","💎 Zircon","☄️ Meteor","🦊 Naruto","🌪️ Storm","🔭 Copernicus","💊 Neo","👨‍🚀 Astronaut","💾 Byte","🧪 Pinkman","⛵ Titanic","💎 Cartier","🌠 Halley","🏎️ AMG","🚁 Chinook","🌋 Crater","🔫 Tommy","🔥 Flint","☀️ Solar","🦇 Wayne","🦅 Eagle","🏔️ Alps","💻 Root","🔥 Firewall","📏 Kelvin","🧊 Frostbite","🔮 Magic","🏦 Vault","🌮 Taco","🎈 Zeppelin","🛡️ VPN","🐉 Mushu","🌀 Vortex","⚽ Zidane","🌟 Kirby","🔥 Roy","☕ Latte","🏎️ Supra","🍰 Cake","🤠 Indy","📐 Matrix","❤️ Heart","💥 Jinx","🎾 Nadal","☁️ AWS","🌙 Night","⚔️ Wilson","🗼 Tokyo","🦊 Fox","👽 Alien","💀 Necromancer","👑 Nefertiti","🧬 DNA","☀️ Sun","🚂 Loco","😈 Daredevil","🤺 Zorro","🏍️ Kaneda","🏹 Arrow","📡 Server","🍺 Stout","🌇 Dusk","🎮 Chief","🛸 Romulan","🧪 Catalyst","⚾ Jeter","⚙️ Kernel","⚔️ Glaive","🎹 Synth","💼 Goodman","💥 Bakugo","🦥 Sloth","🛡️ Aegis","⚛️ Quantum","⛏️ Dwarf","🌙 Selene","🏖️ Ibiza","📈 Vector","⛏️ Coal","🎲 Casino","🧚‍♂️ Elf","🦖 Rex","🖖 Spock","👻 Megumi","🧫 Cell","🐉 Beijing","👑 Cleopatra","💊 Overdose","👑 Victoria","🦋 Paramore","📜 Curse","🧊 Frost","🏹 Bow","🔫 Solo","🥁 Snare","📜 Churchill","🛡️ Naofumi","👊 JoJo","🌲 Forest","⚖️ Osiris","😈 Doom","🏎️ F1","👜 Prada","🔭 Parallax","🧩 Scrabble","🐺 Stark","🚗 Civic","👾 Samus","🌊 Leviathan","🐺 Hati","⚪ Ivory","💣 Mine","🏎️ Kart","👗 Gucci","📷 Kodak","⚛️ Electron","🛡️ Shield","🔋 Battery","🥊 Mayweather","🤖 T800","⚡ Killua","🐰 NewJeans","🍷 Cartel","🥖 Baguette","🗼 Paris","🔥 Fusion","🗡️ Machete","⚙️ Panzer","🥊 Tyson","♙ Pawn","🌬️ Wind","🏔️ Denver","⚽ Neymar","🌌 Asgard","🛡️ Buckler","🤖 Cylon","🌋 Magma","⚡ Tempest","💥 Tetsuo","🦛 Hippo","🐭 Jerry","☀️ Heatwave","🌊 Ocean","🧿 Zenith","🐉 Goku","🐧 Linux","🔺 Apex","⚔️ Raiden","🦅 Ezio","🗡️ Broadsword","🛸 Voyager","🏙️ Zion","🎾 Djokovic","🌌 Horizon","🦇 Dracula","💿 Platinum","🐱 Tom","🐘 Manny","🌌 Thanos","🦘 Kangaroo","🥊 Rocky","🏙️ Gotham","🔭 Scope","🦋 Shinobu","🧥 Nomad","🛡️ Spartacus","🏦 Defi","🕷️ Widow","🌍 Orbit","✨ Nebula","🕊️ Hawks","🎼 Beethoven","🐰 Rabbit","💨 Aero","💍 Gollum","♎ Libra","🏇 Genghis","🔮 Quartz","🐍 Viper","🎧 Guetta","🃏 Poker","🌸 Seoul","🦆 Donald","🦉 Minerva","❄️ Moscow","🧊 Todoroki","🐉 Dragon","🧠 Neural","🌱 Bloom","🍩 Donut","🚁 Apache","🐗 Pumbaa","♕ Queen","🌌 MilkyWay","🌌 Klingon","🐕 Doge","🌌 Supernova","🐎 Aragorn","🏎️ Falcon","☀️ Morning","🌸 Sakura","🐅 Tiger","🎤 Freddie","🦡 Badger","🛡️ Zelda","⚔️ Levi","🔑 Token","☕ Espresso","🏛️ Rome","🤠 Woody","🎤 Kendrick","🎭 Rio","🐉 Drogo","🐍 Slytherin","🚗 Furiosa","⚙️ Logic","🎸 Cobain","🐺 Skoll","⚡ Tracer","⚡ Flash","🐉 Bowser","🐴 Donkey","🎭 Mirage","❄️ Blizzard","🐺 Logan","🏂 White","🌘 Equinox","🧹 Nimbus","🔭 Astro","🔫 Vash","🚬 Detective","☔ Monsoon","😈 Krampus","🏍️ Harley","💻 Zero","🌃 Skyline","🎙️ Sinatra","🌌 Sky","🖥️ Monitor","🗡️ Katana","🍻 Brew","🔫 Vincent","⚔️ Tanjiro","🦅 Falco","🔥 Torch","🌡️ Celsius","🔫 Magnum","🐻 Bear","🔴 Ruby","⚛️ Neutron","🛸 UFO","🏹 Rambo","👾 Glitch","🏜️ Canyon","☄️ Meteorite","🌆 Metropolis","🛥️ Stealth","🔒 Crypto","🦅 Garuda","🍖 Sanji","🚜 Tractor","🔬 Proton","🚪 Portal","♠️ Spade","🦍 Kong","🦸‍♂️ KalEl","🌐 IP","🍪 Cookie","✨ Stardust","💘 IVE","🪄 Merlin","🏀 LeBron","🔥 Illidan","⚡ Storm","🌊 Surge","🖥️ Host","❄️ Arthas","🛸 Enterprise","🗡️ Rogue","❄️ Winter","🗡️ Marth","🚲 BMX","🛥️ Yacht","☀️ Helios","🎧 Kanye","🔷 Sapphire","🚪 Narnia","🔫 Musket","⚔️ Spear","🦝 Rocket","🔫 Croft","🎯 Wick","🏜️ Oasis","🦉 Athena","🐘 Elephant","👁️ Fremen","🏎️ GTR","🌌 Andromeda","⏳ Chronos","🗻 Fuji","🖖 Vulcan","⚔️ Wallace","👻 Phantom","🚀 Concorde","🎼 Mozart","🥪 Sub","♉ Taurus","🐈 Sylvester","♊ Gemini","⚔️ Link","🤖 Claptrap","♒ Aquarius","🎸 Gibson","🦊 Kurama","⬛ Borg","🐘 Hannibal","🦾 Jax","💥 Oppenheimer","🧠 Brain","🏢 McClane","🧟‍ Rick","🤡 Joker","⚙️ Chrome","🦝 Raccoon","🐉 Toothless","🐉 Triad","🥩 Wagyu","🐭 Mouse","🔨 Odinson","🌐 Ping","🐍 Snake","📓 Ryuk","👽 Predator","🗡️ Snow","🔌 Cable","🏂 McMorris","🌌 Dimension","🦅 Raven","⚔️ Mandalorian","🌊 Poseidon","⚡ Socket","🏔️ Avalanche","⛄ Olaf","🔗 Blockchain","🥊 ChunLi","♓ Pisces","🕶️ Snoop","💻 Cipher","🐎 Rohan","🍫 Gump","🦇 Gargoyle","👑 Richard","⚙️ RAM","🦾 Malware","🔭 Einstein","♐ Sagittarius","🐆 Jaguar","🐺 Coyote","🥊 Pacquiao","🧝‍♀️ Galadriel","🏀 Jordan","🐪 Cairo","⚽ Maradona","🧸 Pooh","🛡️ Kevlar","🏎️ Bugatti","🍁 Toronto","🚀 Ripley","🦨 Skunk","🍷 Lecter","😈 Lucifer","🚢 Davy","🌐 Protocol","⚔️ Saladin","♘ Knight","🏜️ Dune","🌑 Omen","🎸 Elvis","🔑 RSA","⚓ Dreadnought","👹 Shrek","🍷 Merlot","⚔️ Valkyrie","✈️ Maverick","🦅 Pegasus","🦇 Morrigan","🕉️ Om","🎸 Metallica","🌌 Mars","⛏️ Gordon","🕰️ Paradox","🌋 Volcano","🔱 Odin","📉 Entropy","🔩 Tungsten","🐦 Tweety","🧱 Clay","🍏 Apple","⚔️ Mulan","🌳 Groot","⚙️ Marcus","⚙️ Edward","🌌 Saturn","🔥 Ember","❄️ Yeti","🧬 Gene","🚗 Brian","🦉 Hedwig","🏎️ Verstappen","🎸 Sheeran","💥 Nova","👜 Birkin","🦅 Kent","🍷 Shiraz","🏰 Hogwarts","🗡️ Arya","🧪 Plasma","🍃 Totoro","🐙 Kraken","🍷 Dionysus","💾 Drive","🌋 Mordor","🌧️ Rain","⚓ Freeman","🐉 Yakuza","🌸 Spring","🕵️ L","💎 Hodl","🛡️ Kite","🛡️ Carbon","🕶️ Eazy","⛰️ Mountain","📊 Calculus","🦇 Aventador","🐗 Inosuke","🛸 Apollo","👑 Jackson","⚽ Ronaldo","💻 Pixel","⚡ Switch","🏎️ Furiosa","🦆 Daffy","🌾 Demeter","🦊 StarFox","☀️ Ra","🎸 Fender","🎣 Gon","⚡ Potter","🎰 Vegas","🎩 Corleone","🐺 KaerMorhen","🗡️ Joan","🎤 Adele","🌐 Web","🤖 2B","🏎️ Dom","👊 Baki","🌟 Rihanna","🐱 Puss","⚔️ Vader","🎩 Shelby","🏍️ Akira","✨ Halo","🐼 Panda","🕸️ Darknet","📜 SunTzu","🌉 London","🤖 R2D2","🎸 Nirvana","🦴 Spine","🌌 Surfer","🌙 Hunter","👊 Monk","🏰 Citadel","🥓 Bacon","🛰️ Webb","🕶️ Mirage","⛵ Magellan","🏙️ Neon","☀️ Daylight","🐶 Scooby","🌊 Abyss","🏞️ River","🐾 Cerberus","💎 Diamond","🌊 Giyu","🗡️ Ichigo","🌴 LA","🌪️ Typhoon","⚡ Shazam","🧲 Electromagnet","🧞 Genie","🎤 Eminem","🏌️ McIlroy","🚦 Router","🐈 BlackCat","🔬 Biology","⛓️ Titanium","🕵️ Bourne","🧀 Cheese","🦍 Donkey","🥯 Bagel","🐆 Panther","🐭 Mickey","⚡ Kakashi","🦾 Cable","👹 Slayer","💀 Hel","🧪 Heisenberg","✨ Nirvana","🦆 Scrooge","🍄 Luigi","🍟 Fries","💊 Pill","💻 Turing","⚽ Messi","📸 Leica","⛈️ Thunder","🏹 Ranger","🚪 Port","🎨 DaVinci","🖤 PinkFloyd","🦇 Bat","⚡ Spark","👑 Tupac","🧞‍♂️ Aladdin","🦾 Bionic","🎧 Avicii","🐨 Koala","🍕 Slice","🛡️ Porsche","🌵 Desert","🥃 Bourbon","🐍 Medusa","⛵ Galleon","🏹 Artemis","🖤 Obsidian","🎲 Roulette","🗡️ Brutus","💉 Serum","⚔️ Pike","⚽ Beckham","⚙️ Docker","🥂 Champagne","🎾 Serena","🎸 Hendrix","🏎️ McQueen","🌨️ Hail","🗡️ Scimitar","🛡️ Paladin","⚡ Zeus","🧸 Ted","🍫 Cacao","🔌 Node","🕳️ Wormhole","🐯 Diego","🔵 Lapis","🛹 Hawk","🦈 Orca","🦴 Skull","🧬 Chromosome","🌌 Aether","👁️ Karma","🧚‍♀️ Freya","✨ Spice","🏊 Phelps","🕵️ Holmes","🖤 Blackpink","🏴‍☠️ Sparrow","⚔️ Ragnar","🧱 Thing","💍 Ring","🔊 Sonic","💃 Tango","🎹 Mozart","⌚ Rolex","🔫 Doomguy","🦁 Mufasa","⚽ Pele","🥐 Croissant","🐍 Jormungandr","⛓️ Kratos","☮️ Peace","🐺 Wolf","🚗 McFly","🐢 Raphael","🏹 Katniss","🐺 Jon","🕵️ Assassin","🖥️ Terminal","🎲 Monopoly","🎶 Bard","🗡️ Yuji","🔌 Motoko","👑 Charlemagne","🌍 Atlas","🏍️ Chopper","🌟 Jotaro","🧟 Jill","🥨 Pretzel","🦞 Boston","🕊️ Gandhi","🧊 Elsa","👊 Saitama","📈 Bull","🗡️ Rapier","🦅 Sphinx","🔫 Sniper","🏜️ Sahara","🌌 Neptune","🌠 ShootingStar","🔮 Mystic","🦓 Zebra","🔥 Hestia","🌌 Quill","💡 Tesla","✈️ Blackbird","🚬 Draper","🛡️ Arthur","🌀 String","💀 Reaper","🦅 Gryffindor","🏔️ Everest","🦾 Alphonse","⚽ Ronaldinho","📡 Uplink","🗝️ Key","🕷️ Morales","🚀 Falcon9","⌨️ Hacker","💠 Vertex","🔫 Price","🦅 Falcon","🐺 Fenrir","🎭 Persona","🚀 Buzz","🛡️ Ares","🎩 Wonka","🕸️ Venom","🚬 Cigar","🍖 Luffy"]

CF_PORTS = [443, 2053, 2083, 2087, 2096, 8443]

def get_patterniha_commit_time():
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ProxyTester"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        import requests
        url = "https://api.github.com/repos/patterniha/Free-Configs/commits?path=configs.txt&page=1&per_page=1"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                date_str = data[0]["commit"]["committer"]["date"]
                return datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass
    return None

def sync_patterniha_if_needed():
    commit_dt = get_patterniha_commit_time()
    if not commit_dt:
        return
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    age_hours = (now_utc - commit_dt).total_seconds() / 3600.0
    if age_hours > 20.0:
        print(f"Patterniha configs updated {age_hours:.1f}h ago (>20h). Waiting up to 45m for fresh release...", flush=True)
        deadline = time.time() + (45 * 60)
        while time.time() < deadline:
            time.sleep(60)
            new_dt = get_patterniha_commit_time()
            if new_dt and (new_dt > commit_dt or (datetime.datetime.now(datetime.timezone.utc) - new_dt).total_seconds() / 3600.0 < 2.0):
                print("Fresh Patterniha release detected! Proceeding.", flush=True)
                break
        else:
            print("45m wait limit reached without new release. Proceeding with current version.", flush=True)

sync_patterniha_if_needed()

DEFAULT_FINALMASK_SETTINGS = {
    "tcp": [
        {"type": "fragment", "settings": {"packets": "tlshello", "lengths": ["0", "104", "1"], "delays": ["0"], "maxSplit": "0"}},
        {"type": "fragment", "settings": {"packets": "1-1", "lengths": ["114", "1"], "delays": ["1"], "maxSplit": "11"}}
    ]
}

def get_dynamic_patterniha_settings():
    clean_ip, clean_fm = None, None
    try:
        import requests
        resp = requests.get('https://raw.githubusercontent.com/patterniha/Free-Configs/main/configs.txt', timeout=10)
        if resp.status_code == 200:
            for l in resp.text.splitlines():
                if not clean_ip:
                    m_ip = re.search(r'@([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):', l)
                    if m_ip:
                        clean_ip = m_ip.group(1)
                if not clean_fm:
                    m_fm = re.search(r'[?&]fm=([^&#]+)', l)
                    if m_fm:
                        try:
                            parsed_fm = json.loads(urllib.parse.unquote(m_fm.group(1)))
                            if isinstance(parsed_fm, dict) and "tcp" in parsed_fm:
                                clean_fm = parsed_fm
                        except Exception:
                            pass
                if clean_ip and clean_fm:
                    break
    except Exception:
        pass

    if not clean_ip or not clean_fm:
        url_target = 'patterniha/Free-Configs'
        sub_list_file = './sub/sub_list.txt'
        if os.path.exists(sub_list_file):
            try:
                with open(sub_list_file, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip()]
                for idx, line in enumerate(lines, 1):
                    if url_target in line:
                        list_file = f'./sub/list/{idx:02d}.txt'
                        if os.path.exists(list_file):
                            with open(list_file, 'r', encoding='utf-8') as lf:
                                for l in lf:
                                    if not clean_ip:
                                        m_ip = re.search(r'@([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+):', l)
                                        if m_ip:
                                            clean_ip = m_ip.group(1)
                                    if not clean_fm:
                                        m_fm = re.search(r'[?&]fm=([^&#]+)', l)
                                        if m_fm:
                                            try:
                                                parsed_fm = json.loads(urllib.parse.unquote(m_fm.group(1)))
                                                if isinstance(parsed_fm, dict) and "tcp" in parsed_fm:
                                                    clean_fm = parsed_fm
                                            except Exception:
                                                pass
                                    if clean_ip and clean_fm:
                                        break
            except Exception:
                pass

    return clean_ip or "188.114.97.6", clean_fm or DEFAULT_FINALMASK_SETTINGS

PREFERRED_TARGETS = [
    "www.npmjs.com", "www.canva.com", "unpkg.com", "www.speedtest.net",
    "www.cdnjs.com", "www.nodejs.org", "141.101.90.101", "104.18.2.92"
]
DYNAMIC_CLEAN_IP, FINALMASK_SETTINGS = get_dynamic_patterniha_settings()
RESILIENCE_TARGETS = PREFERRED_TARGETS + ([DYNAMIC_CLEAN_IP] * 3)

# --- Parameters ---
ETERNITY_LIST_SIZE = 165
REALITY_TARGET_PERCENT = 0.50
REALITY_TARGET_SIZE = math.ceil(ETERNITY_LIST_SIZE * REALITY_TARGET_PERCENT)
NODES_PER_COUNTRY = 1
COUNTRY_NODE_LIMITS = {
    'TR': 4,
    'CN': 2,
    'DE': 10,
    'NL': 10
}

# Hard maximum caps to prevent Runner Bias domination and unwanted countries
COUNTRY_MAX_LIMITS = {
    'US': 30,
    'CA': 10,
    'CN': 2,
    'TR': 4,
    'RELAY': 30
}

# Maximum allowed nodes that share the exact same UUID/Password.
MAX_SAME_UUID = 5 

def is_ip_address(address):
    if not isinstance(address, str):
        return False
    clean = address.strip('[]')
    try:
        ipaddress.ip_address(clean)
        return True
    except ValueError:
        return False
    
def get_proxy_signature(link):
    try:
        if link.startswith('vless://') or link.startswith('trojan://'):
            parsed = urllib.parse.urlparse(link)
            uuid = parsed.username or "unknown"
            server = parsed.hostname or "unknown"
            port = parsed.port or 443
            return f"{server}:{port}:{uuid}"
        
        elif link.startswith('ss://'):
            parsed = urllib.parse.urlparse(link)
            if '@' in parsed.netloc:
                userinfo, server_port = parsed.netloc.rsplit('@', 1)
            else:
                decoded = base64.b64decode(parsed.netloc + '=' * (-len(parsed.netloc) % 4)).decode('utf-8', errors='ignore')
                if '@' in decoded:
                    userinfo, server_port = decoded.rsplit('@', 1)
                else:
                    return link
            server, port_str = server_port.rsplit(':', 1)
            return f"{server.strip('[]')}:{port_str}:{userinfo}"

        elif link.startswith('vmess://'):
            b64 = link.replace("vmess://", "").split('#')[0]
            b64 += '=' * (-len(b64) % 4)
            b64 = b64.replace('-', '+').replace('_', '/')
            j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
            server = str(j.get('add', 'unknown')).strip('[]')
            port = j.get('port', '443')
            uuid = j.get('id', 'unknown')
            return f"{server}:{port}:{uuid}"
    except:
        pass
    
    if '#' in link:
        return link.split('#')[0]
    return link

def is_cloudflare_ip(ip):
    if not ip: return False
    try:
        clean = ip.strip('[]')
        addr = ipaddress.ip_address(clean)
        if addr.version == 4:
            octets = [int(o) for o in clean.split('.')]
            if octets[0] == 104 and (16 <= octets[1] <= 31): return True
            if octets[0] == 172 and (64 <= octets[1] <= 71): return True
            if octets[0] == 162 and (158 <= octets[1] <= 159): return True
            if octets[0] == 188 and octets[1] == 114 and (96 <= octets[2] <= 111): return True
            if octets[0] == 108 and octets[1] == 162 and (192 <= octets[2] <= 255): return True
            if octets[0] == 198 and octets[1] == 41 and (128 <= octets[2] <= 255): return True
            if octets[0] == 173 and octets[1] == 245 and (48 <= octets[2] <= 63): return True
            if octets[0] == 103 and octets[1] == 21 and (244 <= octets[2] <= 247): return True
            if octets[0] == 103 and octets[1] == 22 and (200 <= octets[2] <= 203): return True
            if octets[0] == 103 and octets[1] == 31 and (4 <= octets[2] <= 7): return True
            if octets[0] == 141 and octets[1] == 101 and (64 <= octets[2] <= 127): return True
            if octets[0] == 190 and octets[1] == 93 and (240 <= octets[2] <= 255): return True
            if octets[0] == 197 and octets[1] == 234 and (240 <= octets[2] <= 243): return True
            if octets[0] == 131 and octets[1] == 0 and (72 <= octets[2] <= 75): return True
        elif addr.version == 6:
            cf_v6 = ['2606:4700::/32', '2803:f800::/32', '2405:b500::/32', '2405:8100::/32', '2a06:98c0::/29', '2c0f:f248::/32']
            return any(addr in ipaddress.ip_network(net) for net in cf_v6)
    except:
        pass
    return False

def get_uuid(link):
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
    os.makedirs(LOGS_DIR, exist_ok=True)
    files_to_touch = [
        FULL_OUTPUT_FILE, FULL_OUTPUT_BASE64_FILE, ETERNITY_OUTPUT_FILE,
        ETERNITY_OUTPUT_BASE64_FILE, LOG_INFO_FILE,
        DIVERSITY_OUTPUT_FILE, DIVERSITY_OUTPUT_BASE64_FILE,
        RESILIENCE_OUTPUT_FILE, RESILIENCE_OUTPUT_BASE64_FILE,
        os.path.join(LOGS_DIR, 'dead_nodes.txt')
    ]
    for f in files_to_touch:
        open(f, 'w').close()
    
    os.makedirs(SPLITTED_OUTPUT_DIR, exist_ok=True)
    for p in ['vmess.txt', 'vless.txt', 'trojan.txt', 'ss.txt']:
        open(os.path.join(SPLITTED_OUTPUT_DIR, p), 'w').close()

def create_resilience_clone(node, theme_name, apply_fragment=False):
    link = node.get('link', '')
    ip = node.get('ip', '')
    if not is_cloudflare_ip(ip): return None

    target_addr = random.choice(RESILIENCE_TARGETS)

    if link.startswith('vless://') or link.startswith('trojan://'):
        try:
            scheme, rest = link.split('://', 1)
            user_server, query_name = rest.split('?', 1)
            user, server_port = user_server.split('@', 1)

            if ':' in server_port:
                server, port_str = server_port.rsplit(':', 1)
                server = server.strip('[]')
                port = int(port_str)
            else:
                server = server_port.strip('[]')
                port = 443

            if port not in CF_PORTS: return None

            if '#' in query_name: query, name = query_name.split('#', 1)
            else: query, name = query_name, "Proxy"

            params = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
            net = params.get('type', 'tcp')
            sec = params.get('security', 'none')

            if sec != 'tls': return None
            if net not in ['ws', 'grpc', 'httpupgrade', 'xhttp']: return None

            origin_sni = params.get('sni') or (server if not is_ip_address(server) else '')
            if not origin_sni: return None
            params['sni'] = origin_sni
            if net in ['ws', 'httpupgrade', 'xhttp']:
                if 'host' not in params or not params['host']: params['host'] = origin_sni

            params['security'] = 'tls'
            params['fp'] = 'chrome'
            params.pop('cipherSuites', None)
            params.pop('cs', None)
            if scheme == 'vless' and not params.get('encryption'):
                params['encryption'] = 'none'

            if apply_fragment:
                params['fm'] = json.dumps(FINALMASK_SETTINGS, separators=(',', ':'))
            else:
                params.pop('fm', None)

            server = target_addr
            new_query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            quoted_theme_name = urllib.parse.quote(theme_name)

            clone = node.copy()
            clone['link'] = f"{scheme}://{user}@{server}:{port}?{new_query}#{quoted_theme_name}"
            clone['tag'] = theme_name
            return clone
        except Exception: return None

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
            if net not in ['ws', 'grpc', 'httpupgrade', 'xhttp']: return None

            original_add = str(j.get('add', ''))
            origin_sni = str(j.get('sni', '')) or (original_add if not is_ip_address(original_add) else '')
            if not origin_sni: return None
            j['sni'] = origin_sni
            if net in ['ws', 'httpupgrade', 'xhttp']:
                if 'host' not in j or not j['host']: j['host'] = origin_sni

            j['tls'] = 'tls'
            j['fp'] = 'chrome'
            j['add'] = target_addr
            j['ps'] = theme_name
            new_b64 = base64.b64encode(json.dumps(j, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).decode('ascii')

            clone = node.copy()
            clone['link'] = f"vmess://{new_b64}"
            clone['tag'] = j['ps']
            return clone
        except Exception: return None
    return None

def process_and_save_results():
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 0. Organize existing logs into Logs directory
    for log_f in ['runner_logs.txt', 'parse_errors.txt', 'xray_crashes.txt']:
        if os.path.exists(log_f):
            shutil.move(log_f, os.path.join(LOGS_DIR, log_f))

    parse_error_count = 0
    if os.path.exists(os.path.join(LOGS_DIR, 'parse_errors.txt')):
        with open(os.path.join(LOGS_DIR, 'parse_errors.txt'), 'r', encoding='utf-8') as f:
            parse_error_count = sum(1 for line in f if line.strip())

    try:
        with open(META_FILE, 'r', encoding='utf-8') as f:
            nodes = json.load(f)
        print(f"Successfully read {len(nodes)} nodes from {META_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Could not read or parse {META_FILE}. Details: {e}")
        ensure_empty_files()
        return

    tested_count = len(nodes)
    total_incoming_nodes = tested_count + parse_error_count

    dead_nodes_list = []

    for node in nodes:
        speed = node.get('avg_speed', 0)
        delay = node.get('delay', 9999)
        speed_mb = speed / 1_000_000

        if delay > 0 and delay < 5000:
            latency_score = max(0, 100 - (delay / 10))
        else:
            latency_score = 0

        health = (speed_mb * 7) + (latency_score * 0.3)
        node['health_score'] = health
        
        if health == 0:
            dead_nodes_list.append(node.get('link', ''))

    working_nodes = [node for node in nodes if node.get('health_score', 0) > 0]
    
    # Dump Dead Nodes
    with open(os.path.join(LOGS_DIR, 'dead_nodes.txt'), 'w', encoding='utf-8') as f:
        f.write("\n".join(dead_nodes_list))
    
    if not working_nodes:
        print("No working nodes found. Output files will be empty.")
        ensure_empty_files()
        return
        
    print(f"Found {len(working_nodes)} working nodes.")
    working_nodes.sort(key=lambda x: x.get('health_score', 0), reverse=True)

    unique_servers = list({node.get('server', '') for node in working_nodes if node.get('server')})
    resolved_ips = {}
    print(f"Resolving {len(unique_servers)} unique domains concurrently...", flush=True)

    def resolve_domain(server):
        clean = server.strip('[]')
        if is_ip_address(clean): return server, clean
        try: return server, socket.gethostbyname(server)
        except: return server, ''

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(resolve_domain, unique_servers)
        for server, ip in results: resolved_ips[server] = ip

    raw_processed = []
    if os.path.exists(GEOIP_DB):
        with geoip2.database.Reader(GEOIP_DB) as reader:
            for node in working_nodes:
                server = node.get('server', '')
                ip_address = resolved_ips.get(server, '')
                country_code, country_name = 'XX', 'Unknown'
                
                if is_cloudflare_ip(ip_address):
                    country_code, country_name = 'RELAY', 'Relay'
                elif ip_address:
                    try:
                        res_country = reader.country(ip_address)
                        country_code = res_country.country.iso_code or 'XX'
                        country_name = res_country.country.name or 'Unknown'
                    except: pass

                if country_code in ['CLOUDFLARE', 'PRIVATE', 'XX']:
                    country_code, country_name = 'RELAY', 'Relay'

                sim_delay = node.get('delay', 9999)
                sim_speed = node.get('avg_speed', 0)
                
                if country_code in ['US', 'CA']:
                    if sim_delay < 120: sim_delay = sim_delay + ((120 - sim_delay) * 0.8)
                    sim_speed = int(sim_speed * 0.9)
                
                speed_mb = sim_speed / 1_000_000
                latency_score = max(0, 100 - (sim_delay / 10)) if 0 < sim_delay < 5000 else 0
                new_health = (speed_mb * 7) + (latency_score * 0.3)

                link = node.get('link')
                if link:
                    raw_processed.append({
                        'link': link, 'ip': ip_address, 'tag': node.get('tag', 'N/A'),
                        'speed': sim_speed, 'delay': int(sim_delay),
                        'health_score': new_health, 'country': country_code, 'country_name': country_name
                    })
    else:
        for node in working_nodes:
            if node.get('link'):
                raw_processed.append({
                    'link': node['link'], 'ip': '', 'tag': node.get('tag', 'N/A'),
                    'speed': node.get('avg_speed', 0), 'delay': node.get('delay', 9999),
                    'health_score': node.get('health_score', 0), 'country': 'RELAY', 'country_name': 'Relay'
                })

    print("Deduplicating proxies by configuration...")
    seen_signatures = {}
    for node in raw_processed:
        signature = get_proxy_signature(node['link'])
        if signature not in seen_signatures:
            seen_signatures[signature] = node
        else:
            if node['health_score'] > seen_signatures[signature]['health_score']:
                seen_signatures[signature] = node

    def clean_link_params(raw_link):
        raw_link = html.unescape(raw_link)
        raw_link = re.sub(r'([?&])allowInsecure=(?:1|true)', r'\1allowInsecure=0', raw_link, flags=re.IGNORECASE)
        raw_link = re.sub(r'([?&])insecure=(?:1|true)', r'\1insecure=0', raw_link, flags=re.IGNORECASE)

        def process_fm(m):
            raw_fm = urllib.parse.unquote(m.group(2))
            valid_fm = None
            for candidate in [raw_fm, raw_fm.replace('+', ' ')]:
                try:
                    obj = json.loads(candidate)
                    if isinstance(obj, dict) and any(x in obj for x in ("tcp", "udp", "quicParams")):
                        valid_fm = json.dumps(obj, separators=(',', ':'))
                        break
                except Exception:
                    pass
            
            if valid_fm:
                return m.group(1) + "fm=" + urllib.parse.quote(valid_fm) + m.group(3)
            else:
                if m.group(1) == '?' and m.group(3) == '&': return '?'
                elif m.group(1) == '&' and m.group(3) == '&': return '&'
                else: return ''

        if "fm=" in raw_link:
            while True:
                new_link = re.sub(r'([?&])fm=([^&#]*)(&?)', process_fm, raw_link)
                if new_link == raw_link:
                    break
                raw_link = new_link

        def process_extra(m):
            raw_extra = urllib.parse.unquote(m.group(2))
            for candidate in [raw_extra, raw_extra.replace('+', ' ')]:
                try:
                    obj = json.loads(candidate)
                    if isinstance(obj, dict) and obj:
                        return m.group(1) + "extra=" + urllib.parse.quote(json.dumps(obj, separators=(',', ':'))) + m.group(3)
                except Exception:
                    pass

            if m.group(1) == '?' and m.group(3) == '&': return '?'
            elif m.group(1) == '&' and m.group(3) == '&': return '&'
            else: return ''

        if "extra=" in raw_link:
            while True:
                new_link = re.sub(r'([?&])extra=([^&#]*)(&?)', process_extra, raw_link)
                if new_link == raw_link:
                    break
                raw_link = new_link
                
        return raw_link

    unique_nodes = list(seen_signatures.values())
    unique_nodes.sort(key=lambda x: x.get('health_score', 0), reverse=True)
    duplicates_removed = len(raw_processed) - len(unique_nodes)

    all_processed_nodes = []
    random_numbers = [random.randint(1000, 9999) for _ in range(len(unique_nodes))]

    for index, node in enumerate(unique_nodes):
        country_code, country_name = node['country'], node['country_name']
        name_emoji = EMOJI.get(country_code, EMOJI['NOWHERE'])
        country_name_formatted = COUNTRY_NAME_MAPPING.get(country_name, country_name).replace(' ', '-')
        pretty_name = f'{name_emoji} {country_name_formatted}-{random_numbers[index]}'
        quoted_pretty_name = urllib.parse.quote(pretty_name)

        link = clean_link_params(node['link'])
        if link.startswith("vmess://"):
            try:
                b64 = link.replace("vmess://", "").split('#')[0]
                b64 += '=' * (-len(b64) % 4)
                b64 = b64.replace('-', '+').replace('_', '/')
                j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
                j['ps'] = pretty_name 
                new_b64 = base64.b64encode(json.dumps(j, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).decode('ascii')
                node['link'] = f"vmess://{new_b64}"
            except: node['link'] = f"{link.split('#')[0]}#{quoted_pretty_name}"
        else:
            node['link'] = f"{link.split('#')[0]}#{quoted_pretty_name}"

        node['tag'] = pretty_name
        all_processed_nodes.append(node)

    print("\n--- Generating Domain-Fronted Resilience List ---")
    resilience_candidates = [p for p in all_processed_nodes if p['country'] not in BLOCKED_COUNTRIES]

    def calculate_iran_score(node):
        score = node.get('health_score', 0)
        link = node.get('link', '')
        sni, port, net = "", 443, ""
        try:
            if link.startswith(('vless://', 'trojan://')):
                parsed = urllib.parse.urlparse(link)
                port = parsed.port if parsed.port else 443
                query = dict(urllib.parse.parse_qsl(parsed.query))
                sni = query.get('sni', '').lower()
                net = query.get('type', '').lower()
            elif link.startswith('vmess://'):
                b64 = link.split('://')[1].split('#')[0]
                b64 += '=' * (-len(b64) % 4)
                j = json.loads(base64.b64decode(b64.replace('-', '+').replace('_', '/')).decode('utf-8', errors='ignore'))
                port = int(j.get('port', 443))
                sni = str(j.get('sni', '')).lower()
                net = str(j.get('net', '')).lower()
        except: pass

        burned = ['workers.dev', 'trycloudflare.com', 'pages.dev', 'eu.org']
        if any(b in sni for b in burned):
            score -= 25

        if port == 443:
            score += 15
        if net in ['xhttp', 'grpc']:
            score += 10
        if '.ir' in sni or sni.endswith('.ir.'):
            score += 25
        return score

    resilience_candidates.sort(key=calculate_iran_score, reverse=True)
    resilience_nodes = []
    theme_pool = list(RESILIENCE_THEMES)
    random.shuffle(theme_pool)

    for node in resilience_candidates:
        if len(resilience_nodes) >= 300: break
        if not theme_pool:
            theme_pool = list(RESILIENCE_THEMES)
            random.shuffle(theme_pool)

        current_theme = theme_pool.pop(0)
        theme_name = f"{current_theme}-{random.randint(1000, 9999)}"

        apply_fragment = (len(resilience_nodes) % 2 == 0)
        cloned = create_resilience_clone(node, theme_name, apply_fragment)
        if cloned: resilience_nodes.append(cloned)
        else: theme_pool.insert(0, current_theme)

    res_links = [p['link'] for p in resilience_nodes]
    random.shuffle(res_links)
    with open(RESILIENCE_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(res_links))
    with open(RESILIENCE_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(res_links).encode()).decode())

    print("Calculating UUID spam metrics...")
    uuid_counts_stats = {}
    spam_removed = 0
    for node in all_processed_nodes:
        uuid = get_uuid(node['link'])
        if uuid:
            if uuid_counts_stats.get(uuid, 0) >= MAX_SAME_UUID:
                spam_removed += 1
            uuid_counts_stats[uuid] = uuid_counts_stats.get(uuid, 0) + 1

    print("\n--- Generating Diversity List ---")
    diversity_nodes_by_country = {}
    for node in all_processed_nodes:
        c = node['country']
        if c in ['RELAY', 'XX']: continue
        if node['delay'] < 2000 and node['speed'] >= 50000:
            if c not in diversity_nodes_by_country: diversity_nodes_by_country[c] = []
            diversity_nodes_by_country[c].append(node)

    diversity_nodes = []
    for c, c_nodes in diversity_nodes_by_country.items():
        c_nodes.sort(key=lambda x: x['health_score'], reverse=True)
        diversity_nodes.extend(c_nodes[:3])

    diversity_links = [p['link'] for p in diversity_nodes]
    random.shuffle(diversity_links)
    with open(DIVERSITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(diversity_links))
    with open(DIVERSITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(diversity_links).encode()).decode())

    conventional_nodes = [p for p in all_processed_nodes if p['country'] not in BLOCKED_COUNTRIES]
    full_links = [p['link'] for p in conventional_nodes]
    random.shuffle(full_links)

    with open(FULL_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(full_links))
    with open(FULL_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(full_links).encode()).decode())

    vmess_out, vless_out, trojan_out, ss_out = [], [], [], []
    for link in full_links:
        if link.startswith("vmess://"): vmess_out.append(link)
        if link.startswith("vless://"): vless_out.append(link)
        if link.startswith("trojan://"): trojan_out.append(link)
        if link.startswith("ss://"): ss_out.append(link)

    with open(os.path.join(SPLITTED_OUTPUT_DIR, "vmess.txt"), 'w') as f: f.write("\n".join(vmess_out))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "vless.txt"), 'w') as f: f.write("\n".join(vless_out))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "trojan.txt"), 'w') as f: f.write("\n".join(trojan_out))
    with open(os.path.join(SPLITTED_OUTPUT_DIR, "ss.txt"), 'w') as f: f.write("\n".join(ss_out))

    log_list = [f"name: {n['tag']} | avg_speed: {n.get('speed',0)/1_048_576:.3f} MB/s | delay: {n['delay']} ms\n" for n in conventional_nodes]
    with open(LOG_INFO_FILE, 'w', encoding='utf-8') as f: f.writelines(log_list)

    print("\n--- Initiating Local Iran Probe Coordination ---")
    iran_verified_records = coordinate_iran_probe(full_links)

    print("\n--- Generating Eternity List ---")

    def is_vless_reality(link):
        if not link.startswith('vless://'):
            return False
        l = link.lower()
        return 'security=reality' in l or 'security%3dreality' in l

    uuid_counts_eternity = {}
    eternity_candidates = []
    for node in conventional_nodes:
        link = node['link']
        if link.startswith(('ss://', 'vmess://')):
            continue
        uuid = get_uuid(link)
        if not uuid:
            eternity_candidates.append(node)
            continue
        if uuid_counts_eternity.get(uuid, 0) < MAX_SAME_UUID:
            eternity_candidates.append(node)
            uuid_counts_eternity[uuid] = uuid_counts_eternity.get(uuid, 0) + 1

    nodes_by_country = {}
    for node in eternity_candidates:
        if node['speed'] > 50000:
            c = node['country']
            if c not in nodes_by_country:
                nodes_by_country[c] = []
            nodes_by_country[c].append(node)

    def reality_rank(link):
        if not is_vless_reality(link):
            return 2
        l = link.lower()
        if 'type=grpc' in l or 'type=xhttp' in l:
            return 0
        return 1

    eternity_candidates.sort(key=lambda x: (reality_rank(x['link']), -x['speed']))

    for c in nodes_by_country:
        nodes_by_country[c].sort(key=lambda x: (reality_rank(x['link']), -x['speed']))

    eternity_nodes = []
    selected = set()
    selected_sigs = set()
    reality_c = 0
    c_counts = {}

    def add_to_eternity(n, ignore_country_limit=False):
        nonlocal reality_c
        c_code = n['country']
        max_allowed = COUNTRY_MAX_LIMITS.get(c_code, 999)
        if not ignore_country_limit and c_counts.get(c_code, 0) >= max_allowed:
            return False

        eternity_nodes.append(n)
        selected.add(n['link'])
        sig = get_proxy_signature(n['link'])
        if sig:
            selected_sigs.add(sig)
        c_counts[c_code] = c_counts.get(c_code, 0) + 1
        if is_vless_reality(n['link']):
            reality_c += 1
        return True

    def get_patterniha_raw_links():
        links = []
        try:
            import requests
            resp = requests.get('https://raw.githubusercontent.com/patterniha/Free-Configs/main/configs.txt', timeout=10)
            if resp.status_code == 200:
                links = [l.strip() for l in resp.text.splitlines() if l.strip() and l.startswith(('vless://', 'trojan://'))]
        except Exception:
            pass
        if not links:
            url_target = 'patterniha/Free-Configs'
            sub_list_file = './sub/sub_list.txt'
            if os.path.exists(sub_list_file):
                try:
                    with open(sub_list_file, 'r', encoding='utf-8') as f:
                        lines = [l.strip() for l in f if l.strip()]
                    for idx, line in enumerate(lines, 1):
                        if url_target in line:
                            list_file = f'./sub/list/{idx:02d}.txt'
                            if os.path.exists(list_file):
                                with open(list_file, 'r', encoding='utf-8') as lf:
                                    links = [l.strip() for l in lf if l.strip() and l.startswith(('vless://', 'trojan://'))]
                except Exception:
                    pass
        return links

    if iran_verified_records:
        verified_map = {item['link']: item.get('delay', 9999) for item in iran_verified_records if 'link' in item}
        verified_nodes_pool = []
        for n in conventional_nodes:
            if n['link'] in verified_map:
                node_copy = n.copy()
                node_copy['iran_delay'] = verified_map[n['link']]
                verified_nodes_pool.append(node_copy)

        verified_nodes_pool.sort(key=lambda x: x.get('iran_delay', 9999))
        uuid_counts_verified = {}
        for vn in verified_nodes_pool:
            if len(eternity_nodes) >= 140:
                break
            uid = get_uuid(vn['link'])
            if uid:
                if uuid_counts_verified.get(uid, 0) >= MAX_SAME_UUID:
                    continue
                uuid_counts_verified[uid] = uuid_counts_verified.get(uid, 0) + 1
            add_to_eternity(vn, ignore_country_limit=True)
                
    raw_patterniha_links = get_patterniha_raw_links()
    patterniha_sigs = {get_proxy_signature(l) for l in raw_patterniha_links if l}

    if raw_patterniha_links:
        untested_sample = random.sample(raw_patterniha_links, min(5, len(raw_patterniha_links)))
        for raw_link in untested_sample:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE:
                break
            cleaned = clean_link_params(raw_link)
            tag = f"🏁 Relay-{random.randint(1000, 9999)}"
            formatted_link = f"{cleaned.split('#')[0]}#{urllib.parse.quote(tag)}"
            untested_node = {
                'link': formatted_link,
                'tag': tag,
                'country': 'RELAY',
                'country_name': 'Relay',
                'speed': 0,
                'delay': 0,
                'health_score': 0
            }
            if add_to_eternity(untested_node, ignore_country_limit=True):
                selected.add(raw_link)
                selected.add(cleaned)

    patterniha_working = [
        n for n in eternity_candidates
        if get_proxy_signature(n['link']) in patterniha_sigs
        and get_proxy_signature(n['link']) not in selected_sigs
        and n.get('health_score', 0) > 0
        and n['link'] not in selected
    ]
    patterniha_working.sort(key=lambda x: -x.get('speed', 0))

    for n in patterniha_working[:10]:
        if len(eternity_nodes) >= ETERNITY_LIST_SIZE:
            break
        if n['link'] not in selected and get_proxy_signature(n['link']) not in selected_sigs:
            add_to_eternity(n, ignore_country_limit=True)

    for c in sorted(nodes_by_country.keys()):
        limit = COUNTRY_NODE_LIMITS.get(c, NODES_PER_COUNTRY)
        to_take = min(limit, len(nodes_by_country[c]))
        added = 0
        for n in nodes_by_country[c]:
            if added >= to_take:
                break
            if n['link'] not in selected and add_to_eternity(n):
                added += 1

    if reality_c < REALITY_TARGET_SIZE:
        for n in eternity_candidates:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE or reality_c >= REALITY_TARGET_SIZE:
                break
            if is_vless_reality(n['link']) and n['link'] not in selected:
                add_to_eternity(n)

    if len(eternity_nodes) < ETERNITY_LIST_SIZE:
        for n in eternity_candidates:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE:
                break
            if n['link'] not in selected:
                add_to_eternity(n)

    if iran_verified_records:
        verified_links_set = {item['link'] for item in iran_verified_records if 'link' in item}
        verified_tier = [p['link'] for p in eternity_nodes if p['link'] in verified_links_set]
        fallback_tier = [p['link'] for p in eternity_nodes if p['link'] not in verified_links_set]
        random.shuffle(fallback_tier)
        eternity_links = verified_tier + fallback_tier
    else:
        eternity_links = [p['link'] for p in eternity_nodes]
        random.shuffle(eternity_links)

    with open(ETERNITY_OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write('\n'.join(eternity_links))
    with open(ETERNITY_OUTPUT_BASE64_FILE, 'w', encoding='utf-8') as f: f.write(base64.b64encode('\n'.join(eternity_links).encode()).decode())
    
    # =========================================================
    # --- WRITE BEAUTIFUL STATS DASHBOARD (Stats.md) ----------
    # =========================================================
    
    proto_counts = {'VLESS': len(vless_out), 'VMess': len(vmess_out), 'Trojan': len(trojan_out), 'Shadowsocks': len(ss_out)}
    perf_brackets = {'⚡ Ultra Fast (>5 MB/s)': 0, '🚀 Fast (1-5 MB/s)': 0, '🐢 Slow (<1 MB/s)': 0}
    for n in conventional_nodes:
        if n['speed'] > 5_000_000: perf_brackets['⚡ Ultra Fast (>5 MB/s)'] += 1
        elif n['speed'] > 1_000_000: perf_brackets['🚀 Fast (1-5 MB/s)'] += 1
        else: perf_brackets['🐢 Slow (<1 MB/s)'] += 1

    country_dist = Counter([(n['country'], n['country_name']) for n in conventional_nodes])
    top_countries = country_dist.most_common(15)

    stats_md = f"""# 📊 Proxy Processing Statistics

## 📈 Pipeline Overview
- **Total Incoming Configs:** {total_incoming_nodes}
- **Failed Parsing (Invalid/Corrupted):** {parse_error_count} *(See `Logs/parse_errors.txt`)*
- **Successfully Tested by Xray:** {tested_count}
- **Dead Nodes (Timeout/0ms):** {tested_count - len(working_nodes)} *(See `Logs/dead_nodes.txt`)*
- **Working Nodes (Ping > 0):** {len(working_nodes)}
- **Iran In-Country Double-Verified Nodes:** {len(iran_verified_records)}

## 🗑️ Filtering & Deduplication
- **Duplicates Removed (Same IP/Port/ID):** {duplicates_removed}
- **UUID Spam Removed (Over {MAX_SAME_UUID} instances):** {spam_removed}
- **Final Unique & Safe Working Nodes:** {len(conventional_nodes)}

## 📁 Output Lists Sizes
- 💎 **Eternity:** {len(eternity_links)} configs
- 🌍 **Diversity:** {len(diversity_links)} configs
- 🛡️ **Resilience (Domain-Fronted):** {len(res_links)} configs
- 📦 **Full:** {len(full_links)} configs

---

## 📡 Protocol Distribution (Full List)
| Protocol | Count |
|----------|-------|
| **VLESS** | {proto_counts['VLESS']} |
| **VMess** | {proto_counts['VMess']} |
| **Trojan** | {proto_counts['Trojan']} |
| **Shadowsocks** | {proto_counts['Shadowsocks']} |

## 🚀 Speed Performance (Full List)
| Speed Bracket | Count |
|---------------|-------|
| ⚡ Ultra Fast (>5 MB/s) | {perf_brackets['⚡ Ultra Fast (>5 MB/s)']} |
| 🚀 Fast (1-5 MB/s) | {perf_brackets['🚀 Fast (1-5 MB/s)']} |
| 🐢 Slow (<1 MB/s) | {perf_brackets['🐢 Slow (<1 MB/s)']} |

---

## 🌍 Geographic Distribution (Top 15)
| Country | Count |
|---------|-------|
"""
    for (c_code, c_name), count in top_countries:
        flag = EMOJI.get(c_code, '🌐')
        display_name = COUNTRY_NAME_MAPPING.get(c_name, c_name)
        stats_md += f"| {flag} {display_name} | {count} |\n"

    with open('Stats.md', 'w', encoding='utf-8') as f:
        f.write(stats_md)
        
    print("\n✅ Saved Beautiful Stats Dashboard to Stats.md")

if __name__ == '__main__':
    process_and_save_results()
