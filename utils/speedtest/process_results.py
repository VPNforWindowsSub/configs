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
from collections import Counter
from datetime import datetime

# --- Configuration ---
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

# --- Domain Fronting Configuration ---
TRUSTED_DOMAINS = [
    "www.digitalocean.com", "npmjs.com", "registry.npmjs.org", "digitalocean.com", "hcaptcha.com", "www.w3.org",
    "getbootstrap.com", "ietf.org", "cloudflare.net", "nodejs.org", "cpanel.com", "npmjs.org",
    "www.icann.org", "hub.docker.com", "about.gitlab.com", "postman.com", "codepen.io", "unpkg.com",
    "raspberrypi.com", "readthedocs.org", "codeforces.com", "chat.openai.com", "platform.openai.com", "api.openai.com",
    "pingdom.com", "unicode.org", "openai.com", "character.ai", "bitdefender.com", "deepl.com",
    "1password.com", "crowdstrike.com", "nordpass.com", "www.bitwarden.com", "doi.org", "dashlane.com",
    "researchgate.net", "cambridge.org", "columbia.edu", "fao.org", "umich.edu", "acm.org",
    "udemy.com", "worldbank.org", "orcid.org", "asu.edu",
    "pnas.org", "dictionary.com", "ipcc.ch", "findlaw.com",
    "thesaurus.com", "scholastic.com", "ourworldindata.org", "medium.com", "moodle.org", "fiverr.com",
    "glassdoor.com", "csis.org", "www.medium.com", "iaea.org", "upwork.com", "hubspot.com",
    "thelancet.com", "vocabulary.com", "visa.com", "monday.com", "envato.com", "crunchbase.com",
    "elementor.com", "toptal.com", "squareup.com", "sage.com", "doodle.com", "alison.com",
    "patreon.com", "zoominfo.com", "www.patreon.com", "apollo.io", "tesla.services", "philips.com",
    "nestle.com", "spacex.com", "lilly.com", "pfizer.com", "techrepublic.com", "timeanddate.com",
    "appleinsider.com", "chess.com", "kraken.com", "gizmodo.com", "vizio.com", "pcworld.com",
    "warthunder.com", "cointelegraph.com", "trustwallet.com", "creativecommons.org", "investopedia.com", "www.okx.com",
    "crypto.com", "sourceforge.net", "roku.com", "indeed.com", "metamask.io", "jquery.com",
    "onetrust.com", "plesk.com", "ikea.com", "braze.com", "sedo.com",
    "fontawesome.com", "anydesk.com", "hostgator.com.br", "cloudinary.com", "jimdo.com", "garmin.com",
    "apnews.com", "tabelog.com", "trendyol.com", "economist.com", "hostinger.com", "plos.org",
    "remove.bg", "actu.fr", "rustdesk.com", "haberler.com", "namu.wiki", "jusbrasil.com.br",
    "mediaexpert.pl", "cloudflareclient.com", "ixl.com", "autotrader.co.uk", "ilmeteo.it", "bookmyshow.com",
    "travelandtourworld.com", "zedge.net", "typing.com", "id.me", "3bmeteo.com", "cardmarket.com",
    "dogdrip.net", "autoplius.lt", "dzexams.com", "auth0.com", "elegantthemes.com", "jamanetwork.com",
    "syosetu.org", "about.com", "typepad.com", "bootstrapcdn.com", "themeisle.com", "scan-manga.com",
    "runescape.wiki", "rfc-editor.org", "matterport.com", "yallakora.com", "curseforge.com", "jwplayer.com",
    "example.org", "blueapron.com", "cloudflarestorage.com", "earthlink.net", "generatepress.com", "pcmag.com",
    "flightradar24.com","lww.com", "scmp.com", "qz.com", "indiegogo.com",
    "webs.com", "cell.com", "bitnami.com", "ilo.org", "slashdot.org", "getyourguide.com",
    "quillbot.com", "podbean.com", "libsyn.com", "padlet.com", "medscape.com", "affirm.com",
    "register.com", "cookieyes.com", "fool.com", "laracasts.com", "redis.io", "joomla.org",
    "ko-fi.com", "hopkinsmedicine.org", "pravda.com.ua", "feedly.com", "nzherald.co.nz", "riskified.com",
    "allrecipes.com", "thingiverse.com", "identrust.com", "ably.io", "politico.eu", "nhl.com",
    "handelsblatt.com", "gamma.app", "flightaware.com", "tagesspiegel.de", "oneindia.com", "bb.com.br",
    "cnbcindonesia.com", "worldcat.org", "piano.io", "news24.com", "independent.ie", "buzzsprout.com",
    "g2.com", "domain.com", "verywellhealth.com", "takeaway.com", "prestashop.com", "routledge.com",
    "nefisyemektarifleri.com", "verywellmind.com", "capitaloneshopping.com", "visualcapitalist.com", "complianz.io",
    "producthunt.com", "grandviewresearch.com", "thenextweb.com", "marthastewart.com", "cyberark.com", "neilpatel.com",
    "travelandleisure.com", "arlo.com", "backblaze.com", "buffer.com", "snowflake.com", "blender.org",
    "japantimes.co.jp", "southernliving.com", "belkin.com", "atera.com", "myfitnesspal.com", "theregister.co.uk",
    "rae.es", "prweb.com", "tanium.com", "worldometers.info", "rome2rio.com", "khaleejtimes.com",
    "sibforms.com", "eatingwell.com", "atlasobscura.com", "hindawi.com", "reclameaqui.com.br", "vinted.com",
    "blinkit.com", "directadmin.com", "biorxiv.org", "doxygen.nl", "meteoblue.com", "dynadot.com",
    "pressreader.com", "zopim.com", "royalsocietypublishing.org", "moma.org", "thebalancemoney.com", "thespruce.com",
    "telus.com", "gamebanana.com", "thoughtco.com", "bleepingcomputer.com", "liquidweb.com",
    "benzinga.com", "tutsplus.com", "revolut.com", "jooble.org", "humblebundle.com", "cash.app",
    "oanda.com", "clutch.co", "router-network.com", "pipedrive.com", "bootstrapmade.com", "techopedia.com",
    "iucn.org", "hostmonster.com", "ethereum.org", "kinsta.cloud", "sendinblue.com", "homeadvisor.com",
    "typingtest.com", "matrix.org", "ivanti.com", "foreignaffairs.com", "vestiairecollective.com", "trezor.io",
    "streamlabs.com", "simonandschuster.com", "linksys.com", "workable.com", "investors.com", "microworkers.com",
    "artsy.net", "veed.io", "interestingengineering.com", "css-tricks.com", "lifehack.org", "authorize.net",
    "futurelearn.com", "marketsandmarkets.com", "masterclass.com", "skillshare.com", "gameloop.com", "matillion.com",
    "karger.com", "jumpcloud.com", "adapty.io", "thehackernews.com", "dzone.com", "templatemonster.com",
    "standardnotes.com", "purchasely.io", "idrlabs.com", "pngtree.com", "anyflip.com", "trueachievements.com",
    "ultahost.com", "equifax.com", "activehosted.com", "plyr.io", "pathofexile.com", "wemod.com",
    "gulfnews.com", "law.com", "asda.com", "rawstory.com", "siliconcanals.com", "futura-sciences.com",
    "webassign.net", "insidehighered.com", "sphinx-doc.org", "nexcess.net", "dignitymemorial.com", "helpguide.org",
    "bscscan.com", "edublogs.org", "readwrite.com", "learncbse.in", "twword.com", "pdfcoffee.com",
    "teacherease.com", "teamstoday.com", "bizimhesap.com", "mattermost.com", "cdnfonts.com", "blockchain.com",
    "fireeye.com", "web.com", "pingdom.net", "spring.io", "jsfiddle.net", "linear.app",
    "apachehaus.com", "cloudlinux.com", "gtmetrix.com", "cdnjs.com", "configcat.com", "linux.org",
    "radar.io", "wp-rocket.me", "avastbrowser.com", "interserver.net", "sourceforge.io", "maxmind.com",
    "bitmovin.com", "netcraft.com", "siteorigin.com", "yarnpkg.com", "usenix.org", "jquery.org",
    "bugfender.com", "winudf.com", "uniswap.org", "higgsfield.ai", "suno.ai", "activecampaign.com",
    "weglot.com", "on24.com", "uipath.com", "blibli.com", "retailmenot.com", "volusion.com",
    "liebherr.com", "reverb.com", "whatfix.com", "zeffy.com", "donorbox.org", "bloomreach.com",
    "aqara.com", "cal.com", "getsitecontrol.com", "feefo.com", "getclicky.com", "eneba.com",
    "opencart.com", "bufferapp.com", "cybersource.com", "mypertamina.id", "mynewsdesk.com", "aweber.com",
    "grofers.com", "tidio.co", "dexcom.com", "novartis.com", "chime.com", "lendingtree.com",
    "988lifeline.org", "pluralsight.com", "avaaz.org", "ncsl.org", "usgbc.org", "amnh.org",
    "commonsensemedia.org", "rsf.org", "psychiatry.org", "doaj.org", "leo.org", "altmetric.com",
    "uwa.edu.au", "stonybrook.edu", "gatesfoundation.org", "mind.org.uk", "plannedparenthood.org",
    "taylorandfrancis.com", "quran.com", "peta.org", "delfi.ee", "nolo.com", "themoscowtimes.com",
    "informationweek.com", "geekwire.com", "meduza.io", "petapixel.com", "businessinsider.de", "designboom.com",
    "deseret.com", "sme.sk", "computerweekly.com", "parsec.app", "wego.com", "plarium.com",
    "open-meteo.com", "newspapers.com", "commbank.com.au", "basketball-reference.com", "lexology.com", "tasteofhome.com",
    "delfi.lv", "thehindubusinessline.com", "talabat.com", "newindianexpress.com", "nv.ua", "wiwo.de",
    "testmy.net", "denik.cz", "webopedia.com"
]

