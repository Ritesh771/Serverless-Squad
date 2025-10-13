#!/usr/bin/env python
"""
Simple script to check if the Django server is running and WebSocket endpoint is accessible
"""
import requests
import sys

def check_server():
    try:
        # Check if the server is running
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        print(f"✅ Server is running. Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible on http://127.0.0.1:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server request timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def check_websocket_endpoint():
    try:
        # Check if the WebSocket endpoint is accessible via HTTP (should return 404 or similar)
        response = requests.get('http://127.0.0.1:8000/ws/status/11/customer/', timeout=5)
        print(f"✅ WebSocket endpoint is accessible. Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ WebSocket endpoint is not accessible - server may not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ WebSocket endpoint request timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking WebSocket endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Server and WebSocket Endpoint Check")
    print("=" * 40)
    
    server_ok = check_server()
    websocket_ok = check_websocket_endpoint()
    
    if server_ok and websocket_ok:
        print("\n✅ All checks passed! The server and WebSocket endpoint are accessible.")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed. Please make sure the Django server is running on port 8000.")
        sys.exit(1)