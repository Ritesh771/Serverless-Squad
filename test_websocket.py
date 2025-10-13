#!/usr/bin/env python
"""
WebSocket connection test script
"""
import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    # Test WebSocket connection
    uri = "ws://127.0.0.1:8000/ws/status/11/customer/"
    
    try:
        print(f"Connecting to {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection confirmation message
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
                
            # Send a test subscription message
            test_message = {
                "type": "subscribe_to_booking",
                "booking_id": "11"
            }
            await websocket.send(json.dumps(test_message))
            print("Sent subscription message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"Response: {data}")
            except asyncio.TimeoutError:
                print("⚠️ No response to subscription message")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("WebSocket Connection Test")
    print("=" * 30)
    
    try:
        asyncio.run(test_websocket_connection())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)