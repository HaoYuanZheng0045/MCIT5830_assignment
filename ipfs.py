# -*- coding: utf-8 -*-
import requests
import json

def pin_to_ipfs(data):
    assert isinstance(data, dict), "Error pin_to_ipfs expects a dictionary"
    json_data = json.dumps(data)
    files = {'file': ('data.json', json_data)}
    response = requests.post('http://localhost:5001/api/v0/add', files=files)
    if response.status_code == 200:
        response_json = response.json()
        cid = response_json['Hash']
    else:
        raise Exception(f"Failed to pin data to IPFS: {response.text}")
    return cid

def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), "get_from_ipfs accepts a cid in the form of a string"
    gateway_url = f"https://ipfs.io/ipfs/{cid}"
    response = requests.get(gateway_url)
    if response.status_code == 200:
        if content_type == "json":
            data = response.json()
        else:
            data = response.content
    else:
        raise Exception(f"Failed to get data from IPFS: {response.text}")
    if content_type == "json":
        assert isinstance(data, dict), "get_from_ipfs should return a dict"
    return data

if __name__ == "__main__":
    data_to_pin = {
        "title": "EVERYDAYS: THE FIRST 5000 DAYS",
        "name": "EVERYDAYS: THE FIRST 5000 DAYS",
        "type": "object",
        "imageUrl": "https://ipfsgateway.makersplace.com/ipfs/QmZ15eQX8FPjfrtdX3QYbrhZxJpbLpvDpsgb2p3VEH8Bqq",
        "description": "I made a picture from start to finish every single day from May 1st, 2007 - January 7th, 2021. This is every motherfucking one of those pictures.",
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
                "description": "I made a picture from start to finish every single day from May 1st, 2007 - January 7th, 2021. This is every motherfucking one of those pictures."
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
        cid = pin_to_ipfs(data_to_pin)
        print(f"Data pinned to IPFS with CID: {cid}")
    except Exception as e:
        print(e)
    
    try:
        retrieved_data = get_from_ipfs(cid)
        print(f"Data retrieved from IPFS: {retrieved_data}")
    except Exception as e:
        print(e)
