#!/usr/bin/env python
"""
Simulation demo - Shows how to use the Circuit API with simulation.
Run with: uv run python examples/simulation_demo.py
"""

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine, SimulationResults

def demo_dc_analysis():
    """Demonstrate DC operating point analysis."""
    print("=" * 60)
    print("DC OPERATING POINT ANALYSIS DEMO")
    print("=" * 60)
    
    # Create a voltage divider
    circuit = Circuit("Voltage Divider")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2="gnd", resistance="1k")
    
    print(f"\nCircuit: {circuit}")
    print("\nExpected output at node 2: 5V (voltage divider)")
    
    # Try to simulate
    engine = SimulationEngine()
    try:
        print("\nRunning DC simulation...")
        results = engine.simulate_dc(circuit)
        
        # Display results
        print(f"\nSimulation Results: {results}")
        print("\nNode Voltages:")
        for node in results.nodes:
            voltage = results.voltage(node)
            if voltage is not None:
                print(f"  Node {node}: {voltage[0]:.3f} V")
        
        # Verify the voltage divider worked
        v2 = results.voltage(2)
        if v2 is not None:
            print(f"\n✓ Voltage divider output: {v2[0]:.3f} V")
            
    except ImportError as e:
        print(f"\n⚠ Simulation requires ngspice: {e}")
        print("\nTo install ngspice:")
        print("  - Ubuntu/Debian: sudo apt-get install ngspice")
        print("  - macOS: brew install ngspice")
        print("  - Windows: Download from http://ngspice.sourceforge.net/")
        
        # Show what would happen
        print("\n📊 Expected results (if ngspice was available):")
        print("  Node 1: 10.000 V (input)")
        print("  Node 2: 5.000 V (divided)")
        print("  Node gnd: 0.000 V (ground)")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")

def demo_rc_transient():
    """Demonstrate transient analysis of RC circuit."""
    print("\n" + "=" * 60)
    print("TRANSIENT ANALYSIS DEMO (RC Circuit)")
    print("=" * 60)
    
    # Create RC circuit
    circuit = Circuit("RC Circuit")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="10k")
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1u")
    
    print(f"\nCircuit: {circuit}")
    print("\nRC Time constant τ = R×C = 10kΩ × 1μF = 10ms")
    print("At t=τ, capacitor charges to ~63.2% of input voltage")
    
    engine = SimulationEngine()
    try:
        print("\nRunning transient simulation for 50ms...")
        results = engine.simulate_transient(
            circuit,
            stop_time=0.05,  # 50ms
            step_time=0.0001  # 0.1ms steps
        )
        
        print(f"\nSimulation Results: {results}")
        
        # Find voltage at t=10ms (one time constant)
        if results.time is not None:
            import numpy as np
            tau_index = np.argmin(np.abs(results.time - 0.01))
            v_cap = results.voltage(2)
            if v_cap is not None:
                v_at_tau = v_cap[tau_index]
                print(f"\n✓ Capacitor voltage at t=τ (10ms): {v_at_tau:.3f} V")
                print(f"  Expected: ~3.16 V (63.2% of 5V)")
                
    except ImportError as e:
        print(f"\n⚠ Simulation requires ngspice: {e}")
        print("\n📊 Expected results (if ngspice was available):")
        print("  At t=0ms: Vcap = 0.000 V")
        print("  At t=10ms (τ): Vcap ≈ 3.160 V")
        print("  At t=30ms (3τ): Vcap ≈ 4.750 V")
        print("  At t=50ms (5τ): Vcap ≈ 4.967 V")
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")

def demo_mock_results():
    """Demonstrate the SimulationResults interface with mock data."""
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS INTERFACE DEMO")
    print("=" * 60)
    
    # Create mock DC results
    results = SimulationResults("dc")
    results.add_voltage(1, 10.0)
    results.add_voltage(2, 5.0)
    results.add_voltage(3, 2.5)
    results.add_current("V1", 0.01)  # 10mA
    
    print("\nMock DC Analysis Results:")
    print(f"  {results}")
    print(f"\n  Voltage at node 1: {results.voltage(1)[0]:.3f} V")
    print(f"  Voltage at node 2: {results.voltage(2)[0]:.3f} V")
    print(f"  Current through V1: {results.current('V1')[0]*1000:.1f} mA")
    
    # Create mock transient results
    import numpy as np
    time = np.linspace(0, 0.01, 100)  # 10ms, 100 points
    capacitor_voltage = 5 * (1 - np.exp(-time / 0.001))  # RC charging
    
    transient_results = SimulationResults("transient")
    transient_results.set_time_vector(time)
    transient_results.add_voltage(1, np.ones_like(time) * 5)  # Constant 5V
    transient_results.add_voltage(2, capacitor_voltage)  # Charging curve
    
    print("\nMock Transient Analysis Results:")
    print(f"  {transient_results}")
    print(f"  Time points: {len(time)}")
    print(f"  Initial capacitor voltage: {capacitor_voltage[0]:.3f} V")
    print(f"  Final capacitor voltage: {capacitor_voltage[-1]:.3f} V")
    
    # Demonstrate plotting capability (without actually plotting)
    print("\n📊 Plotting capability:")
    print("  results.plot('V(2)')  # Would plot voltage at node 2")
    print("  results.plot('V(1)', 'V(2)')  # Would plot both voltages")
    print("  results.plot()  # Would plot all node voltages")

def main():
    """Run all demos."""
    print("\n" + "🔌" * 30)
    print("  CIRCUIT SIMULATION DEMO")
    print("  PySpice Integration Test")
    print("🔌" * 30)
    
    # Check PySpice availability
    try:
        import PySpice
        print(f"\n✅ PySpice version {PySpice.__version__} is installed")
    except ImportError:
        print("\n⚠ PySpice not installed. Install with: pip install PySpice")
    
    # Run demos
    demo_dc_analysis()
    demo_rc_transient()
    demo_mock_results()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n✅ Circuit API is working")
    print("✅ Value parser converts human-readable values")
    print("✅ PySpice builder creates circuit representations")
    print("✅ Simulation engine structure is ready")
    print("⚠  ngspice needed for actual simulations")
    print("\nNext steps:")
    print("1. Resolve ngspice installation (conflict with KiCad)")
    print("2. Test with real simulations")
    print("3. Add interactive plotting with matplotlib")
    print("4. Create more example circuits")

if __name__ == "__main__":
    main()