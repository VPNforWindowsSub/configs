import json
import base64
import os
import time
import geoip2.database

out_json = './out.json'

sub_all_base64 = "./sub/sub_merge_base64.txt"
sub_all = "./sub/sub_merge.txt"
Eternity_file_base64 = "./Eternity"
Eternity_file = "./Eternity.txt"
Eternity_Base = "./EternityBase"
splitted_output = "./sub/splitted/"

def read_json(file):
    while not os.path.isfile(file):
        print('Awaiting speedtest complete')
        time.sleep(30)
    with open(file, 'r', encoding='utf-8') as f:
        print('Reading out.json')
        return json.load(f)

def output_geo_balanced(all_nodes, total_proxies_in_final_file):
    if not all_nodes:
        print("No nodes to process.")
        return
 
    print(f"-> [output.py] Total nodes read from out.json: {len(all_nodes)}")
    vless_nodes_in_json = [node for node in all_nodes if node.get("protocol", "").lower() == "vless"]
    print(f"-> [output.py] VLESS nodes found in out.json: {len(vless_nodes_in_json)}")

    print("Sorting all nodes by speed...")
    all_nodes.sort(key=lambda x: x.get('avg_speed', 0), reverse=True)
    
    all_nodes_no_ssr = [p for p in all_nodes if p.get("protocol", "").lower() != "ssr"]

    source_pool_size = 1000
    source_pool = all_nodes_no_ssr[:source_pool_size]
    
    print(f"Processing top {len(source_pool)} nodes to build the final list...")
    processed_nodes = []
    with geoip2.database.Reader('./utils/Country.mmdb') as reader:
        for node in source_pool:
            try:
                server_host = node.get("remarks", "").split(" - ")[0]
                ip_address = server_host if '.' in server_host and server_host.replace('.', '').isdigit() else node.get('server_ip', '8.8.8.8')
                country = reader.country(ip_address).country.iso_code
                node['country'] = country
                processed_nodes.append(node)
            except (geoip2.errors.AddressNotFoundError, ValueError):
                node['country'] = 'XX'
                processed_nodes.append(node)

    nodes_by_country = {}
    for node in processed_nodes:
        country = node.get('country', 'XX')
        if country not in nodes_by_country:
            nodes_by_country[country] = []
        nodes_by_country[country].append(node)

    final_proxies = []
    selected_node_links = set()

    print("Selecting at least 2 nodes from every available country...")
    for country, nodes in nodes_by_country.items():
        nodes_to_take = min(2, len(nodes))
        for i in range(nodes_to_take):
            node = nodes[i]
            if node['link'] not in selected_node_links:
                final_proxies.append(node)
                selected_node_links.add(node['link'])

    print(f"Selected {len(final_proxies)} nodes based on geographic diversity.")

    if len(final_proxies) < total_proxies_in_final_file:
        print(f"Filling remaining {total_proxies_in_final_file - len(final_proxies)} slots with top-speed nodes...")
        for node in processed_nodes:
            if len(final_proxies) >= total_proxies_in_final_file:
                break
            if node['link'] not in selected_node_links:
                final_proxies.append(node)
                selected_node_links.add(node['link'])

    print("Sorting the final list by speed...")
    final_proxies.sort(key=lambda x: x.get('avg_speed', 0), reverse=True)
    
    final_proxies = final_proxies[:total_proxies_in_final_file]

    print(f"Final list generated with {len(final_proxies)} nodes.")

    final_output_links = [proxy['link'] for proxy in final_proxies]
    eternity_content_base64 = base64.b64encode('\n'.join(final_output_links).encode('utf-8')).decode('ascii')

    with open(Eternity_file_base64, 'w', encoding='utf-8') as f:
        f.write(eternity_content_base64)
        print(f'Write Part Base64 (Eternity) Success! Total: {len(final_output_links)}')

    with open(Eternity_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output_links))
        print('Write Part Text (Eternity.txt) Success!')

    def arred(x, n): return x*(10**n)//1/(10**n)
    log_output_list = []
    for item in all_nodes_no_ssr:
        info = "id: %s | remarks: %s | protocol: %s | ping: %s MS | avg_speed: %s MB | max_speed: %s MB | Link: %s\n" % (str(item["id"]), item["remarks"], item["protocol"], str(
            item["ping"]), str(arred(item.get("avg_speed", 0) * 0.00000095367432, 3)), str(arred(item.get("max_speed", 0) * 0.00000095367432, 3)), item["link"])
        log_output_list.append(info)
    with open('./LogInfo.txt', 'w', encoding='utf-8') as f1:
        f1.writelines(log_output_list)
        f1.close()
        print('Write Log Success!')

    full_output_links = [proxy['link'] for proxy in all_nodes_no_ssr]
    full_content_base64 = base64.b64encode('\n'.join(full_output_links).encode('utf-8')).decode('ascii')
    
    with open(sub_all_base64, 'w+', encoding='utf-8') as f:
        f.write(full_content_base64)
        print('Write All Base64 Success!')
    
    with open(Eternity_Base, 'w') as f:
        f.write('\n'.join(full_output_links))
        print('Write Base Success!')
    with open(sub_all, 'w') as f:
        f.write('\n'.join(full_output_links))
        print('Write All Success!')
    
    os.makedirs(splitted_output, exist_ok=True)
    vmess_outputs, vless_outputs, trojan_outputs, ss_outputs = [], [], [], []

    for link in full_output_links:
        if str(link).startswith("vmess://"): vmess_outputs.append(link)
        if str(link).startswith("vless://"): vless_outputs.append(link)
        if str(link).startswith("trojan://"): trojan_outputs.append(link)
        if str(link).startswith("ss://"): ss_outputs.append(link)

    with open(splitted_output.__add__("vmess.txt"), 'w') as f: f.write("\n".join(vmess_outputs))
    with open(splitted_output.__add__("vless.txt"), 'w') as f: f.write("\n".join(vless_outputs))
    with open(splitted_output.__add__("trojan.txt"), 'w') as f: f.write("\n".join(trojan_outputs))
    with open(splitted_output.__add__("ss.txt"), 'w') as f: f.write("\n".join(ss_outputs))
    print('Write splitted files Success!')
    
    return '\n'.join(full_output_links)

if __name__ == '__main__':
    num = 165 
    all_nodes = read_json(out_json)
    output_geo_balanced(all_nodes, num)