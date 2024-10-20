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
        'file': ('data.json', json_data)
    }
    
    # Send the POST request to the IPFS API to add the file
    response = requests.post(url, files=files)
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        cid = response_json['Hash']
    else:
        raise Exception("Failed to pin data to IPFS: {}".format(response.text))
    
    return str(cid)  # Ensure CID is returned as a string

def get_from_ipfs(cid, content_type="json"):
    """
    Retrieves data from IPFS using the provided CID.
    Returns the content in JSON format by default.
    """
    assert isinstance(cid, str), "get_from_ipfs expects a CID in the form of a string"
    
    # URL for retrieving the data from the IPFS gateway
    gateway_url = "http://localhost:8080/ipfs/{}".format(cid)
    
    # Send GET request to fetch the file from IPFS
    response = requests.get(gateway_url)
    
    # Check if the request was successful
    if response.status_code == 200:
        if content_type == "json":
            data = response.json()
        else:
            data = response.content
    else:
        raise Exception("Failed to retrieve data from IPFS: {}".format(response.text))
    
    if content_type == "json":
        assert isinstance(data, dict), "get_from_ipfs should return a dictionary"
    
    return data

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
        # Pin data to IPFS
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

