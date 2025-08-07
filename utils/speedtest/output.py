import json
import base64
import os
import time
import geoip2.database
import urllib.parse

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
        # SingTools outputs a direct JSON array of nodes
        return json.load(f)

def reconstruct_link(node):
    """Reconstructs the subscription link from a singtools node object."""
    protocol_type = node.get('type', '')
    
    if protocol_type == 'vless':
        uuid = node.get('uuid', '')
        server = node.get('server', '')
        port = node.get('port', '')
        name = urllib.parse.quote(node.get('name', ''))
        
        params = {
            'type': node.get('network', 'tcp'),
            'security': 'tls' if node.get('tls', {}).get('enabled') else 'none',
            'sni': node.get('tls', {}).get('server_name', ''),
            'fp': node.get('tls', {}).get('fingerprint', ''),
        }
        
        if params['type'] == 'ws':
            ws_opts = node.get('transport', {})
            params['path'] = ws_opts.get('path', '/')
            params['host'] = ws_opts.get('headers', {}).get('Host', '')

        query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v})
        return f"vless://{uuid}@{server}:{port}?{query_string}#{name}"
        
    # Add other protocol reconstructions here if needed (e.g., vmess, trojan)
    # For now, return a placeholder if not VLESS
    return ""


def output_geo_balanced(raw_nodes, total_proxies_in_final_file):
    # --- START: New code block to add ---
    # Filter out nodes that failed the test (speed is 0 or key is missing)
    successful_nodes = [node for node in raw_nodes if node.get("speed", 0) > 0 or node.get("delay", 0) > 0]

    if not successful_nodes:
        print("All node tests failed. No successful nodes to process. Exiting.")
        # Create empty files to prevent the workflow from failing at later steps
        open(Eternity_file_base64, 'w').close()
        open(Eternity_file, 'w').close()
        open(Eternity_Base, 'w').close()
        open(sub_all_base64, 'w').close()
        open(sub_all, 'w').close()
        return
    
    # Replace raw_nodes with only the successful ones for further processing
    raw_nodes = successful_nodes
    # --- END: New code block to add ---

    if not raw_nodes:
        print("No nodes to process.")
        return

    # --- Start of new pre-processing section ---
    all_nodes = []
    for node in raw_nodes:
        # Map singtools keys to the format this script expects
        new_node = {
            "id": node.get("id", ""),
            "remarks": node.get("name", ""),
            "protocol": node.get("type", ""),
            "ping": node.get("delay", 0),
            "avg_speed": node.get("speed", 0), # speed is in B/s
            "max_speed": node.get("speed", 0), # singtools doesn't provide max, use avg
            "server_ip": node.get("ip", ""),
            "link": reconstruct_link(node) # Reconstruct the link
        }
        all_nodes.append(new_node)
    # --- End of new pre-processing section ---

    print(f"-> [output.py] Total nodes read and formatted: {len(all_nodes)}")
    vless_nodes_in_json = [node for node in all_nodes if node.get("protocol", "").lower() == "vless"]
    print(f"-> [output.py] VLESS nodes found: {len(vless_nodes_in_json)}")

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
                # Use server_ip if available, otherwise fallback to remarks
                ip_address = node.get('server_ip')
                if not ip_address:
                    server_host = node.get("remarks", "").split(" - ")[0]
                    ip_address = server_host if '.' in server_host and server_host.replace('.', '').isdigit() else '8.8.8.8'

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

    final_output_links = [proxy['link'] for proxy in final_proxies if proxy['link']]
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

    full_output_links = [proxy['link'] for proxy in all_nodes_no_ssr if proxy['link']]
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
    raw_nodes_from_json = read_json(out_json)
    output_geo_balanced(raw_nodes_from_json, num)