RESILIENCE_THEMES=["🌐 Grid","🏹 Barton","👻 Roach","🌙 Twilight","⚡ Zenitsu","🕸️ Shadow","🦅 Raptor","🏔️ Ridge","🔥 Inferno","🦁 CapeTown","⚔️ Zoro","🌙 Lunar","✈️ Spitfire","🗡️ Dagger","👻 Rayman","📡 Bandwidth","📡 Antenna","🌿 Amazon","🦊 MetaMask","⚖️ Gravity","🦇 Gotham","🗡️ Cloud","🧙 Dumbledore","👽 Stitch","🌲 Taiga","🏹 Hanzo","🕸️ Node","🌟 Zenith","🎤 Billie","☯️ Yin","🔫 Jules","🚀 Normandy","🕶️ JayZ","🐰 Bunny","🚢 Nelson","🌫️ Vapor","🦍 Gorilla","🖼️ NFT","⛏️ Steve","🏖️ Miami","📞 Tardis","🦾 Cyborg","🎩 Lincoln","☄️ Comet","🚘 CJ","🔪 Ripper","🦂 Scorpion","🏌️ Woods","👺 Ronin","🔥 Scorpion","🏇 Attila","🏝️ Bali","🔭 Optics","🥊 Ryu","🦖 Godzilla","🐰 Bugs","🕵️‍♀️ Kim","🧬 Helix","😈 Daemon","⚡ Kinetic","👾 Virus","🎤 Abel","🙏 Cleric","🌋 Tremor","📡 Beacon","☀️ Summer","🧩 Enigma","🌿 Jade","🌑 Blackhole","🚪 Gateway","📡 Proxy","🍔 Burger","☄️ Flare","🤠 Morgan","🛡️ Chief","🔶 Amber","⚖️ Anubis","🔭 Galileo","🧊 Sid","🌘 Eclipse","🏀 Bird","🏁 McLaren","🌌 Jupiter","🦅 Phoenix","🦾 Stark","🌌 Gurren","❄️ Frost","🚬 Noir","⚙️ Inertia","🔫 Flintlock","⚪ Silver","📡 Sonar","🚀 Soyuz","🧥 Armani","🛡️ Bastion","🤖 Daft","💥 Fission","🌑 MoonKnight","🔮 Oracle","🍸 Bond","🕷️ Parker","🌠 Asteroid","🍸 Martini","⚡ Fiber","🦅 Scout","🌑 Raven","🤖 C3PO","🧪 Chemistry","🐂 Minotaur","🌬️ Chicago","🚀 Saturn","🎹 Moog","♌ Leo","🌌 Fractal","🦾 MegaMan","🧘 Zen","🏹 Quiver","🏰 Gondor","🐈 Catwoman","🛡️ Rogers","💍 Crystal","🚬 Spike","🦄 Unicorn","🕌 Dubai","📓 Light","🤖 Gundam","🦅 Hawk","🍷 Speakeasy","🧵 Dior","🏛️ Aurelius","🐶 Inuyasha","🧬 Augment","🦍 Tarzan","🧚‍♀️ Tinkerbell","🦍 Beast","🌌 Mercury","🦅 Horus","🥞 Pancake","♔ King","❄️ Isotope","🏎️ Ferrari","🦍 Caesar","🦏 Rhinoceros","🤖 Shinji","🦅 Griffin","🍄 Mario","👑 Peach","💣 Claymore","🌳 Druid","✈️ Boeing","🎹 Chopin","🐉 Spyro","🐺 Geralt","✨ Aura","🍣 Sushi","🌐 Polygon","♍ Virgo","🎯 Darts","🦁 Simba","🕶️ Cypher","🌉 SF","🥊 Ken","🎸 Punk","🕵️ Stealth","🏎️ M3","🦅 Skyline","🌿 Solstice","🔴 Asuka","👦 Ben10","🎸 Zeppelin","💦 Aqua","⚔️ Jedi","🌅 Dawn","📉 Bear","⛵ Columbus","🦾 Genji","⚔️ Halberd","🚀 Moon","⚾ Ruth","🦒 Giraffe","♖ Rook","🍎 Newton","🦦 Otter","🌊 Hydro","🌌 Tatooine","🏎️ Veyron","💎 Onyx","🎀 Swift","✨ Topaz","🔨 Warhammer","🦖 Jurassic","🐷 Porky","💻 Matrix","🏎️ Leclerc","🕵️ Poirot","⚙️ Macro","🤖 AI","🌠 Orion","⚪ Pearl","🏀 Shaq","🔴 Garnet","👁️ Cyclops","✨ Quasar","🏀 Magic","🦁 Lion","🦁 Lannister","⛄ Snow","🌕 Moon","🎧 Skrillex","🥊 Drago","🔗 Ledger","💣 C4","🐉 Shenron","🎤 Mercury","📡 Radar","💻 Windows","🦇 Alucard","🏈 Manning","🌑 Pulsar","⚔️ Sora","🚗 Tesla","⚡ Speedster","🏐 Shoyo","🏛️ Sparta","🔥 Hades","🎸 Jagger","🕯️ Ritual","🛡️ Vanguard","🐼 Po","📏 Zenith","🛡️ Wakanda","⚡ Bolt","🍹 Mojito","💼 Vuitton","🍂 Autumn","🦇 Batgirl","🤖 Bender","⚡ ACDC","🌀 Karma","🦅 Hawkeye","⚔️ Maximus","🛡️ Leonidas","🐍 Kobe","⚔️ Sephiroth","🥊 Ali","🚙 Wrangler","💣 Grenade","🎸 Slash","✍️ Plato","📜 Aristotle","♏ Scorpio","🔥 Wildfire","🧽 Sponge","♑ Capricorn","🔗 Mesh","🐉 Targaryen","☁️ Cloud","🌀 Flux","🍀 Luck","🦇 Belmont","🎩 Gatsby","⚡ Static","🐍 Shelby","⚡ Sith","🐎 Knight","🕶️ Gojo","🐪 Camel","🗡️ Sasuke","🎯 Ballistic","❄️ Tundra","🧿 Ward","🔢 Algebra","🌟 Bowie","⚔️ Kenshin","🌌 Cosmos","🦅 Napoleon","✍️ Socrates","⚽ Henry","🖥️ Mainframe","🎱 Billiards","🍕 Milan","♈ Aries","🗽 NY","🌭 Dog","🦇 Nightwing","📜 Washington","🏹 Crossbow","🦅 Alexander","🌳 Jungle","🏀 Curry","🌟 Madonna","🐿️ Squirrel","🔱 Curry","🐺 Direwolf","👑 Drake","🛡️ Troy","🔥 Loki","👁️ Vision","🏝️ Island","🔌 Jack","🌌 Void","🏈 Brady","🔬 Mutation","💣 Torpedo","🌀 Cyclone","🚀 Shepard","♗ Bishop","🎧 Tiesto","⚽ Mbappe","🥚 Egg","💎 Tiffany","🏙️ Berlin","🥊 McGregor","⚔️ Berserker","🛹 Skateboard","💨 Sonic","🌌 Galaxy","🌿 Leon","♟️ Checkmate","🟥 Carnage","🦅 Hermes","🚀 Rover","🀄 Mahjong","🚁 Drone","🍩 Homer","🌐 Nexus","🌊 Tsunami","☔ Seattle","🔨 Hephaestus","🦈 Shark","🔫 Master","🦹‍♂️ Lex","🗡️ Guts","🛹 Mullen","🏰 Madrid","🌌 Pluto","🎾 Federer","🤖 WallE","🔥 Pyromancer","🎩 Mobster","🌑 NewMoon","🦸‍♂️ Incredible","🔊 Echo","🔨 Thor","🛳️ Cruise","🔵 Cobalt","🌋 Mustafar","⛏️ Miner","📐 Geometry","🌹 Nobara","🛰️ Sputnik","🗡️ Kirito","❄️ SubZero","🌿 Mantis","☀️ Apollo","✈️ Airbus","⚔️ Deadpool","🐉 Dovahkiin","♋ Cancer","🏎️ Senna","🐻 Grizzly","🌫️ Fog","🎤 Dua","💀 Diablo","💨 Gale","🧇 Waffle","😈 Dante","⚙️ Steel","🏹 Cupid","🛰️ Hubble","♠️ Syndicate","🦅 Robin","🎤 Ariana","🔵 Aquamarine","👁️ Strange","💣 Missile","☯️ Yang","🦂 Cobra","🧲 Magneto","💾 Cache","🐉 Smaug","🏍️ Ducati","⌚ Omega","🍵 Matcha","🍁 Fall","🌌 Kamina","🕴️ BabaYaga","✨ Opal","🔱 Trident","💥 Blast","🏎️ Hamilton","🐎 Mustang","💀 Punisher","🦈 Jaws","🌑 Midnight","👑 Caesar","☕ Mocha","🌬️ Breeze","👁️ Retina","🏎️ Schumacher","🌌 Venus","💎 Zircon","☄️ Meteor","🦊 Naruto","🌪️ Storm","🔭 Copernicus","💊 Neo","👨‍🚀 Astronaut","💾 Byte","🧪 Pinkman","⛵ Titanic","💎 Cartier","🌠 Halley","🏎️ AMG","🚁 Chinook","🌋 Crater","🔫 Tommy","🔥 Flint","☀️ Solar","🦇 Wayne","🦅 Eagle","🏔️ Alps","💻 Root","🔥 Firewall","📏 Kelvin","🧊 Frostbite","🔮 Magic","🏦 Vault","🌮 Taco","🎈 Zeppelin","🛡️ VPN","🐉 Mushu","🌀 Vortex","⚽ Zidane","🌟 Kirby","🔥 Roy","☕ Latte","🏎️ Supra","🍰 Cake","🤠 Indy","📐 Matrix","❤️ Heart","💥 Jinx","🎾 Nadal","☁️ AWS","🌙 Night","⚔️ Wilson","🗼 Tokyo","🦊 Fox","👽 Alien","💀 Necromancer","👑 Nefertiti","🧬 DNA","☀️ Sun","🚂 Loco","😈 Daredevil","🤺 Zorro","🏍️ Kaneda","🏹 Arrow","📡 Server","🍺 Stout","🌇 Dusk","🎮 Chief","🛸 Romulan","🧪 Catalyst","⚾ Jeter","⚙️ Kernel","⚔️ Glaive","🎹 Synth","💼 Goodman","💥 Bakugo","🦥 Sloth","🛡️ Aegis","⚛️ Quantum","⛏️ Dwarf","🌙 Selene","🏖️ Ibiza","📈 Vector","⛏️ Coal","🎲 Casino","🧚‍♂️ Elf","🦖 Rex","🖖 Spock","👻 Megumi","🧫 Cell","🐉 Beijing","👑 Cleopatra","💊 Overdose","👑 Victoria","🦋 Paramore","📜 Curse","🧊 Frost","🏹 Bow","🔫 Solo","🥁 Snare","📜 Churchill","🛡️ Naofumi","👊 JoJo","🌲 Forest","⚖️ Osiris","😈 Doom","🏎️ F1","👜 Prada","🔭 Parallax","🧩 Scrabble","🐺 Stark","🚗 Civic","👾 Samus","🌊 Leviathan","🐺 Hati","⚪ Ivory","💣 Mine","🏎️ Kart","👗 Gucci","📷 Kodak","⚛️ Electron","🛡️ Shield","🔋 Battery","🥊 Mayweather","🤖 T800","⚡ Killua","🐰 NewJeans","🍷 Cartel","🥖 Baguette","🗼 Paris","🔥 Fusion","🗡️ Machete","⚙️ Panzer","🥊 Tyson","♙ Pawn","🌬️ Wind","🏔️ Denver","⚽ Neymar","🌌 Asgard","🛡️ Buckler","🤖 Cylon","🌋 Magma","⚡ Tempest","💥 Tetsuo","🦛 Hippo","🐭 Jerry","☀️ Heatwave","🌊 Ocean","🧿 Zenith","🐉 Goku","🐧 Linux","🔺 Apex","⚔️ Raiden","🦅 Ezio","🗡️ Broadsword","🛸 Voyager","🏙️ Zion","🎾 Djokovic","🌌 Horizon","🦇 Dracula","💿 Platinum","🐱 Tom","🐘 Manny","🌌 Thanos","🦘 Kangaroo","🥊 Rocky","🏙️ Gotham","🔭 Scope","🦋 Shinobu","🧥 Nomad","🛡️ Spartacus","🏦 Defi","🕷️ Widow","🌍 Orbit","✨ Nebula","🕊️ Hawks","🎼 Beethoven","🐰 Rabbit","💨 Aero","💍 Gollum","♎ Libra","🏇 Genghis","🔮 Quartz","🐍 Viper","🎧 Guetta","🃏 Poker","🌸 Seoul","🦆 Donald","🦉 Minerva","❄️ Moscow","🧊 Todoroki","🐉 Dragon","🧠 Neural","🌱 Bloom","🍩 Donut","🚁 Apache","🐗 Pumbaa","♕ Queen","🌌 MilkyWay","🌌 Klingon","🐕 Doge","🌌 Supernova","🐎 Aragorn","🏎️ Falcon","☀️ Morning","🌸 Sakura","🐅 Tiger","🎤 Freddie","🦡 Badger","🛡️ Zelda","⚔️ Levi","🔑 Token","☕ Espresso","🏛️ Rome","🤠 Woody","🎤 Kendrick","🎭 Rio","🐉 Drogo","🐍 Slytherin","🚗 Furiosa","⚙️ Logic","🎸 Cobain","🐺 Skoll","⚡ Tracer","⚡ Flash","🐉 Bowser","🐴 Donkey","🎭 Mirage","❄️ Blizzard","🐺 Logan","🏂 White","🌘 Equinox","🧹 Nimbus","🔭 Astro","🔫 Vash","🚬 Detective","☔ Monsoon","😈 Krampus","🏍️ Harley","💻 Zero","🌃 Skyline","🎙️ Sinatra","🌌 Sky","🖥️ Monitor","🗡️ Katana","🍻 Brew","🔫 Vincent","⚔️ Tanjiro","🦅 Falco","🔥 Torch","🌡️ Celsius","🔫 Magnum","🐻 Bear","🔴 Ruby","⚛️ Neutron","🛸 UFO","🏹 Rambo","👾 Glitch","🏜️ Canyon","☄️ Meteorite","🌆 Metropolis","🛥️ Stealth","🔒 Crypto","🦅 Garuda","🍖 Sanji","🚜 Tractor","🔬 Proton","🚪 Portal","♠️ Spade","🦍 Kong","🦸‍♂️ KalEl","🌐 IP","🍪 Cookie","✨ Stardust","💘 IVE","🪄 Merlin","🏀 LeBron","🔥 Illidan","⚡ Storm","🌊 Surge","🖥️ Host","❄️ Arthas","🛸 Enterprise","🗡️ Rogue","❄️ Winter","🗡️ Marth","🚲 BMX","🛥️ Yacht","☀️ Helios","🎧 Kanye","🔷 Sapphire","🚪 Narnia","🔫 Musket","⚔️ Spear","🦝 Rocket","🔫 Croft","🎯 Wick","🏜️ Oasis","🦉 Athena","🐘 Elephant","👁️ Fremen","🏎️ GTR","🌌 Andromeda","⏳ Chronos","🗻 Fuji","🖖 Vulcan","⚔️ Wallace","👻 Phantom","🚀 Concorde","🎼 Mozart","🥪 Sub","♉ Taurus","🐈 Sylvester","♊ Gemini","⚔️ Link","🤖 Claptrap","♒ Aquarius","🎸 Gibson","🦊 Kurama","⬛ Borg","🐘 Hannibal","🦾 Jax","💥 Oppenheimer","🧠 Brain","🏢 McClane","🧟‍ Rick","🤡 Joker","⚙️ Chrome","🦝 Raccoon","🐉 Toothless","🐉 Triad","🥩 Wagyu","🐭 Mouse","🔨 Odinson","🌐 Ping","🐍 Snake","📓 Ryuk","👽 Predator","🗡️ Snow","🔌 Cable","🏂 McMorris","🌌 Dimension","🦅 Raven","⚔️ Mandalorian","🌊 Poseidon","⚡ Socket","🏔️ Avalanche","⛄ Olaf","🔗 Blockchain","🥊 ChunLi","♓ Pisces","🕶️ Snoop","💻 Cipher","🐎 Rohan","🍫 Gump","🦇 Gargoyle","👑 Richard","⚙️ RAM","🦾 Malware","🔭 Einstein","♐ Sagittarius","🐆 Jaguar","🐺 Coyote","🥊 Pacquiao","🧝‍♀️ Galadriel","🏀 Jordan","🐪 Cairo","⚽ Maradona","🧸 Pooh","🛡️ Kevlar","🏎️ Bugatti","🍁 Toronto","🚀 Ripley","🦨 Skunk","🍷 Lecter","😈 Lucifer","🚢 Davy","🌐 Protocol","⚔️ Saladin","♘ Knight","🏜️ Dune","🌑 Omen","🎸 Elvis","🔑 RSA","⚓ Dreadnought","👹 Shrek","🍷 Merlot","⚔️ Valkyrie","✈️ Maverick","🦅 Pegasus","🦇 Morrigan","🕉️ Om","🎸 Metallica","🌌 Mars","⛏️ Gordon","🕰️ Paradox","🌋 Volcano","🔱 Odin","📉 Entropy","🔩 Tungsten","🐦 Tweety","🧱 Clay","🍏 Apple","⚔️ Mulan","🌳 Groot","⚙️ Marcus","⚙️ Edward","🌌 Saturn","🔥 Ember","❄️ Yeti","🧬 Gene","🚗 Brian","🦉 Hedwig","🏎️ Verstappen","🎸 Sheeran","💥 Nova","👜 Birkin","🦅 Kent","🍷 Shiraz","🏰 Hogwarts","🗡️ Arya","🧪 Plasma","🍃 Totoro","🐙 Kraken","🍷 Dionysus","💾 Drive","🌋 Mordor","🌧️ Rain","⚓ Freeman","🐉 Yakuza","🌸 Spring","🕵️ L","💎 Hodl","🛡️ Kite","🛡️ Carbon","🕶️ Eazy","⛰️ Mountain","📊 Calculus","🦇 Aventador","🐗 Inosuke","🛸 Apollo","👑 Jackson","⚽ Ronaldo","💻 Pixel","⚡ Switch","🏎️ Furiosa","🦆 Daffy","🌾 Demeter","🦊 StarFox","☀️ Ra","🎸 Fender","🎣 Gon","⚡ Potter","🎰 Vegas","🎩 Corleone","🐺 KaerMorhen","🗡️ Joan","🎤 Adele","🌐 Web","🤖 2B","🏎️ Dom","👊 Baki","🌟 Rihanna","🐱 Puss","⚔️ Vader","🎩 Shelby","🏍️ Akira","✨ Halo","🐼 Panda","🕸️ Darknet","📜 SunTzu","🌉 London","🤖 R2D2","🎸 Nirvana","🦴 Spine","🌌 Surfer","🌙 Hunter","👊 Monk","🏰 Citadel","🥓 Bacon","🛰️ Webb","🕶️ Mirage","⛵ Magellan","🏙️ Neon","☀️ Daylight","🐶 Scooby","🌊 Abyss","🏞️ River","🐾 Cerberus","💎 Diamond","🌊 Giyu","🗡️ Ichigo","🌴 LA","🌪️ Typhoon","⚡ Shazam","🧲 Electromagnet","🧞 Genie","🎤 Eminem","🏌️ McIlroy","🚦 Router","🐈 BlackCat","🔬 Biology","⛓️ Titanium","🕵️ Bourne","🧀 Cheese","🦍 Donkey","🥯 Bagel","🐆 Panther","🐭 Mickey","⚡ Kakashi","🦾 Cable","👹 Slayer","💀 Hel","🧪 Heisenberg","✨ Nirvana","🦆 Scrooge","🍄 Luigi","🍟 Fries","💊 Pill","💻 Turing","⚽ Messi","📸 Leica","⛈️ Thunder","🏹 Ranger","🚪 Port","🎨 DaVinci","🖤 PinkFloyd","🦇 Bat","⚡ Spark","👑 Tupac","🧞‍♂️ Aladdin","🦾 Bionic","🎧 Avicii","🐨 Koala","🍕 Slice","🛡️ Porsche","🌵 Desert","🥃 Bourbon","🐍 Medusa","⛵ Galleon","🏹 Artemis","🖤 Obsidian","🎲 Roulette","🗡️ Brutus","💉 Serum","⚔️ Pike","⚽ Beckham","⚙️ Docker","🥂 Champagne","🎾 Serena","🎸 Hendrix","🏎️ McQueen","🌨️ Hail","🗡️ Scimitar","🛡️ Paladin","⚡ Zeus","🧸 Ted","🍫 Cacao","🔌 Node","🕳️ Wormhole","🐯 Diego","🔵 Lapis","🛹 Hawk","🦈 Orca","🦴 Skull","🧬 Chromosome","🌌 Aether","👁️ Karma","🧚‍♀️ Freya","✨ Spice","🏊 Phelps","🕵️ Holmes","🖤 Blackpink","🏴‍☠️ Sparrow","⚔️ Ragnar","🧱 Thing","💍 Ring","🔊 Sonic","💃 Tango","🎹 Mozart","⌚ Rolex","🔫 Doomguy","🦁 Mufasa","⚽ Pele","🥐 Croissant","🐍 Jormungandr","⛓️ Kratos","☮️ Peace","🐺 Wolf","🚗 McFly","🐢 Raphael","🏹 Katniss","🐺 Jon","🕵️ Assassin","🖥️ Terminal","🎲 Monopoly","🎶 Bard","🗡️ Yuji","🔌 Motoko","👑 Charlemagne","🌍 Atlas","🏍️ Chopper","🌟 Jotaro","🧟 Jill","🥨 Pretzel","🦞 Boston","🕊️ Gandhi","🧊 Elsa","👊 Saitama","📈 Bull","🗡️ Rapier","🦅 Sphinx","🔫 Sniper","🏜️ Sahara","🌌 Neptune","🌠 ShootingStar","🔮 Mystic","🦓 Zebra","🔥 Hestia","🌌 Quill","💡 Tesla","✈️ Blackbird","🚬 Draper","🛡️ Arthur","🌀 String","💀 Reaper","🦅 Gryffindor","🏔️ Everest","🦾 Alphonse","⚽ Ronaldinho","📡 Uplink","🗝️ Key","🕷️ Morales","🚀 Falcon9","⌨️ Hacker","💠 Vertex","🔫 Price","🦅 Falcon","🐺 Fenrir","🎭 Persona","🚀 Buzz","🛡️ Ares","🎩 Wonka","🕸️ Venom","🚬 Cigar","🍖 Luffy"]

