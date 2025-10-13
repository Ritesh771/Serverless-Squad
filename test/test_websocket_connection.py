#!/usr/bin/env python
"""
Simple script to test WebSocket connection directly
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws/status/11/customer/"
    
    try:
        print(f"Connecting to {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection confirmation
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received: {data}")
                
                if data.get('type') == 'connection_established':
                    print("✅ Connection established successfully!")
                    return True
                else:
                    print(f"⚠️ Unexpected message type: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⚠️ No message received within 5 seconds")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e.status_code}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("WebSocket Connection Test")
    print("=" * 30)
    
    try:
        result = asyncio.run(test_websocket())
        if result:
            print("\n✅ WebSocket test passed!")
        else:
            print("\n❌ WebSocket test failed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")