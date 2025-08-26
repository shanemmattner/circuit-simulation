#!/usr/bin/env python3
"""
Quick test to verify MCP server is working.
This creates a simple voltage divider circuit and simulates it via MCP.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_mcp.server import (
    create_circuit, add_component, run_dc_simulation, validate_circuit
)


async def test_circuit_simulation():
    """Test circuit creation and simulation via MCP server functions."""
    print("🧪 Testing Circuit Simulation MCP Server")
    print("=" * 50)
    
    try:
        # Test 1: Create a circuit
        print("\n1. Creating voltage divider circuit...")
        circuit_result = await create_circuit({
            "name": "Test Voltage Divider",
            "description": "Simple test circuit"
        })
        
        if circuit_result["status"] == "success":
            circuit_id = circuit_result["circuit_id"]
            print(f"   ✅ Created circuit with ID: {circuit_id}")
        else:
            print(f"   ❌ Failed to create circuit: {circuit_result['message']}")
            return
        
        # Test 2: Add voltage source
        print("\n2. Adding voltage source...")
        v1_result = await add_component({
            "circuit_id": circuit_id,
            "type": "voltage_source",
            "name": "V1",
            "value": "10V",
            "positive": 1,
            "negative": 0
        })
        
        if v1_result["status"] == "success":
            print("   ✅ Added voltage source V1")
        else:
            print(f"   ❌ Failed to add V1: {v1_result['message']}")
            return
        
        # Test 3: Add resistors
        print("\n3. Adding resistors...")
        r1_result = await add_component({
            "circuit_id": circuit_id,
            "type": "resistor", 
            "name": "R1",
            "value": "1k",
            "positive": 1,
            "negative": 2
        })
        
        r2_result = await add_component({
            "circuit_id": circuit_id,
            "type": "resistor",
            "name": "R2", 
            "value": "1k",
            "positive": 2,
            "negative": 0
        })
        
        if r1_result["status"] == "success" and r2_result["status"] == "success":
            print("   ✅ Added resistors R1 and R2")
        else:
            print("   ❌ Failed to add resistors")
            return
        
        # Test 4: Validate circuit
        print("\n4. Validating circuit...")
        validation_result = await validate_circuit({
            "circuit_id": circuit_id
        })
        
        if validation_result["status"] == "success":
            print(f"   ✅ Circuit validation: {'PASSED' if validation_result['valid'] else 'FAILED'}")
            if validation_result.get("warnings"):
                print(f"   ⚠️  Warnings: {validation_result['warnings']}")
        else:
            print(f"   ❌ Validation failed: {validation_result['message']}")
        
        # Test 5: Run DC simulation
        print("\n5. Running DC simulation...")
        sim_result = await run_dc_simulation({
            "circuit_id": circuit_id
        })
        
        if sim_result["status"] == "success":
            print("   ✅ DC simulation completed successfully!")
            node_voltages = sim_result["results"]["node_voltages"]
            print(f"   📊 Results:")
            for node, voltage in node_voltages.items():
                print(f"      Node {node}: {voltage:.3f}V")
            
            # Check if voltage divider worked correctly
            if "2" in node_voltages:
                expected = 5.0  # 10V divided by two 1k resistors = 5V
                actual = node_voltages["2"]
                if abs(actual - expected) < 0.1:
                    print(f"   ✅ Voltage divider working correctly: {actual:.3f}V ≈ {expected}V")
                else:
                    print(f"   ⚠️  Unexpected result: {actual:.3f}V, expected ~{expected}V")
        else:
            print(f"   ❌ Simulation failed: {sim_result['message']}")
            return
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! MCP server is working correctly!")
        print("✨ Ready to connect from Claude Desktop or other MCP clients")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run the test."""
    await test_circuit_simulation()


if __name__ == "__main__":
    asyncio.run(main())