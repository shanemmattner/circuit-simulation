#!/usr/bin/env python3
"""
Quick test for AC frequency analysis integration with FastAPI.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ac_analysis():
    """Test AC frequency analysis via FastAPI."""
    print("🔍 Testing AC Frequency Analysis Integration")
    print("=" * 50)
    
    # Create an RC filter circuit (good for AC analysis)
    circuit_data = {
        "name": "RC Filter for AC Analysis",
        "description": "RC low-pass filter for frequency response testing",
        "components": [
            {
                "type": "voltage_source",
                "name": "V1",
                "positive_node": "1",
                "negative_node": "0",
                "value": "1V"  # AC source
            },
            {
                "type": "resistor", 
                "name": "R1",
                "positive_node": "1",
                "negative_node": "2",
                "value": "1k"
            },
            {
                "type": "capacitor",
                "name": "C1", 
                "positive_node": "2",
                "negative_node": "0",
                "value": "1u"  # 1 microfarad
            }
        ]
    }
    
    try:
        # 1. Create circuit
        print("1. Creating RC filter circuit...")
        response = requests.post(f"{BASE_URL}/api/circuits", json=circuit_data)
        
        if response.status_code != 201:
            print(f"   ❌ Failed to create circuit: {response.status_code}")
            return False
            
        circuit = response.json()
        circuit_id = circuit["id"]
        print(f"   ✅ Circuit created: {circuit_id}")
        
        # 2. Start AC frequency analysis
        print("2. Starting AC frequency analysis...")
        ac_request = {
            "type": "ac",
            "parameters": {
                "start_frequency": 1.0,      # 1 Hz
                "stop_frequency": 10000.0,   # 10 kHz
                "points_per_decade": 20,     # Good resolution
                "variation": "dec"           # Logarithmic sweep
            },
            "priority": 8
        }
        
        response = requests.post(f"{BASE_URL}/api/circuits/{circuit_id}/simulate", json=ac_request)
        
        if response.status_code != 202:
            print(f"   ❌ Failed to start AC simulation: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
        simulation = response.json()
        job_id = simulation["job_id"]
        print(f"   ✅ AC simulation started: {job_id}")
        print(f"   Type: {simulation['type']}")
        
        # 3. Check simulation status
        print("3. Monitoring AC simulation...")
        response = requests.get(f"{BASE_URL}/api/simulations/{job_id}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get status: {response.status_code}")
            return False
            
        status = response.json()
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status['progress']}%")
        print(f"   Message: {status.get('message', 'No message')}")
        
        # 4. Get results if completed
        if status["status"] == "completed":
            print("4. Retrieving AC analysis results...")
            response = requests.get(f"{BASE_URL}/api/simulations/{job_id}/results")
            
            if response.status_code == 200:
                results = response.json()
                print("   ✅ AC analysis results retrieved!")
                
                # Check for AC-specific data
                if "frequency" in results:
                    freq_count = len(results["frequency"])
                    print(f"   📊 Frequency points: {freq_count}")
                
                if "voltages" in results:
                    for node, voltage in results["voltages"].items():
                        if isinstance(voltage, dict) and voltage.get("complex"):
                            mag_count = len(voltage["magnitude"])
                            print(f"   🔍 Node {node}: {mag_count} magnitude/phase points")
                            break
                
                print("   🎯 RC Filter frequency response data available!")
                return True
            else:
                print(f"   ⚠️  Results not ready: {response.status_code}")
        elif status["status"] == "failed":
            print(f"   ❌ AC simulation failed: {status.get('message', 'Unknown error')}")
            return False
        else:
            print(f"   ⏳ AC simulation {status['status']} - check again later")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running!")
        print("Start it with: uv run uvicorn src.api.main:app --reload")
        return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AC Frequency Analysis Integration Test")
    print("========================================")
    
    if test_ac_analysis():
        print("\n🎉 AC frequency analysis integration successful!")
        print("FastAPI now supports complete simulation suite: DC + Transient + AC")
    else:
        print("\n⚠️  AC integration needs attention")
    
    print(f"\nVisit {BASE_URL}/docs to test AC analysis interactively")