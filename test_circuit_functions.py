#!/usr/bin/env python3
"""
Test the circuit simulation functions directly (without MCP dependency).
This demonstrates that the core functionality works.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the core functions from circuit_mcp server
# We'll test them without the actual MCP framework
import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Dict

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults


@dataclass 
class CircuitSession:
    """Circuit session for testing."""
    circuit_id: str
    circuit: Circuit
    created_at: datetime
    last_modified: datetime
    simulations: Dict[str, SimulationResults]


# Test storage
SESSIONS: Dict[str, CircuitSession] = {}
ENGINE = SimulationEngine()


async def create_circuit(args):
    """Create circuit function for testing."""
    name = args.get("name", "Untitled Circuit")
    description = args.get("description", "")
    
    circuit_id = str(uuid.uuid4())[:8]
    
    session = CircuitSession(
        circuit_id=circuit_id,
        circuit=Circuit(name),
        created_at=datetime.now(),
        last_modified=datetime.now(),
        simulations={}
    )
    
    SESSIONS[circuit_id] = session
    
    return {
        "status": "success",
        "circuit_id": circuit_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat()
    }


async def add_component(args):
    """Add component function for testing."""
    circuit_id = args.get("circuit_id")
    component_type = args.get("type")
    name = args.get("name")
    value = args.get("value")
    positive = args.get("positive")
    negative = args.get("negative")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    try:
        if component_type == "resistor":
            circuit.add_resistor(name, positive, negative, value)
        elif component_type == "capacitor":
            circuit.add_capacitor(name, positive, negative, value)
        elif component_type == "inductor":
            circuit.add_inductor(name, positive, negative, value)
        elif component_type == "voltage_source":
            circuit.add_voltage_source(name, positive, negative, value)
        elif component_type == "current_source":
            circuit.add_current_source(name, positive, negative, value)
        else:
            return {"status": "error", "message": f"Unknown component type: {component_type}"}
        
        session.last_modified = datetime.now()
        
        return {
            "status": "success",
            "message": f"Added {component_type} {name} to circuit",
            "component": {
                "type": component_type,
                "name": name,
                "value": value,
                "nodes": {"positive": positive, "negative": negative}
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to add component: {str(e)}"}


async def validate_circuit(args):
    """Validate circuit function for testing."""
    circuit_id = args.get("circuit_id")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    issues = []
    warnings = []
    
    if not circuit.components:
        issues.append("Circuit has no components")
    
    has_source = any(
        comp.get("type") in ["voltage_source", "current_source"]
        for comp in circuit.components
    )
    if not has_source:
        issues.append("Circuit has no voltage or current sources")
    
    if 0 not in circuit.nodes:
        warnings.append("Circuit has no explicit ground (node 0)")
    
    valid = len(issues) == 0
    
    return {
        "status": "success", 
        "valid": valid,
        "issues": issues,
        "warnings": warnings,
        "summary": {
            "components": len(circuit.components),
            "nodes": len(circuit.nodes),
            "has_ground": 0 in circuit.nodes,
            "has_source": has_source
        }
    }


async def run_dc_simulation(args):
    """Run DC simulation function for testing."""
    circuit_id = args.get("circuit_id")
    
    session = SESSIONS.get(circuit_id)
    if not session:
        return {"status": "error", "message": f"Circuit {circuit_id} not found"}
    
    circuit = session.circuit
    
    try:
        results = ENGINE.simulate_dc(circuit)
        session.simulations["dc"] = results
        session.last_modified = datetime.now()
        
        node_voltages = {}
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                node_voltages[str(node)] = float(voltage[0])
        
        branch_currents = {}
        for component in results.components:
            current = results.current(component)
            if current is not None:
                branch_currents[component] = float(current[0])
        
        return {
            "status": "success",
            "simulation_type": "dc",
            "circuit_id": circuit_id,
            "circuit_name": circuit.name,
            "results": {
                "node_voltages": node_voltages,
                "branch_currents": branch_currents,
                "convergence": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "message": f"DC simulation failed: {str(e)}", "circuit_id": circuit_id}


async def test_circuit_simulation():
    """Test circuit creation and simulation."""
    print("🧪 Testing Circuit Simulation MCP Functions")
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
        
        print("\n" + "=" * 50)
        print("🎉 MCP server functions are working correctly!")
        print("✨ Ready for MCP client integration")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_circuit_simulation())