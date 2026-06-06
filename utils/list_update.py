#!/usr/bin/env python3

from datetime import timedelta, datetime
import re
import requests
from requests.adapters import HTTPAdapter

def url_updated(url):
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    try:
        resp = s.get(url, timeout=4)
        status = resp.status_code
    except Exception:
        status = 404
    if status == 200:
        url_updated = True
    else:
        url_updated = False
    return url_updated

class update_url():
    @staticmethod
    def update_main(use_airport=False, sub_list_txt='./sub/sub_list.txt'):
        with open(sub_list_txt, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]

        new_lines = []
        for line in lines:
            if " _ " in line:
                current_url, method = line.split(" _ ", 1)
            else:
                current_url, method = line, "auto"

            if method == 'auto':
                new_lines.append(line)
                continue

            if method == 'update_airports':
                if use_airport:
                    new_url = update_url.update_airports(current_url)
                    if new_url != current_url:
                        print('Airport url updated.')
                        new_lines.append(f"{new_url} _ {method}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
                continue

            print(f'Finding available update for: {current_url[:50]}...')
            if method == 'change_date':
                new_url = update_url.change_date(current_url)
            elif method == 'page_release':
                new_url = update_url.find_link(current_url)
            else:
                new_url = current_url

            if new_url != current_url:
                print(f'Url updated to {new_url[:50]}...\n')
                new_lines.append(f"{new_url} _ {method}")
            else:
                print('No available update\n')
                new_lines.append(line)

        with open(sub_list_txt, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines) + "\n")

    @staticmethod
    def update_airports(current_url):
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=2))
            s.mount('https://', HTTPAdapter(max_retries=2))
            urllist = list(set([x for x in s.get('https://raw.githubusercontent.com/RenaLio/Mux2sub/main/urllist', timeout=4).text.split("\n") if x.startswith("http")]))
            sublist = list(set([x for x in s.get('https://raw.githubusercontent.com/RenaLio/Mux2sub/main/sub_list', timeout=4).text.split("\n") if x.startswith("http")]))

            air_free = list(set([x for x in s.get('https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_free', timeout=4).text.split("\n") if x.startswith("http")]))
            air_mining = list(set([x for x in s.get('https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_mining', timeout=4).text.split("\n") if x.startswith("http")]))

            urllist.extend(sublist)
            urllist.extend(air_free)
            urllist.extend(air_mining)

            if urllist:
                return "|".join(list(set(urllist)))
        except Exception as e:
            print(e)
        return current_url

    @staticmethod
    def change_date(current_url):
        today = datetime.today()
        if "pojiezhiyuanjun/freev2" in current_url:
            date_str = today.strftime('%m%d')
            new_url = f"https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/{date_str}.txt"
        elif "nodefree.org/dy" in current_url:
            date_str = today.strftime('%Y%m%d')
            new_url = f"https://nodefree.org/dy/{today.strftime('%Y')}/{today.strftime('%m')}/{date_str}.yaml"
        elif "v2rayshare.com" in current_url:
            date_str = today.strftime('%Y%m%d')
            new_url = f"https://v2rayshare.com/wp-content/uploads/{today.strftime('%Y')}/{today.strftime('%m')}/{date_str}.txt"
        elif "clashnode.com" in current_url:
            date_str = today.strftime('%Y%m%d')
            new_url = f"https://clashnode.com/wp-content/uploads/{today.strftime('%Y')}/{today.strftime('%m')}/{date_str}.txt"
        else:
            return current_url

        if url_updated(new_url):
            return new_url
        return current_url

    @staticmethod
    def find_link(current_url):
        if "mianfeifq/share" in current_url:
            try:
                res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
                for file in res_json:
                    if file['name'].startswith('data') and file['name'].endswith('.txt'):
                        return file['download_url']
            except Exception:
                pass
        return current_url

if __name__ == '__main__':
    update_url.update_main()
