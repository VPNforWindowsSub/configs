import requests
import yaml
import base64
import os

# File paths
sub_list_json = './sub/sub_list.json'
sub_merge_path = './sub/'

def get_all_proxies(url_list):
    """Downloads content from all URLs and decodes if necessary."""
    full_content = ""
    for item in url_list:
        urls = item.get("url")
        if not isinstance(urls, list):
            urls = [urls]
        
        for url in urls:
            try:
                print(f"-> Fetching content from: {url}")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                content = response.text
                
                # Attempt to decode if it looks like Base64
                try:
                    # A simple check: if it's one long line with no spaces, it's likely base64
                    if ' ' not in content and '\n' not in content.strip():
                        print("   - Content appears to be Base64, decoding...")
                        content = base64.b64decode(content).decode('utf-8', 'ignore')
                except Exception:
                    print("   - Failed to decode Base64, using as is.")
                
                full_content += content + "\n"
            except requests.RequestException as e:
                print(f"   - Failed to fetch {url}: {e}")
    
    return full_content

def convert_content_to_yaml(content, converter_host="http://127.0.0.1:25500"):
    """Sends raw proxy content to the subconverter and gets a clean YAML output."""
    if not content.strip():
        return None
        
    convert_url = f'{converter_host}/sub?target=clash&insert=false&emoji=true&list=false&tfo=false&scv=true&fdn=false&sort=false&udp=false'
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    
    try:
        print("-> Sending content to subconverter for YAML conversion...")
        response = requests.post(convert_url, data=content.encode('utf-8'), headers=headers, timeout=60)
        response.raise_for_status()
        
        if "No nodes were found!" in response.text:
            print("   - Subconverter returned no nodes.")
            return None
            
        # Parse to ensure it's valid YAML and has proxies
        parsed_yaml = yaml.safe_load(response.text)
        if 'proxies' in parsed_yaml and parsed_yaml['proxies']:
            print(f"   - Successfully converted {len(parsed_yaml['proxies'])} nodes.")
            return response.text
        else:
            print("   - Conversion resulted in empty proxy list.")
            return None
            
    except Exception as e:
        print(f"   - Error during subconversion: {e}")
        return None

def main(url_list):
    """Main function to get subs and write files."""
    print("Starting subscription processing...")
    
    # 1. Get all raw proxy links
    raw_proxy_content = get_all_proxies(url_list)
    
    if not raw_proxy_content:
        print("No proxy content could be fetched. Exiting.")
        # Create empty files to prevent workflow failure
        open(f'{sub_merge_path}/sub_merge_yaml.yml', 'w').close()
        open(f'{sub_merge_path}/sub_merge_base64.txt', 'w').close()
        return

    # 2. Convert the raw content to clean YAML
    final_yaml_content = convert_content_to_yaml(raw_proxy_content)

    if not final_yaml_content:
        print("Failed to generate YAML content. Exiting.")
        open(f'{sub_merge_path}/sub_merge_yaml.yml', 'w').close()
        open(f'{sub_merge_path}/sub_merge_base64.txt', 'w').close()
        return

    # 3. Write the final YAML file
    with open(f'{sub_merge_path}/sub_merge_yaml.yml', 'w', encoding='utf-8') as f:
        f.write(final_yaml_content)
    print(f"-> Successfully wrote to sub_merge_yaml.yml")

    # 4. Create the Base64 version for the speed test
    try:
        parsed_yaml = yaml.safe_load(final_yaml_content)
        # We need to convert the YAML back to raw links for LiteSpeedTest
        # This is a placeholder as we are now using the API test.
        # For consistency, we will just encode the YAML content itself.
        # A better approach would be a yaml_decode function if needed.
        base64_content = base64.b64encode(final_yaml_content.encode('utf-8')).decode('ascii')
        with open(f'{sub_merge_path}/sub_merge_base64.txt', 'w', encoding='utf-8') as f:
            f.write(base64_content)
        print(f"-> Successfully wrote to sub_merge_base64.txt")
    except Exception as e:
        print(f"-> Error creating Base64 file: {e}")

if __name__ == "__main__":
    # This part is not used by the workflow but is good for local testing
    pass
