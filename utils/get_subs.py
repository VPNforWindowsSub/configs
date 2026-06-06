import json
import re
import os
import base64
import urllib.parse
import yaml
import requests
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
            remarks = url_container['remarks']

            repo_links = []

            for each_url in url_container.get("url", []):
                print(f"===> Processing URL: {each_url}", flush=True)
                try:
                    resp = session.get(each_url, timeout=15)
                    resp.raise_for_status()
                    text = resp.text

                    extracted = []
                    # 1. Direct Regex
                    matches = re.finditer(r'(vless|vmess|trojan|ss|ssr)://([^\s<>"\'`]+)', text)
                    for m in matches:
                        extracted.append(f"{m.group(1)}://{m.group(2)}")

                    # 2. Try Base64 Decode
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

                    # 3. Fallback to Subconverter
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

        print(f"\n===> STEP 3: Generating final output files...", flush=True)

        unique_links = list(set([p['link'] for p in all_clash_proxies]))
        os.makedirs(sub_merge_path, exist_ok=True)

        final_clash_dict = {'proxies': [{"type": p.split("://")[0]} for p in unique_links]}
        with open(os.path.join(sub_merge_path, f'{output_path}.yml'), 'w', encoding='utf-8') as f:
            yaml.dump(final_clash_dict, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        content_base64 = base64.b64encode("\n".join(unique_links).encode('utf-8')).decode('ascii')
        with open(os.path.join(sub_merge_path, f'{output_path}_base64.txt'), 'w', encoding='utf-8') as f:
            f.write(content_base64)

        print(f"Successfully wrote {len(unique_links)} nodes.", flush=True)