CF_PORTS = [443, 2053, 2083, 2087, 2096, 8443]

# --- Parameters ---
ETERNITY_LIST_SIZE = 165
VLESS_TARGET_PERCENT = 0.55
VLESS_TARGET_SIZE = math.ceil(ETERNITY_LIST_SIZE * VLESS_TARGET_PERCENT)
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
    'TR': 4
}

# Maximum allowed nodes that share the exact same UUID/Password.
MAX_SAME_UUID = 5 

def is_ip_address(address):
    if not isinstance(address, str):
        return False
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address))

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
            server, port_str = server_port.split(':', 1)
            return f"{server}:{port_str}:{userinfo}"

        elif link.startswith('vmess://'):
            b64 = link.replace("vmess://", "").split('#')[0]
            b64 += '=' * (-len(b64) % 4)
            b64 = b64.replace('-', '+').replace('_', '/')
            j = json.loads(base64.b64decode(b64).decode('utf-8', errors='ignore'))
            server = j.get('add', 'unknown')
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

def create_resilience_clone(node, theme_name):
    link = node.get('link', '')
    ip = node.get('ip', '')
    if not is_cloudflare_ip(ip): return None

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
                
            if port not in CF_PORTS: return None
                
            if '#' in query_name: query, name = query_name.split('#', 1)
            else: query, name = query_name, "Proxy"
                
            params = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
            net = params.get('type', 'tcp')
            sec = params.get('security', 'none')
            
            if sec != 'tls': return None
            if net not in ['ws', 'grpc', 'httpupgrade']: return None
            
            if 'sni' not in params or not params['sni']: params['sni'] = server
            if net in ['ws', 'httpupgrade', 'xhttp']:
                if 'host' not in params or not params['host']: params['host'] = server
                    
            server = trusted_domain
            new_query = urllib.parse.urlencode(params)
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
            if net not in ['ws', 'grpc', 'httpupgrade']: return None
                
            original_add = str(j.get('add', ''))
            if 'sni' not in j or not j['sni']: j['sni'] = original_add
            if net in ['ws', 'httpupgrade', 'xhttp']:
                if 'host' not in j or not j['host']: j['host'] = original_add
                    
            j['add'] = trusted_domain
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

    unique_servers = list(set([node.get('server', '') for node in working_nodes if node.get('server')]))
    resolved_ips = {}
    print(f"Resolving {len(unique_servers)} unique domains concurrently...", flush=True)

    def resolve_domain(server):
        if is_ip_address(server): return server, server
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
        except: pass
            
        burned = ['workers.dev', 'trycloudflare.com', 'pages.dev', 'eu.org', '.cc', 'multiplydose', 'calmloud', 'ignitelimit', 'gossipglove', 'calmlunch', 'creationlong']
        if any(b in sni for b in burned) or '/assignment' in path: score -= 20
        if port != 443 and port in CF_PORTS: score += 15
        if '.ir' in sni or sni.endswith('.ir.'): score += 25
        return score

    resilience_candidates.sort(key=calculate_iran_score, reverse=True)
    resilience_nodes = []
    theme_pool = list(RESILIENCE_THEMES)
    random.shuffle(theme_pool)

    for node in resilience_candidates:
        if len(resilience_nodes) >= 1000: break
        if not theme_pool:
            theme_pool = list(RESILIENCE_THEMES)
            random.shuffle(theme_pool)
            
        current_theme = theme_pool.pop(0)
        theme_name = f"{current_theme}-{random.randint(1000, 9999)}"
        
        cloned = create_resilience_clone(node, theme_name)
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

    # Keep ALL nodes for Resilience, Diversity, and Full lists!
    final_nodes = all_processed_nodes

    print("\n--- Generating Diversity List ---")
    diversity_nodes_by_country = {}
    for node in final_nodes:
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

    conventional_nodes = [p for p in final_nodes if p['country'] not in BLOCKED_COUNTRIES]
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

    print("\n--- Generating Eternity List ---")
    
    # Apply UUID Spam Filter strictly to Eternity candidates
    uuid_counts_eternity = {}
    eternity_candidates = []
    for node in conventional_nodes:
        uuid = get_uuid(node['link'])
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
            if c not in nodes_by_country: nodes_by_country[c] = []
            nodes_by_country[c].append(node)

    for c in nodes_by_country:
        nodes_by_country[c].sort(key=lambda x: (0 if x['link'].startswith('vless://') else 1, -x['speed']))

    eternity_nodes = []
    selected = set()
    vless_c = 0
    c_counts = {}

    def add_to_eternity(n):
        nonlocal vless_c
        c_code = n['country']
        max_allowed = COUNTRY_MAX_LIMITS.get(c_code, 999)
        if c_counts.get(c_code, 0) >= max_allowed: return False
            
        eternity_nodes.append(n)
        selected.add(n['link'])
        c_counts[c_code] = c_counts.get(c_code, 0) + 1
        if n['link'].startswith('vless://'): vless_c += 1
        return True

    for c in sorted(nodes_by_country.keys()):
        limit = COUNTRY_NODE_LIMITS.get(c, NODES_PER_COUNTRY)
        to_take = min(limit, len(nodes_by_country[c]))
        added = 0
        for n in nodes_by_country[c]:
            if added >= to_take: break
            if n['link'] not in selected and add_to_eternity(n): added += 1

    if vless_c < VLESS_TARGET_SIZE:
        for n in conventional_nodes:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE or vless_c >= VLESS_TARGET_SIZE: break
            if n['link'].startswith('vless://') and n['link'] not in selected: add_to_eternity(n)

    if len(eternity_nodes) < ETERNITY_LIST_SIZE:
        for n in conventional_nodes:
            if len(eternity_nodes) >= ETERNITY_LIST_SIZE: break
            if n['link'] not in selected: add_to_eternity(n)

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
