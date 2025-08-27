#!/usr/bin/env python3
"""
WebSocket demo client for testing real-time simulation updates.
"""

import asyncio
import json
import websockets
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def websocket_demo():
    """Demo WebSocket real-time simulation monitoring."""
    print("🔌 WebSocket Demo - Real-time Simulation Updates")
    print("=" * 55)
    
    # 1. Create a circuit via REST API
    print("1. Creating test circuit...")
    circuit_data = {
        "name": "WebSocket Demo Circuit",
        "description": "RC circuit for WebSocket testing",
        "components": [
            {
                "type": "voltage_source",
                "name": "V1",
                "positive_node": "1", 
                "negative_node": "0",
                "value": "12V"
            },
            {
                "type": "resistor",
                "name": "R1",
                "positive_node": "1",
                "negative_node": "2",
                "value": "10k"
            },
            {
                "type": "capacitor",
                "name": "C1",
                "positive_node": "2",
                "negative_node": "0",
                "value": "100u"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/circuits", json=circuit_data)
        circuit = response.json()
        circuit_id = circuit['id']
        print(f"   Circuit created: {circuit_id}")
        
        # 2. Start simulation via REST API  
        print("2. Starting transient simulation...")
        sim_data = {
            "type": "transient",
            "parameters": {
                "stop_time": 0.005,
                "step_time": 0.0001
            },
            "priority": 8
        }
        
        response = requests.post(f"{BASE_URL}/api/circuits/{circuit_id}/simulate", json=sim_data)
        simulation = response.json()
        job_id = simulation['job_id']
        print(f"   Job started: {job_id}")
        
        # 3. Connect to WebSocket for real-time updates
        print("3. Connecting to WebSocket for real-time updates...")
        ws_url = f"{WS_URL}/ws/simulation/{job_id}"
        
        async with websockets.connect(ws_url) as websocket:
            print(f"   Connected to: {ws_url}")
            
            # Send a ping command
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print("   Sent ping command")
            
            # Listen for messages
            message_count = 0
            while message_count < 10:  # Limit messages for demo
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    message_type = data.get("type", "unknown")
                    
                    print(f"   [{timestamp}] {message_type.upper()}: ", end="")
                    
                    if message_type == "connection":
                        print(data.get("message", ""))
                        
                    elif message_type == "pong":
                        print("WebSocket connection active")
                        
                    elif message_type == "progress":
                        progress_data = data.get("data", {})
                        progress = progress_data.get("progress", 0)
                        message = progress_data.get("message", "")
                        print(f"{progress:.1f}% - {message}")
                        
                    elif message_type == "result":
                        result_data = data.get("data", {})
                        status = result_data.get("status", "unknown")
                        print(f"Simulation {status}")
                        
                        if status == "completed":
                            # Get results via REST API
                            print("4. Fetching simulation results...")
                            result_response = requests.get(f"{BASE_URL}/api/simulations/{job_id}/results")
                            if result_response.status_code == 200:
                                results = result_response.json()
                                print(f"   Voltages: {len(results.get('voltages', {}))} nodes")
                                print(f"   Currents: {len(results.get('currents', {}))} branches")
                                if results.get('time'):
                                    print(f"   Time points: {len(results['time'])}")
                            break
                            
                    else:
                        print(f"Message: {data.get('message', '')}")
                    
                    message_count += 1
                    
                except asyncio.TimeoutError:
                    print("   [TIMEOUT] No more messages received")
                    break
                    
        print("\n✅ WebSocket Demo Complete!")
        print(f"Visit {BASE_URL}/docs to explore the full API")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running!")
        print("Start it with: uv run uvicorn src.api.main:app --reload")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(websocket_demo())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Failed to run demo: {e}")
        print("Make sure the API server is running and websockets is installed:")
        print("  uv add websockets")
        print("  uv run uvicorn src.api.main:app --reload")