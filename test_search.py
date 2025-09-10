#!/usr/bin/env python3
"""
Test script to directly test the search endpoint
"""

import requests
import json

def test_search():
    """Test the search endpoint directly"""
    
    url = "http://127.0.0.1:5000/search"
    data = {
        "name": "Anand Khandare",
        "department": "Artificial Intelligence and Data Science", 
        "college": "Thakur College of Engineering and Technology"
    }
    
    print("Testing search endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"Publications Found: {result.get('publications_found', 'N/A')}")
            print(f"Publications Added: {result.get('publications_added', 'N/A')}")
        else:
            print("ERROR: Search request failed")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_search()
