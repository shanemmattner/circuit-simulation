#!/usr/bin/env python3
"""
Simple manual test script for circuit simulation
Run with: uv run python test_manual.py
"""

print("🔬 Manual Test Script for Circuit Simulation")
print("=" * 50)

# Test 1: Basic imports
print("\n1️⃣ Testing imports...")
try:
    from circuit_sim import Circuit
    from circuit_sim.simulator import SimulationEngine
    import numpy as np
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

# Test 2: Create a simple circuit
print("\n2️⃣ Creating voltage divider circuit...")
try:
    circuit = Circuit("Voltage Divider Test")
    circuit.add_voltage_source("V1", 1, 0, "10V")
    circuit.add_resistor("R1", 1, 2, "1k")
    circuit.add_resistor("R2", 2, 0, "1k")
    print(f"   ✅ Created: {circuit}")
except Exception as e:
    print(f"   ❌ Circuit creation failed: {e}")
    exit(1)

# Test 3: Run DC simulation
print("\n3️⃣ Running DC simulation...")
try:
    engine = SimulationEngine()
    results = engine.simulate_dc(circuit)
    
    # Access voltage correctly
    voltages = results.voltage(2)  # Returns array
    v_out = voltages[0] if isinstance(voltages, np.ndarray) else voltages
    
    print(f"   📊 Output voltage at node 2: {v_out:.3f}V")
    
    if abs(v_out - 5.0) < 0.1:
        print(f"   ✅ Result correct (expected ~5V)")
    else:
        print(f"   ⚠️  Unexpected result (expected ~5V)")
        
except Exception as e:
    print(f"   ❌ Simulation failed: {e}")
    exit(1)

# Test 4: RC circuit transient
print("\n4️⃣ Testing RC circuit transient analysis...")
try:
    rc_circuit = Circuit("RC Circuit")
    rc_circuit.add_voltage_source("V1", 1, 0, "5V")
    rc_circuit.add_resistor("R1", 1, 2, "10k")
    rc_circuit.add_capacitor("C1", 2, 0, "1uF")
    
    # Run transient
    results = engine.simulate_transient(rc_circuit, stop_time=0.05, step_time=0.0001)
    
    print(f"   📊 Simulation points: {len(results.time)}")
    
    # Check capacitor voltage at t=0 and t=50ms
    cap_voltages = results.voltage(2)
    initial_v = cap_voltages[0] if isinstance(cap_voltages, np.ndarray) else cap_voltages
    final_v = cap_voltages[-1] if isinstance(cap_voltages, np.ndarray) else cap_voltages
    
    print(f"   📊 Initial capacitor voltage: {initial_v:.3f}V")
    print(f"   📊 Final capacitor voltage: {final_v:.3f}V")
    print(f"   ✅ RC transient simulation complete")
    
except Exception as e:
    print(f"   ❌ RC transient failed: {e}")

# Test 5: MCP tools
print("\n5️⃣ Testing MCP tools...")
try:
    from src.circuit_mcp.tools.circuit_tools import CircuitTools
    from src.circuit_mcp.tools.simulation_tools import SimulationTools
    from mcp.server import Server
    import asyncio
    
    # Create server instance for tools
    server = Server("test-server")
    
    # Create tools with server
    ct = CircuitTools(server)
    st = SimulationTools(server)
    
    # Test circuit creation
    result = ct.create_circuit({"name": "MCP Test Circuit"})
    circuit_id = result.get("circuit_id")
    print(f"   ✅ Created circuit via MCP: {circuit_id[:8]}...")
    
    # Add component
    ct.add_component({
        "circuit_id": circuit_id,
        "component_type": "voltage_source",
        "name": "V1",
        "positive": 1,
        "negative": 0,
        "value": "12V"
    })
    print(f"   ✅ Added voltage source via MCP")
    
    ct.add_component({
        "circuit_id": circuit_id,
        "component_type": "resistor",
        "name": "R1",
        "positive": 1,
        "negative": 0,
        "value": "1k"
    })
    print(f"   ✅ Added resistor via MCP")
    
    # Run simulation
    sim_result = asyncio.run(st.run_dc_simulation({"circuit_id": circuit_id}))
    if sim_result.get("status") == "success":
        print(f"   ✅ MCP simulation successful")
    else:
        print(f"   ⚠️  MCP simulation status: {sim_result.get('status')}")
    
except ImportError as e:
    print(f"   ⚠️  MCP not fully configured: {e}")
except Exception as e:
    print(f"   ❌ MCP test failed: {e}")

# Summary
print("\n" + "=" * 50)
print("✨ Manual testing complete!")
print("\nYou can now:")
print("1. Create circuits with: circuit = Circuit('name')")
print("2. Add components: circuit.add_resistor('R1', 1, 2, '1k')")
print("3. Run simulations: results = engine.simulate_dc(circuit)")
print("4. Access results: voltage = results.voltage(node_number)")
print("\nFor MCP server, run: uv run python run_mcp_server.py")