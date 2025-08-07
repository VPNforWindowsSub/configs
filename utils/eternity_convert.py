import re
import yaml
import json
import time
import os
import requests

from sub_convert import sub_convert
from subs_function import subs_function
from list_merge import sub_merge

Eterniy_base_file = './EternityBase'
Eterniy_file = './Eternity' # This is now only used for the backup function
Eternity_yml_file = './Eternity.yml'
readme = './README.md'
log_file = './LogInfo.txt'

provider_path = './update/provider/'
update_path = './update/'

sub_list_json = './sub/sub_list.json'

config_file = './update/provider/config.yml'

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def substrings(string, left, right):
    try:
        value = string.replace('\n', '').replace(' ', '')
        start = value.index(left)
        end = value[start:].index(right) + len(value[:start])
        final_value = value[start:end].replace(left, '')
        return final_value
    except ValueError:
        return ""

def eternity_convert(config_path, output_path):
    # Read the raw links of all successfully tested nodes from the local EternityBase file.
    with open(Eterniy_base_file, 'r', encoding='utf-8') as f:
        base_content = f.read()

    # Convert the raw links into the Clash YAML format by POSTing them to the local subconverter.
    subconverter_url = "http://127.0.0.1:25500/sub?target=clash&udp=false"
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    try:
        response = requests.post(subconverter_url, data=base_content.encode('utf-8'), headers=headers, timeout=60)
        response.raise_for_status()
        all_provider_yaml = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error contacting subconverter: {e}")
        return

    # Load the generated YAML into a Python object
    try:
        provider_data = yaml.safe_load(all_provider_yaml)
        if not provider_data or 'proxies' not in provider_data:
            print("Could not parse proxies from subconverter output.")
            return
        proxies_list = provider_data['proxies']
    except yaml.YAMLError as e:
        print(f"Error parsing YAML from subconverter: {e}")
        return

    # Load the speed test log file
    try:
        with open(log_file, 'r') as log_reader:
            log_lines = log_reader.readlines()
    except FileNotFoundError:
        log_lines = []

    # Combine proxy data with speed test results
    for i, proxy in enumerate(proxies_list):
        if i < len(log_lines):
            speed = substrings(log_lines[i], "avg_speed:", "|")
            proxy['name'] = f"{proxy.get('name', '')} | {speed}"

    # Load the main clash config template
    with open(config_path, 'r', encoding='utf-8') as config_f:
        config = yaml.safe_load(config_f.read())

    # Create the list of proxy names for the proxy groups
    all_name = [p['name'] for p in proxies_list]

    proxy_groups = config.get('proxy-groups', [])
    full_size = len(all_name)
    part_size = full_size // 4
    
    for rule in proxy_groups:
        if rule.get('proxies') is None:
            if "Tier 1" in rule['name']:
                rule['proxies'] = all_name[0:part_size]
            elif "Tier 2" in rule['name']:
                rule['proxies'] = all_name[part_size:part_size*2]
            elif "Tier 3" in rule['name']:
                rule['proxies'] = all_name[part_size*2:part_size*3]
            elif "Tier 4" in rule['name']:
                rule['proxies'] = all_name[part_size*3:full_size]

    # Build the final configuration dictionary
    config['proxies'] = proxies_list
    config['proxy-groups'] = proxy_groups

    # Write the final, complete Eternity.yml file
    config_yaml = yaml.dump(config, default_flow_style=False, sort_keys=False,
                              allow_unicode=True, width=750, indent=2, Dumper=NoAliasDumper)

    with open(output_path, 'w+', encoding='utf-8') as f:
        f.write(config_yaml)
    print(f"Successfully generated final config at {output_path}")

def backup(file):
    try:
        t = time.localtime()
        date = time.strftime('%y%m', t)
        date_day = time.strftime('%y%m%d', t)

        with open(file, 'r', encoding='utf-8') as file_eternity:
            sub_content = file_eternity.read()

        os.makedirs(f'{update_path}{date}', exist_ok=True)
        txt_dir = os.path.join(update_path, date, f'{date_day}.txt')
        
        with open(txt_dir, 'w', encoding='utf-8') as f:
            f.write(sub_convert.base64_decode(sub_content))
            
    except Exception as e:
        print(f"Error during backup: {e}")

if __name__ == '__main__':
    sub_merge.geoip_update(
        'https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')
    # The script now only generates the YML file. It does not touch Eternity or Eternity.txt
    eternity_convert(config_file, Eternity_yml_file)
    backup(Eterniy_file) # This will now back up the correct file created by output.py
    sub_merge.readme_update(readme, sub_merge.read_list(sub_list_json))
