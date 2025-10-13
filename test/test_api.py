import requests
import json

# Test the chat query endpoint
url = "http://localhost:8000/api/chat/query/"
data = {
    "user_id": "1",
    "role": "customer",
    "message": "Hello, how can I track my bookings?"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test the chat context endpoint
url = "http://localhost:8000/api/chat/context/"
params = {
    "user_id": "1",
    "role": "customer"
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")