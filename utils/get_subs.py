from sub_convert import sub_convert
from subs_function import subs_function
import json
import re
import os
import yaml
import urllib.parse

sub_list_json = './sub/sub_list.json'
sub_merge_path = './sub/'
sub_list_path = './sub/list/'

ipv4 = r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
ipv6 = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
ill = ['|', '?', '[', ']', '@', '!', '%', ':']
valid_ss_cipher_methods = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr", "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
valid_ss_plugins = ["obfs","v2ray-plugin"]

class subs:

    def get_subs_v3(content_urls: [], output_path="sub_merge", should_cleanup=True, specific_files_cleanup=["05.txt"]):
        if content_urls == []:
            return

        if should_cleanup:
            for t in os.walk(sub_list_path):
                for f in t[2]:
                    if specific_files_cleanup.__contains__(f) == False:
                        f = t[0]+f
                        os.remove(f)
        else:
            for t in os.walk(sub_list_path):
                for f in t[2]:
                    if specific_files_cleanup.__contains__(f):
                        f = t[0]+f
                        os.remove(f)

        content_list = []
        corresponding_list = []
        corresponding_id = 0
        bad_lines = 0
        for (index, url_container) in enumerate(content_urls):
            ids = content_urls[index]['id']
            remarks = content_urls[index]['remarks']
            if type(url_container['url']) == list:
                for each_url in url_container["url"]:
                    print(f"===> Processing URL: {each_url}", flush=True)

                    content_clash = subs_function.convert_sub(
                        each_url, 'clash', "http://0.0.0.0:25500", False, extra_options="&udp=false")
                    
                    print(f"===> Finished processing URL: {each_url}", flush=True)

                    if content_clash == 'Err: No nodes found' or content_clash == 'Err: failed to parse sub':
                        if content_clash == 'Err: No nodes found':
                            print(
                                "host convertor was unable to find any nodes. just continue & ignore...\n", flush=True)
                        if content_clash == 'Err: failed to parse sub':
                            print(
                                "host convertor failed. just continue & ignore...\n", flush=True)
                    elif content_clash != None and content_clash != '':
                        single_url_gather_quantity = list(
                            filter(lambda x: x != '', content_clash.split('\n'))).__len__()
                        print(
                            f"added content of current url : {single_url_gather_quantity - 1}", flush=True)

                        clash_content = list(
                            filter(lambda x: x != '', content_clash.split('\n')[1:]))

                        if clash_content.__len__() > 0:
                            safe_clash = []
                            for (index, cl) in enumerate(clash_content):
                                try:
                                    if re.search(ipv6, str(cl)) == None or re.search(ipv4, str(cl)) != None:
                                        if re.search("path: /(.*?)\?(.*?)=(.*?)}", str(cl)) == None:
                                            cl_res = yaml.safe_load(cl)
                                            if cl_res:
                                                cl_temp = cl_res[0]
                                                if 'uuid' in cl_temp and cl_temp.get('uuid') and len(cl_temp['uuid']) != 36:
                                                    bad_lines += 1
                                                    continue

                                                proxy_type = cl_temp.get('type')

                                                if proxy_type in ["ss", "ssr"]:
                                                    if cl_temp.get("cipher") in valid_ss_cipher_methods:
                                                        if proxy_type == "ss" and 'plugin' in cl_temp:
                                                            if cl_temp.get('plugin') in valid_ss_plugins:
                                                                if cl_temp.get('plugin') == 'obfs' and 'plugin-opts' in cl_temp:
                                                                    if cl_temp['plugin-opts'].get('mode') in ['http', 'tls']:
                                                                        safe_clash.append(cl_res)
                                                                    else:
                                                                        bad_lines += 1
                                                                elif cl_temp.get('plugin') == 'v2ray-plugin' and 'plugin-opts' in cl_temp:
                                                                    if cl_temp['plugin-opts'].get('mode') == 'websocket':
                                                                        safe_clash.append(cl_res)
                                                                    else:
                                                                        bad_lines += 1
                                                                else:
                                                                    safe_clash.append(cl_res)
                                                            else:
                                                                bad_lines += 1
                                                        else:
                                                            safe_clash.append(cl_res)
                                                    else:
                                                        bad_lines += 1

                                                elif proxy_type == "vmess":
                                                    if cl_temp.get("network") in ["h2", "grpc"] and not cl_temp.get("tls"):
                                                        bad_lines += 1
                                                    else:
                                                        safe_clash.append(cl_res)

                                                elif proxy_type in ["vless", "trojan"]:
                                                    safe_clash.append(cl_res)
                                except Exception as e:
                                    bad_lines += 1

                            if safe_clash.__len__() > 0:
                                content_list.append(
                                    "\n".join(clash_content) + "\n")
                                file = open(f'{sub_list_path}{ids:0>2d}.txt',
                                            'a+', encoding='utf-8')
                                file.write("\n".join(clash_content) + "\n")
                                file.close()
                                print(
                                    f'Writing content of {remarks} to {ids:0>2d}.txt\n', flush=True)

                                print("Check Points Passed 👍\n", flush=True)
                                for (i, each_clash_proxy) in enumerate(safe_clash):
                                    corresponding_list.append(
                                        {"id": corresponding_id, "c_clash": each_clash_proxy})
                                    corresponding_id += 1
                            else:
                                print(
                                    f'there is no clash lines {each_url}', flush=True)
                                print(
                                    f'Writing content of {remarks} to {ids:0>2d}.txt\n', flush=True)
                        else:
                            print(
                                f'there is no clash lines first stage {each_url}', flush=True)
                            print(
                                f'Writing content of {remarks} to {ids:0>2d}.txt\n', flush=True)
                    else:
                        print(
                            f'Writing error of {remarks} to {ids:0>2d}.txt\n', flush=True)

            gather_quantity = list(
                filter(lambda x: x != '', ''.join(content_list).split('\n'))).__len__()
            print(f"already gathered {gather_quantity}", flush=True)

            print('\n', flush=True)
            print('----------------------------------------------', flush=True)
            print('\n', flush=True)

        print('===> COLLECTION PHASE COMPLETE. Starting processing phase...', flush=True)
        print(f"Total nodes to process: {len(corresponding_list)}", flush=True)

        # --- CORRECTED ORDER OF OPERATIONS ---
        # 1. De-duplicate first (fast operation)
        print("\n===> STEP 1: Removing duplicate proxies...", flush=True)
        corresponding_list = subs_function.fix_proxies_duplication(
            corresponding_proxies=corresponding_list)
        print("===> STEP 1 COMPLETE.\n", flush=True)

        # 2. Rename the smaller, unique list (slow operation)
        print("===> STEP 2: Renaming proxies based on GeoIP...", flush=True)
        corresponding_list = subs_function.fix_proxies_name(
            corresponding_proxies=corresponding_list)
        print("===> STEP 2 COMPLETE.\n", flush=True)

        print(f"\nfinal sub length => {len(corresponding_list)}", flush=True)

        print("-> [get_subs.py] Applying comprehensive sanitization (tfo, alpn, short-id)...", flush=True)
        for item in corresponding_list:
            proxy = item.get('c_clash', {})
            if isinstance(proxy, list):
                proxy = proxy[0] if proxy else {}

            if 'tfo' in proxy:
                del proxy['tfo']

            if 'alpn' in proxy and isinstance(proxy['alpn'], list):
                cleaned_alpn = [urllib.parse.unquote(v).strip() for v in proxy['alpn']]
                proxy['alpn'] = cleaned_alpn

            if (proxy.get('type') == 'vless' and
                'reality-opts' in proxy and
                'short-id' in proxy.get('reality-opts', {})):

                original_short_id = str(proxy['reality-opts']['short-id'])
                cleaned_short_id = re.sub('[^0-9a-fA-F]', '', original_short_id)

                if cleaned_short_id:
                    proxy['reality-opts']['short-id'] = cleaned_short_id
                else:
                    del proxy['reality-opts']['short-id']

        clash_proxies = [item['c_clash'][0] if isinstance(item['c_clash'], list) else item['c_clash'] for item in corresponding_list]
        final_clash_dict = {'proxies': clash_proxies}

        print("\n===> STEP 3: Generating final output files...", flush=True)
        content_yaml = yaml.dump(final_clash_dict, default_flow_style=False, indent=2, sort_keys=False, allow_unicode=True)
        with open(f'{sub_merge_path}/{output_path}.yml', 'w', encoding='utf-8') as f:
            f.write(content_yaml)
        print(f"Successfully wrote {len(clash_proxies)} nodes to YAML.", flush=True)

        raw_links_str = sub_convert.yaml_decode(final_clash_dict)
        content_base64 = sub_convert.base64_encode(raw_links_str)
        with open(f'{sub_merge_path}/{output_path}_base64.txt', 'w', encoding='utf-8') as f:
            f.write(content_base64)
        print(f"Successfully wrote {len(raw_links_str.splitlines())} nodes to Base64.", flush=True)
        
        print("===> STEP 3 COMPLETE. All tasks finished.", flush=True)
        print('Done!\n', flush=True)

if __name__ == "__main__":
    pass
