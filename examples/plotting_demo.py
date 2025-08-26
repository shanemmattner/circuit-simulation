#!/usr/bin/env python3
"""
Demonstration of plotting capabilities for circuit simulations.

This script shows how to visualize simulation results using the built-in
plotting functionality.
"""

import numpy as np
import matplotlib.pyplot as plt
from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def demo_dc_plot():
    """Demonstrate DC analysis plotting."""
    print("\n=== DC Analysis Plot ===")
    
    # Create voltage divider
    circuit = (
        Circuit("Voltage Divider")
        .add_voltage_source("V1", 1, 0, "10V")
        .add_resistor("R1", 1, 2, "2k")
        .add_resistor("R2", 2, 3, "3k") 
        .add_resistor("R3", 3, 0, "5k")
    )
    
    # Simulate
    engine = SimulationEngine()
    results = engine.simulate_dc(circuit)
    
    # Plot all node voltages
    results.plot()
    
    print(f"Node voltages:")
    for node in results.nodes:
        v = results.voltage(node)
        if v is not None:
            print(f"  V({node}) = {v[0]:.3f}V")


def demo_transient_plot():
    """Demonstrate transient analysis plotting."""
    print("\n=== Transient Analysis Plot ===")
    
    # Create RC circuit
    circuit = (
        Circuit("RC Circuit")
        .add_voltage_source("V1", 1, 0, "5V")
        .add_resistor("R1", 1, 2, "10k")
        .add_capacitor("C1", 2, 0, "1u")
    )
    
    # Simulate for 50ms
    engine = SimulationEngine()
    results = engine.simulate_transient(circuit, stop_time=0.05, step_time=0.0001)
    
    # Plot capacitor voltage
    results.plot("V(2)")
    
    # Calculate time constant
    tau = 10e3 * 1e-6  # R * C = 10k * 1uF = 10ms
    print(f"Time constant τ = RC = {tau*1000:.1f}ms")
    print(f"At t=τ, V_C should be {5 * (1 - 1/np.e):.3f}V (63.2% of 5V)")
    
    # Find voltage at t=tau
    if results.time is not None and results.voltage(2) is not None:
        idx = np.argmin(np.abs(results.time - tau))
        v_at_tau = results.voltage(2)[idx]
        print(f"Simulated V_C at t=τ: {v_at_tau:.3f}V")


def demo_multiple_signals():
    """Demonstrate plotting multiple signals."""
    print("\n=== Multiple Signals Plot ===")
    
    # Create circuit with multiple nodes
    circuit = (
        Circuit("Multi-Stage Filter")
        .add_voltage_source("V1", 1, 0, "10V")
        .add_resistor("R1", 1, 2, "1k")
        .add_capacitor("C1", 2, 0, "100n")
        .add_resistor("R2", 2, 3, "2k")
        .add_capacitor("C2", 3, 0, "47n")
    )
    
    # Simulate transient
    engine = SimulationEngine()
    results = engine.simulate_transient(circuit, stop_time=0.001, step_time=0.000001)
    
    # Plot multiple voltages on same graph
    results.plot("V(2)", "V(3)")
    
    print("Plotted V(2) and V(3) showing two-stage RC filter response")


def demo_custom_plot():
    """Demonstrate custom plotting with matplotlib."""
    print("\n=== Custom Plot with Matplotlib ===")
    
    # Create RL circuit
    circuit = (
        Circuit("RL Circuit")
        .add_voltage_source("V1", 1, 0, "12V")
        .add_resistor("R1", 1, 2, "100")
        .add_inductor("L1", 2, 0, "100m")  # 100mH
    )
    
    # Simulate
    engine = SimulationEngine()
    results = engine.simulate_transient(circuit, stop_time=0.005, step_time=0.00001)
    
    # Custom plot with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot voltage
    if results.time is not None and results.voltage(2) is not None:
        ax1.plot(results.time * 1000, results.voltage(2), 'b-', linewidth=2)
        ax1.set_xlabel("Time (ms)")
        ax1.set_ylabel("Voltage (V)")
        ax1.set_title("RL Circuit - Inductor Voltage")
        ax1.grid(True, alpha=0.3)
        
        # Calculate theoretical time constant
        tau = 0.1 / 100  # L/R = 100mH / 100Ω = 1ms
        ax1.axvline(tau * 1000, color='r', linestyle='--', alpha=0.5, label=f'τ = {tau*1000:.1f}ms')
        ax1.legend()
    
    # Plot current (if available)
    if results.current("V1") is not None:
        ax2.plot(results.time * 1000, -results.current("V1") * 1000, 'r-', linewidth=2)
        ax2.set_xlabel("Time (ms)")
        ax2.set_ylabel("Current (mA)")
        ax2.set_title("RL Circuit - Circuit Current")
        ax2.grid(True, alpha=0.3)
        
        # Show steady state current
        i_ss = 12 / 100  # V/R = 12V / 100Ω = 120mA
        ax2.axhline(i_ss * 1000, color='g', linestyle='--', alpha=0.5, label=f'I_steady = {i_ss*1000:.0f}mA')
        ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    print(f"RL time constant τ = L/R = 1ms")
    print(f"Steady-state current = V/R = 120mA")


def demo_save_plots():
    """Demonstrate saving plots to files."""
    print("\n=== Saving Plots to Files ===")
    
    # Create simple circuit
    circuit = (
        Circuit("Test Circuit")
        .add_voltage_source("V1", 1, 0, "3.3V")
        .add_resistor("R1", 1, 2, "470")
        .add_resistor("R2", 2, 0, "1k")
    )
    
    # Simulate
    engine = SimulationEngine()
    results = engine.simulate_dc(circuit)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot as bar chart for DC
    nodes = [n for n in results.nodes if n != 0]
    voltages = [results.voltage(n)[0] for n in nodes]
    
    bars = ax.bar([f"Node {n}" for n in nodes], voltages, color=['blue', 'green'])
    ax.set_ylabel("Voltage (V)")
    ax.set_title("DC Operating Point")
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, v in zip(bars, voltages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{v:.3f}V', ha='center', va='bottom')
    
    # Save to file
    output_file = "examples/output/dc_analysis.png"
    import os
    os.makedirs("examples/output", exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    plt.show()


def main():
    """Run all plotting demonstrations."""
    import sys
    import os
    
    # Set matplotlib backend for non-interactive environments
    if os.environ.get('DISPLAY') is None:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
    
    print("=" * 60)
    print("Circuit Simulation Plotting Demonstrations")
    print("=" * 60)
    
    # Check if running interactively
    interactive = sys.stdin.isatty()
    
    demos = [
        ("DC Analysis", demo_dc_plot),
        ("Transient Analysis", demo_transient_plot),
        ("Multiple Signals", demo_multiple_signals),
        ("Custom Matplotlib", demo_custom_plot),
        ("Save to File", demo_save_plots),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        print(f"\n{i}. {name}")
        print("-" * 40)
        try:
            func()
            print("✓ Demo completed successfully")
        except Exception as e:
            print(f"✗ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos) and interactive:
            input("\nPress Enter to continue to next demo...")
    
    print("\n" + "=" * 60)
    print("All plotting demonstrations complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()