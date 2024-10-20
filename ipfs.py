# -*- coding: utf-8 -*-
import requests
import json

def pin_to_ipfs(data):
    """
    Converts a Python dictionary to JSON and uploads it to the local IPFS node.
    Returns the CID (Content Identifier) of the pinned data.
    """
    assert isinstance(data, dict), "Error: pin_to_ipfs expects a dictionary"
    
    # URL for the local IPFS node
    url = "http://localhost:5001/api/v0/add"
    
    # Convert the data to JSON and prepare it for upload
    json_data = json.dumps(data)
    files = {
        'file': ('data.json', json_data, 'application/json')  # 添加MIME类型
    }
    
    try:
        # Send the POST request to the IPFS API to add the file
        response = requests.post(url, files=files)
        response.raise_for_status()  # 如果响应状态码不是 200，抛出异常
        
        response_json = response.json()
        cid = response_json.get('Hash')
        
        if not cid:
            raise Exception("Failed to obtain CID from IPFS response.")
        
        return str(cid)  # Ensure CID is returned as a string
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to pin data to IPFS: {}".format(e))

def get_from_ipfs(cid, content_type="json"):
    """
    Retrieves data from IPFS using the provided CID.
    Returns the content in JSON format by default.
    """
    assert isinstance(cid, str), "get_from_ipfs expects a CID in the form of a string"
    
    # Try using different gateways
    gateways = [
        f"https://cloudflare-ipfs.com/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://gateway.moralisipfs.com/ipfs/{cid}"
    ]
    
    for gateway_url in gateways:
        try:
            response = requests.get(gateway_url)
            response.raise_for_status()  # If status code is not 200, raise an exception
            
            if content_type == "json":
                try:
                    data = response.json()
                    assert isinstance(data, dict), "get_from_ipfs should return a dictionary when content_type is 'json'"
                except json.JSONDecodeError:
                    raise Exception("The content retrieved is not valid JSON.")
            else:
                data = response.content
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data from {gateway_url}: {e}")
    
    raise Exception("Failed to retrieve data from any IPFS gateway")

if __name__ == "__main__":
    # 使用你想要测试的 CID
    cid = "QmZKxhYycNWK4wkqkpt2gbaqzzZUZ5op5kmNeFZo"

    # Retrieve the data using the CID
    if isinstance(cid, str):
        try:
            retrieved_data = get_from_ipfs(cid)
            print("Data retrieved from IPFS: {}".format(retrieved_data))
        except Exception as e:
            print(e)
    else:
        print("Error: The CID is not in a string format.")

