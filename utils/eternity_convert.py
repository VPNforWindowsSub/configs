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
Eterniy_file = './Eternity'
Eternity_yml_file = './Eternity.yml'
readme = './README.md'
log_file = './LogInfo.txt'

provider_path = './update/provider/'
update_path = './update/'

sub_list_json = './sub/sub_list.json'

config_file = './update/provider/config.yml'
config_global_file = './update/provider/config-global.yml'

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def is_ip_address(address):
    try:
        parts = address.split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    except:
        return False

def substrings(string, left, right):
    try:
        value = string.replace('\n', '').replace(' ', '')
        start = value.index(left)
        end = value[start:].index(right) + len(value[:start])
        final_value = value[start:end].replace(left, '')
        return final_value
    except ValueError:
        return ""

def eternity_convert(file, config, output, provider_file_enabled=True):
    with open(Eterniy_base_file, 'r', encoding='utf-8') as f:
        base_content = f.read()

    subconverter_url = "http://127.0.0.1:25500/sub?target=clash&udp=false"
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    try:
        response = requests.post(subconverter_url, data=base_content.encode('utf-8'), headers=headers, timeout=60)
        response.raise_for_status()
        all_provider = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error contacting subconverter: {e}")
        return

    temp_providers = all_provider.split('\n')
    try:
        with open(log_file, 'r') as log_reader:
            log_lines = log_reader.readlines()
    except FileNotFoundError:
        log_lines = []

    indexx = 0
    for line in temp_providers:
        if line and line.strip() != 'proxies:':
            if indexx < len(log_lines):
                server_name = substrings(line, "name:", ",")
                server_type = substrings(line, "type:", ",")
                log_lines[indexx] = f"name: {server_name} | type: {server_type} | {log_lines[indexx]}"
                indexx += 1

    with open(log_file, 'w') as log_writer:
        log_writer.writelines(log_lines)

    removed_bad_char = [line for line in all_provider.split("\n")[1:] if "�" not in line and line.strip()]
    log_lines_without_bad_char = [line for line in log_lines if "�" not in line]

    print(f"removed_bad_char count => {len(removed_bad_char)} & log_lines_without_bad_char count => {len(log_lines_without_bad_char)}")

    num = 200
    num = len(removed_bad_char) if len(removed_bad_char) <= num else num
    
    final_proxies_yaml_list = removed_bad_char[:num]
    all_provider = "proxies:\n" + "\n".join(final_proxies_yaml_list)

    proxy_all = []
    skip_names_index = []
    for indexx, line in enumerate(final_proxies_yaml_list):
        try:
            speed = substrings(log_lines_without_bad_char[indexx], "avg_speed:", "|")
            line_parsed = yaml.safe_load(line)
            
            if line_parsed:
                server = line_parsed.get('server', '')
                if is_ip_address(server):
                    if line_parsed.get('sni') == server:
                        del line_parsed['sni']
                    if 'ws-opts' in line_parsed and 'headers' in line_parsed.get('ws-opts', {}) and line_parsed['ws-opts']['headers'].get('Host') == server:
                        del line_parsed['ws-opts']['headers']['Host']
                        if not line_parsed['ws-opts']['headers']:
                            del line_parsed['ws-opts']['headers']
                
                line_parsed['skip-cert-verify'] = True
                
                line_parsed['name'] = f"{line_parsed.get('name', '')} | {speed}"
                
                if "password" in line_parsed:
                    password_str = str(line_parsed.get("password"))
                    line_parsed["password"] = password_str
                    if re.match(r'^\d+\.?\d*[eE][-+]?\d+$', password_str):
                        skip_names_index.append(indexx)
                        continue
                
                proxy_all.append(line_parsed)

        except (yaml.YAMLError, IndexError) as e:
            print(f"Skipping line due to error: {e}. Line: {line}")
            continue

    if provider_file_enabled:
        providers_files = {'all': provider_path + 'provider-all.yml'}
        eternity_providers = {'all': all_provider}
        print('Writing content to provider')
        for key in providers_files.keys():
            with open(providers_files[key], 'w', encoding='utf-8') as provider_file:
                provider_file.write(eternity_providers[key])
        print('Done!\n')

    with open(config_file, 'r', encoding='utf-8') as config_f:
        config = yaml.safe_load(config_f.read())

    all_name = [p['name'] for i, p in enumerate(proxy_all) if i not in skip_names_index]

    proxy_groups = config.get('proxy-groups', [])
    proxy_group_fill = [rule['name'] for rule in proxy_groups if rule.get('proxies') is None]

    full_size = len(all_name)
    part_size = full_size // 4
    
    for rule in proxy_groups:
        if rule['name'] in proxy_group_fill:
            if "Tier 1" in rule['name']:
                rule['proxies'] = all_name[0:part_size]
            elif "Tier 2" in rule['name']:
                rule['proxies'] = all_name[part_size:part_size*2]
            elif "Tier 3" in rule['name']:
                rule['proxies'] = all_name[part_size*2:part_size*3]
            elif "Tier 4" in rule['name']:
                rule['proxies'] = all_name[part_size*3:full_size]

    config['proxies'] = proxy_all
    config['proxy-groups'] = proxy_groups

    config_yaml = yaml.dump(config, default_flow_style=False, sort_keys=False,
                              allow_unicode=True, width=750, indent=2, Dumper=NoAliasDumper)

    with open(output, 'w+', encoding='utf-8') as Eternity_yml:
        Eternity_yml.write(config_yaml)

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
    eternity_convert(Eterniy_file, config_file, output=Eternity_yml_file)
    backup(Eterniy_file)
    sub_merge.readme_update(readme, sub_merge.read_list(sub_list_json))