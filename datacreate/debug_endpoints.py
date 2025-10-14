#!/usr/bin/env python
"""
Debug script to check endpoints and their responses
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def debug_services_endpoint():
    """Debug the services endpoint"""
    print("=== Debugging Services Endpoint ===")
    
    # Try to access services without authentication
    response = requests.get(f"{BASE_URL}/api/services/")
    print(f"Services (no auth): {response.status_code}")
    if response.status_code != 200:
        print(f"  Response: {response.text[:200]}...")
    
    # Try with customer credentials
    credentials = {'username': 'customer1', 'password': 'password123'}
    auth_response = requests.post(f"{BASE_URL}/auth/login/", json=credentials)
    
    if auth_response.status_code == 200:
        token = auth_response.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}/api/services/", headers=headers)
        print(f"Services (with auth): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Services count: {len(data.get('results', []))}")
        else:
            print(f"  Response: {response.text[:200]}...")
    else:
        print(f"Auth failed: {auth_response.status_code}")
        print(f"  Response: {auth_response.text}")

def debug_auth_endpoint():
    """Debug the authentication endpoint"""
    print("\n=== Debugging Auth Endpoint ===")
    
    credentials = {'username': 'customer1', 'password': 'password123'}
    response = requests.post(f"{BASE_URL}/auth/login/", json=credentials)
    print(f"Auth response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Access token: {data.get('access', 'N/A')[:20]}...")
        print(f"  Refresh token: {data.get('refresh', 'N/A')[:20]}...")
    else:
        print(f"  Response: {response.text}")

def debug_api_root():
    """Debug the API root endpoint"""
    print("\n=== Debugging API Root ===")
    
    response = requests.get(f"{BASE_URL}/api/")
    print(f"API Root: {response.status_code}")
    if response.status_code == 200:
        print("  API is accessible")
    else:
        print(f"  Response: {response.text[:200]}...")

if __name__ == '__main__':
    debug_auth_endpoint()
    debug_api_root()
    debug_services_endpoint()