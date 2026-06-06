import json
import re
import os
import base64
import urllib.parse
import yaml
import requests
import glob
from requests.adapters import HTTPAdapter

sub_list_txt = './sub/sub_list.txt'
sub_merge_path = './sub/'
sub_list_path = './sub/list/'

class subs:
    @staticmethod
    def get_subs_v3(content_urls: list, output_path="sub_merge", should_cleanup=True, specific_files_cleanup=None):
        if specific_files_cleanup is None:
            specific_files_cleanup = []
        if not content_urls:
            return

        if should_cleanup:
            for t in os.walk(sub_list_path):
                for f in t[2]:
                    if f not in specific_files_cleanup:
                        os.remove(os.path.join(t[0], f))

        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=2))
        session.mount('https://', HTTPAdapter(max_retries=2))

        all_clash_proxies = []

        for index, url_container in enumerate(content_urls):
            ids = url_container['id']
            repo_links = []

            for each_url in url_container.get("url", []):
                print(f"===> Processing URL: {each_url}", flush=True)
                try:
                    resp = session.get(each_url, timeout=15)
                    resp.raise_for_status()
                    text = resp.text

                    extracted = []
                    matches = re.finditer(r'(vless|vmess|trojan|ss|ssr)://([^\s<>"\'`]+)', text)
                    for m in matches:
                        extracted.append(f"{m.group(1)}://{m.group(2)}")

                    try:
                        b64_text = text.strip()
                        b64_text += '=' * (-len(b64_text) % 4)
                        b64_text = b64_text.replace('-', '+').replace('_', '/')
                        decoded = base64.b64decode(b64_text).decode('utf-8', errors='ignore')
                        matches_b64 = re.finditer(r'(vless|vmess|trojan|ss|ssr)://([^\s<>"\'`]+)', decoded)
                        for m in matches_b64:
                            extracted.append(f"{m.group(1)}://{m.group(2)}")
                    except Exception:
                        pass

                    if not extracted:
                        print(f"No direct links found, falling back to subconverter for {each_url}...", flush=True)
                        try:
                            sc_resp = session.post("http://127.0.0.1:25500/sub?target=mixed", data=text.encode('utf-8'), timeout=15)
                            if sc_resp.status_code == 200:
                                decoded_sc = base64.b64decode(sc_resp.text.strip()).decode('utf-8', errors='ignore')
                                matches_sc = re.finditer(r'(vless|vmess|trojan|ss|ssr)://([^\s<>"\'`]+)', decoded_sc)
                                for m in matches_sc:
                                    extracted.append(f"{m.group(1)}://{m.group(2)}")
                        except Exception as e:
                            print(f"Subconverter fallback failed: {e}")

                    extracted = list(set(extracted))
                    print(f"Found {len(extracted)} links from {each_url}", flush=True)
                    repo_links.extend(extracted)

                except Exception as e:
                    print(f"Failed to process {each_url}: {e}", flush=True)

            repo_links = list(set(repo_links))
            os.makedirs(sub_list_path, exist_ok=True)
            with open(os.path.join(sub_list_path, f'{ids:02d}.txt'), 'w', encoding='utf-8') as f:
                f.write("\n".join(repo_links))

            for link in repo_links:
                ptype = link.split("://")[0]
                all_clash_proxies.append({"type": ptype, "link": link})

        unique_links = list(set([p['link'] for p in all_clash_proxies]))
        os.makedirs(sub_merge_path, exist_ok=True)

        for f in glob.glob(os.path.join(sub_merge_path, f'{output_path}*')):
            if f.endswith('.txt') or f.endswith('.yml'):
                os.remove(f)

        MAX_BYTES = 70 * 1024 * 1024
        chunks = []
        current_chunk = []
        current_size = 0

        for link in unique_links:
            link_size = len(link.encode('utf-8')) + 1
            if current_size + link_size > MAX_BYTES:
                chunks.append(current_chunk)
                current_chunk = [link]
                current_size = link_size
            else:
                current_chunk.append(link)
                current_size += link_size

        if current_chunk:
            chunks.append(current_chunk)

        for i, chunk in enumerate(chunks):
            suffix = "" if i == 0 else f"_{i+1}"
            plain_text = '\n'.join(chunk)
            b64_text = base64.b64encode(plain_text.encode('utf-8')).decode('ascii')
            yaml_proxies = [{"type": link.split("://")[0]} for link in chunk]

            with open(os.path.join(sub_merge_path, f'{output_path}{suffix}.yml'), 'w', encoding='utf-8') as f:
                yaml.dump({'proxies': yaml_proxies}, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            with open(os.path.join(sub_merge_path, f'{output_path}_base64{suffix}.txt'), 'w', encoding='utf-8') as f:
                f.write(b64_text)

            with open(os.path.join(sub_merge_path, f'{output_path}{suffix}.txt'), 'w', encoding='utf-8') as f:
                f.write(plain_text)

        print(f"Successfully wrote {len(unique_links)} nodes.", flush=True)
