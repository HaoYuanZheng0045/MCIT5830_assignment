import requests
import json

# 你的 Pinata API 密钥和密钥
API_KEY = "442e4f52649c261647e2"
API_SECRET = "fcd2883dbeee1221924a4097186802dbb457f4950353933f4a537b658e35718a"

def pin_to_ipfs(data):
    """
    Converts a Python dictionary to JSON and uploads it to Pinata.
    Returns the CID (Content Identifier) of the pinned data.
    """
    assert isinstance(data, dict), "Error: pin_to_ipfs expects a dictionary"
    
    # Pinata API URL
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    headers = {
        "pinata_api_key": API_KEY,
        "pinata_secret_api_key": API_SECRET,
        "Content-Type": "application/json"
    }

    try:
        # Convert the data to JSON
        json_data = json.dumps(data)
        response = requests.post(url, data=json_data, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        
        response_json = response.json()
        cid = response_json.get('IpfsHash')
        
        if not cid:
            raise Exception("Failed to obtain CID from Pinata response.")
        
        return str(cid)  # 确保CID是字符串格式返回
    except requests.exceptions.RequestException as e:
        raise Exception("Failed to pin data to IPFS via Pinata: {}".format(e))

def get_from_ipfs(cid, content_type="json"):
    """
    Retrieves data from IPFS using the provided CID through a public gateway.
    Returns the content in JSON format by default.
    """
    assert isinstance(cid, str), "get_from_ipfs expects a CID in the form of a string"
    
    # Using a public gateway to access the IPFS data
    gateways = [
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://ipfs.io/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]

    for gateway_url in gateways:
        try:
            response = requests.get(gateway_url)
            response.raise_for_status()  # If status code is not 200, raise an exception
            
            if content_type == "json":
                data = response.json()
                assert isinstance(data, dict), "get_from_ipfs should return a dictionary when content_type is 'json'"
            else:
                data = response.content
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data from {gateway_url}: {e}")
    
    raise Exception("Failed to retrieve data from any IPFS gateway")

if __name__ == "__main__":
    # Data to be pinned to IPFS
    data_to_pin = {
        "title": "EVERYDAYS: THE FIRST 5000 DAYS",
        "name": "EVERYDAYS: THE FIRST 5000 DAYS",
        "type": "object",
        "imageUrl": "https://ipfsgateway.makersplace.com/ipfs/QmZ15eQX8FPjfrtdX3QYbrhZxJpbLpvDpsgb2p3VEH8Bqq",
        "description": "I made a picture from start to finish every single day from May 1st, 2007 - January 7th, 2021. This is every one of those pictures.",
        "attributes": [
            {
                "trait_type": "Creator",
                "value": "beeple"
            }
        ],
        "properties": {
            "name": {
                "type": "string",
                "description": "EVERYDAYS: THE FIRST 5000 DAYS"
            },
            "description": {
                "type": "string",
                "description": "I made a picture from start to finish every single day from May 1st, 2007 - January 7th, 2021. This is every one of those pictures."
            },
            "preview_media_file": {
                "type": "string",
                "description": "https://ipfsgateway.makersplace.com/ipfs/QmZ15eQX8FPjfrtdX3QYbrhZxJpbLpvDpsgb2p3VEH8Bqq"
            },
            "preview_media_file_type": {
                "type": "string",
                "description": "jpg"
            },
            "created_at": {
                "type": "datetime",
                "description": "2021-02-16T00:07:31.674688+00:00"
            },
            "total_supply": {
                "type": "int",
                "description": 1
            },
            "digital_media_signature_type": {
                "type": "string",
                "description": "SHA-256"
            },
            "digital_media_signature": {
                "type": "string",
                "description": "6314b55cc6ff34f67a18e1ccc977234b803f7a5497b94f1f994ac9d1b896a017"
            },
            "raw_media_file": {
                "type": "string",
                "description": "https://ipfsgateway.makersplace.com/ipfs/QmXkxpwAHCtDXbbZHUwqtFucG1RMS6T87vi1CdvadfL7qA"
            }
        }
    }
    
    try:
        # Pin data to IPFS using Pinata
        cid = pin_to_ipfs(data_to_pin)
        print("Data successfully pinned to IPFS with CID: {}".format(cid))
    except Exception as e:
        print(e)

    # Retrieve the data using the CID
    if isinstance(cid, str):
        try:
            retrieved_data = get_from_ipfs(cid)
            print("Data retrieved from IPFS: {}".format(retrieved_data))
        except Exception as e:
            print(e)
    else:
        print("Error: The CID is not in a string format.")



