#!/usr/bin/env python3
"""
Python client for testing the FastAPI circuit simulation service.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the FastAPI circuit simulation service."""
    print("🚀 Testing Circuit Simulation API")
    print("=" * 50)
    
    # 1. Health check
    print("1. Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 2. Create circuit
    print("2. Creating RC Circuit...")
    circuit_data = {
        "name": "Python Test Circuit",
        "description": "RC circuit created via Python client",
        "components": [
            {
                "type": "voltage_source",
                "name": "V1", 
                "positive_node": "1",
                "negative_node": "0",
                "value": "10V"
            },
            {
                "type": "resistor",
                "name": "R1",
                "positive_node": "1", 
                "negative_node": "2",
                "value": "2k"
            },
            {
                "type": "capacitor",
                "name": "C1",
                "positive_node": "2",
                "negative_node": "0", 
                "value": "10u"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/circuits", json=circuit_data)
    print(f"Status: {response.status_code}")
    circuit = response.json()
    print(f"Created Circuit ID: {circuit['id']}")
    print(f"Components: {circuit['component_count']}, Nodes: {circuit['node_count']}\n")
    
    circuit_id = circuit['id']
    
    # 3. Start DC simulation
    print("3. Starting DC Simulation...")
    sim_data = {
        "type": "dc",
        "parameters": {"analysis": "operating_point"},
        "priority": 8
    }
    
    response = requests.post(f"{BASE_URL}/api/circuits/{circuit_id}/simulate", json=sim_data)
    simulation = response.json()
    job_id = simulation['job_id']
    print(f"Job ID: {job_id}")
    print(f"Status: {simulation['status']}\n")
    
    # 4. Monitor simulation (it runs immediately in our implementation)
    print("4. Checking Simulation Status...")
    response = requests.get(f"{BASE_URL}/api/simulations/{job_id}")
    status = response.json()
    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress']}%")
    print(f"Message: {status['message']}\n")
    
    # 5. Get results if available
    if status['status'] == 'completed':
        print("5. Getting Simulation Results...")
        response = requests.get(f"{BASE_URL}/api/simulations/{job_id}/results")
        if response.status_code == 200:
            results = response.json()
            print(f"Voltages: {len(results.get('voltages', {}))} nodes")
            print(f"Currents: {len(results.get('currents', {}))} branches")
            print(f"Metadata: {results.get('metadata', {})}\n")
        else:
            print(f"Results not ready: {response.status_code}\n")
    
    # 6. Start transient simulation
    print("6. Starting Transient Simulation...")
    transient_data = {
        "type": "transient",
        "parameters": {
            "stop_time": 0.001,
            "step_time": 0.00001
        },
        "priority": 6
    }
    
    response = requests.post(f"{BASE_URL}/api/circuits/{circuit_id}/simulate", json=transient_data)
    transient_sim = response.json()
    transient_job_id = transient_sim['job_id']
    print(f"Transient Job ID: {transient_job_id}\n")
    
    # 7. List all simulations
    print("7. Listing All Simulations...")
    response = requests.get(f"{BASE_URL}/api/simulations")
    simulations = response.json()
    print(f"Total Simulations: {simulations['total']}")
    for sim in simulations['simulations'][:3]:  # Show first 3
        print(f"  - {sim['job_id'][:8]}... ({sim['type']}) - {sim['status']}")
    
    print("\n✅ API Testing Complete!")
    print(f"Visit {BASE_URL}/docs for interactive documentation")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running!")
        print("Start it with: uv run uvicorn src.api.main:app --reload")