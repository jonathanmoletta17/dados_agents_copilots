import requests
import json

try:
    response = requests.get('http://localhost:8000/api/v1/sis/search?page=1&size=20&sort=score')
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    if response.headers.get('content-type') == 'application/json':
        print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
