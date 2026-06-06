import glob
from sub_convert import sub_convert
from list_update import update_url
from get_subs import subs

import re
import os
import yaml
from urllib import request
from urllib.parse import urlparse

Eterniy = './Eternity'
readme = './README.md'
sub_list_txt = './sub/sub_list.txt'
sub_merge_path = './sub/'
sub_list_path = './sub/list/'

ipv4 = r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
ipv6 = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'

def add_valid(line):
    if (line.__contains__("ssr://") or line.__contains__("ss://")
            or line.__contains__("trojan://") or line.__contains__("vmess://") or line.__contains__("vless://")):
        return line
    return ''

class sub_merge():
    def sub_merge(url_list):
        content_list = []
        for t in os.walk(sub_list_path):
            for f in t[2]:
                f = t[0]+f
                os.remove(f)

        for index, url_container in enumerate(url_list):
            ids = url_container['id']
            remarks = url_container['remarks']
            if type(url_container['url']) == list:
                for each_url in url_container["url"]:
                    content = ''
                    print("gather server from " + each_url)
                    content += sub_convert.convert_remote(each_url, 'url', 'http://127.0.0.1:25500')

                    if content == 'Url 解析错误':
                        content = sub_convert.main(each_url, 'url', 'url')
                        if content != 'Url 解析错误':
                            if add_valid(content) != '':
                                content_list.append(content)
                            else:
                                print(f'this url failed{each_url}')
                            print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                        else:
                            print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write(content)
                    elif content == 'Url 订阅内容无法解析':
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                    elif content != None:
                        if add_valid(content) != '':
                            content_list.append(content)
                        else:
                            print(f'this url failed{each_url}')
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write(content)
                        print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                    else:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
            else:
                each_url = url_container["url"]
                content = ''
                print("gather server from " + each_url)
                content += sub_convert.convert_remote(each_url, 'url', 'http://127.0.0.1:25500')

                if content == 'Url 解析错误':
                    content = sub_convert.main(each_url, 'url', 'url')
                    if content != 'Url 解析错误':
                        if add_valid(content) != '':
                            content_list.append(content)
                        else:
                            print(f'this url failed{each_url}')
                        print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                    else:
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                    with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                        file.write(content)
                elif content == 'Url 订阅内容无法解析':
                    with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                        file.write('Url Subscription could not be parsed')
                    print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                elif content != None:
                    content_list.append(content)
                    with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                        file.write(content)
                    print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                else:
                    with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                        file.write('Url Subscription could not be parsed')
                    print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

            print('already gathered ' + str(''.join(content_list).split('\n').__len__()) + '\n')

        print('Merging nodes...\n')

        content_list = list(filter(lambda x: x != '', ''.join(content_list).split("\n")))
        content_list = list(filter(lambda x: x.startswith("ssr://") or x.startswith("ss://")
                                            or x.startswith("trojan://") or x.startswith("vmess://") or x.startswith("vless://"), content_list))

        content_list = list(filter(lambda x: x.__contains__("订阅内容解析错误") == False, content_list))
        content_raw = "\n".join(content_list)

        print(f"it's fine till here with {content_list.__len__()} lines")

        content_yaml = sub_convert.main(content_raw, 'content', 'YAML', {
            'dup_rm_enabled': True, 'format_name_enabled': True})

        yaml_proxies = content_yaml.split('\n')[1:]
        temp = list(filter(lambda x: re.search(ipv6, x) == None or re.search(ipv4, x) != None, yaml_proxies))
        temp = list(filter(lambda x: re.search(r"path: /(.*?)\?(.*?)=(.*?)}", x) == None, temp))

        temp2 = temp
        temp = []
        for pr in temp2:
            try:
                yaml.safe_load(pr)
                temp.append(pr)
            except Exception as e:
                print(e)

        print(f"found {yaml_proxies.__len__() - temp.__len__()} bad lines :)")
        
        content_yaml_str = "\n".join(temp)
        if content_yaml_str[-1:] == '\n':
            content_yaml_str = content_yaml_str[:-1]
        content_yaml_str = 'proxies:\n' + content_yaml_str

        content_raw = sub_convert.yaml_decode(content_yaml_str)
        valid_links = content_raw.splitlines()

        for f in glob.glob(f'{sub_merge_path}sub_merge*'):
            if f.endswith('.txt') or f.endswith('.yml'):
                os.remove(f)

        MAX_BYTES = 70 * 1024 * 1024
        chunks = []
        current_chunk = []
        current_size = 0

        for link in valid_links:
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
            b64_text = sub_convert.base64_encode(plain_text)
            chunk_yaml_str = sub_convert.main(plain_text, 'content', 'YAML', {'dup_rm_enabled': False, 'format_name_enabled': False})
            
            with open(f'{sub_merge_path}sub_merge{suffix}.txt', 'w+', encoding='utf-8') as f:
                f.write(plain_text)
            with open(f'{sub_merge_path}sub_merge_base64{suffix}.txt', 'w+', encoding='utf-8') as f:
                f.write(b64_text)
            with open(f'{sub_merge_path}sub_merge_yaml{suffix}.yml', 'w+', encoding='utf-8') as f:
                f.write(chunk_yaml_str)

        print('Done!\n')

    @staticmethod
    def read_list(txt_file, remote=False):
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]

        input_list = []
        for idx, line in enumerate(lines, 1):
            if " _ " in line:
                url_part, method = line.split(" _ ", 1)
            else:
                url_part, method = line, "auto"

            if remote == False:
                urls = [u.strip() for u in url_part.split('|') if u.strip()]
            else:
                urls = url_part

            site = url_part.split('|')[0] if '|' in url_part else url_part
            try:
                domain = urlparse(site).netloc
            except:
                domain = f"Source_{idx}"
            if not domain: domain = f"Source_{idx}"

            input_list.append({
                "id": idx,
                "remarks": domain,
                "site": site,
                "url": urls,
                "update_method": method,
                "enabled": True
            })
        return input_list

    def geoip_update(url):
        print('Downloading Country.mmdb...')
        try:
            request.urlretrieve(url, './utils/Country.mmdb')
            print('Success!\n')
        except Exception:
            print('Failed!\n')
            pass

    def readme_update(readme_file='./README.md', sub_list=[]):
        print('Update README.md file...')
        with open(readme_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total = 0
        for f in glob.glob('./sub/sub_merge*.txt'):
            if 'base64' not in f:
                with open(f, 'r', encoding='utf-8') as file:
                    total += len([l for l in file.readlines() if l.strip()])
                    
        total_str = f'Total number of merged nodes: `{total}`\n'
        
        thanks = []
        repo_amount_dic = {}
        for repo in sub_list:
            try:
                line = ''
                if repo['enabled'] == True:
                    id = repo['id']
                    remarks = repo['remarks']
                    repo_site = repo['site']

                    sub_file = f'./sub/list/{id:0>2d}.txt'
                    with open(sub_file, 'r', encoding='utf-8') as sf:
                        proxies = sf.readlines()
                        if proxies == ['Url 解析错误'] or proxies == ['订阅内容解析错误']:
                            amount = 0
                        else:
                            amount = len(proxies)
                    repo_amount_dic.setdefault(id, amount)
                    line = f'- [{remarks}]({repo_site}), number of nodes: `{amount}`\n'
                    thanks.append(line)
            except FileNotFoundError:
                pass
            except Exception:
                pass

        for index in range(len(lines)):
            if lines[index] == '### high-speed node\n':
                lines.pop(index+1)
                while lines[index+4] != '\n':
                    lines.pop(index+4)

                with open('./Eternity', 'r', encoding='utf-8') as f:
                    proxies_base64 = f.read()
                    proxies = sub_convert.base64_decode(proxies_base64)
                    proxies = proxies.split('\n')
                    proxies = ['    '+proxy for proxy in proxies if proxy.strip()]
                    proxies = [proxy+'\n' for proxy in proxies]
                top_amount = len(proxies)

                lines.insert(index+1, f'high-speed node quantity: `{top_amount}`\n')
                index += 4
                for i in proxies:
                    index += 1
                    lines.insert(index, i)
                break

        for index in range(len(lines)):
            if lines[index] == '### all nodes\n':
                lines.pop(index+1)

                total_yaml = 0
                for f in glob.glob('./sub/sub_merge_yaml*.yml'):
                    with open(f, 'r', encoding='utf-8') as file:
                        prox_lines = file.read().split('\n')
                        total_yaml += len([p for p in prox_lines if p.strip() and not p.startswith('proxies:')])

                lines.insert(index+1, f'merge nodes w/o dup: `{total_yaml}`\n')
                break

        for index in range(len(lines)):
            if lines[index] == '### node sources\n':
                while lines[index+1] != '\n':
                    lines.pop(index+1)

                for i in thanks:
                    index += 1
                    lines.insert(index, i)
                break

        with open(readme_file, 'w', encoding='utf-8') as f:
            data = ''.join(lines)
            print('Finish!\n')
            f.write(data)


if __name__ == '__main__':
    update_url.update_main(use_airport=False, sub_list_txt="./sub/sub_list.txt")
    sub_merge.geoip_update('https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')

    sub_list = sub_merge.read_list(sub_list_txt)
    sub_list_remote = sub_merge.read_list(sub_list_txt, True)

    subs.get_subs_v3([x for x in sub_list if x.get('update_method') != 'update_airports'])
    sub_merge.readme_update(readme, sub_list)
