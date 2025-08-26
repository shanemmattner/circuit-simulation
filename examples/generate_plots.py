#!/usr/bin/env python3
"""
Generate and save circuit simulation plots to files.
Run with: docker-compose run circuit-sim python3 examples/generate_plots.py
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files
import matplotlib.pyplot as plt

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine


def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs("examples/output", exist_ok=True)
    print("📁 Output directory: examples/output/")


def generate_voltage_divider():
    """Generate voltage divider DC analysis plot."""
    print("\n1️⃣  Generating Voltage Divider Plot...")
    
    # Create voltage divider
    circuit = (
        Circuit("Voltage Divider")
        .add_voltage_source("V1", 1, 0, "12V")
        .add_resistor("R1", 1, 2, "2.2k")
        .add_resistor("R2", 2, 3, "3.3k") 
        .add_resistor("R3", 3, 0, "4.7k")
    )
    
    # Simulate
    engine = SimulationEngine()
    results = engine.simulate_dc(circuit)
    
    # Create custom plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Bar chart of voltages
    nodes = [1, 2, 3]
    voltages = [results.voltage(n)[0] for n in nodes]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = ax1.bar([f"Node {n}" for n in nodes], voltages, color=colors)
    ax1.set_ylabel("Voltage (V)", fontsize=12)
    ax1.set_title("DC Operating Point - Voltage Divider", fontsize=14, fontweight='bold')
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.set_ylim(0, 13)
    
    # Add value labels on bars
    for bar, v in zip(bars, voltages):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{v:.2f}V', ha='center', va='bottom', fontweight='bold')
    
    # Circuit diagram representation
    ax2.axis('off')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("Circuit Diagram", fontsize=14, fontweight='bold')
    
    # Draw circuit schematic
    ax2.text(5, 9, "12V", ha='center', fontsize=12, fontweight='bold')
    ax2.plot([5, 5], [8.5, 7.5], 'ko-', linewidth=2)
    ax2.text(6, 7, "R1=2.2kΩ", fontsize=10)
    ax2.plot([5, 5], [7.5, 5.5], 'r-', linewidth=3)
    ax2.plot([5, 5], [5.5, 3.5], 'r-', linewidth=3)
    ax2.text(6, 5, f"Node 2: {voltages[1]:.2f}V", fontsize=10, color='blue')
    ax2.text(6, 3, "R2=3.3kΩ", fontsize=10)
    ax2.plot([5, 5], [3.5, 1.5], 'r-', linewidth=3)
    ax2.text(6, 1, "R3=4.7kΩ", fontsize=10)
    ax2.plot([4, 6], [0.5, 0.5], 'k-', linewidth=2)
    ax2.plot([4.5, 5.5], [0.3, 0.3], 'k-', linewidth=1)
    ax2.plot([4.7, 5.3], [0.1, 0.1], 'k-', linewidth=0.5)
    
    plt.tight_layout()
    output_file = "examples/output/voltage_divider.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {output_file}")
    
    return output_file


def generate_rc_charging():
    """Generate RC circuit charging curve."""
    print("\n2️⃣  Generating RC Charging Curve...")
    
    # Create RC circuit
    circuit = (
        Circuit("RC Circuit")
        .add_voltage_source("V1", 1, 0, "5V")
        .add_resistor("R1", 1, 2, "10k")
        .add_capacitor("C1", 2, 0, "10u")  # 10uF
    )
    
    # Simulate for 200ms
    engine = SimulationEngine()
    results = engine.simulate_transient(circuit, stop_time=0.2, step_time=0.0001)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if results.time is not None and results.voltage(2) is not None:
        time_ms = results.time * 1000  # Convert to milliseconds
        voltage = results.voltage(2)
        
        # Plot charging curve
        ax.plot(time_ms, voltage, 'b-', linewidth=2, label='Capacitor Voltage')
        
        # Mark time constant
        tau = 10e3 * 10e-6  # R * C = 10k * 10uF = 100ms
        tau_ms = tau * 1000
        v_at_tau = 5 * (1 - 1/np.e)  # 63.2% of 5V
        
        ax.axvline(tau_ms, color='r', linestyle='--', alpha=0.5, label=f'τ = {tau_ms:.0f}ms')
        ax.axhline(v_at_tau, color='g', linestyle='--', alpha=0.5, label=f'V(τ) = {v_at_tau:.2f}V')
        ax.axhline(5, color='gray', linestyle='--', alpha=0.3, label='V_final = 5V')
        
        # Add annotations
        ax.annotate('63.2% of final voltage', 
                   xy=(tau_ms, v_at_tau), xytext=(tau_ms + 20, v_at_tau - 0.5),
                   arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
        
        ax.set_xlabel("Time (ms)", fontsize=12)
        ax.set_ylabel("Voltage (V)", fontsize=12)
        ax.set_title("RC Circuit Charging Curve (R=10kΩ, C=10µF)", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right')
        ax.set_xlim(0, 200)
        ax.set_ylim(0, 5.5)
    
    output_file = "examples/output/rc_charging.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {output_file}")
    
    return output_file


def generate_rl_response():
    """Generate RL circuit current response."""
    print("\n3️⃣  Generating RL Circuit Response...")
    
    # Create RL circuit
    circuit = (
        Circuit("RL Circuit")
        .add_voltage_source("V1", 1, 0, "12V")
        .add_resistor("R1", 1, 2, "100")
        .add_inductor("L1", 2, 0, "50m")  # 50mH
    )
    
    # Simulate
    engine = SimulationEngine()
    results = engine.simulate_transient(circuit, stop_time=0.003, step_time=0.000005)
    
    # Create plot with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    if results.time is not None:
        time_ms = results.time * 1000
        
        # Plot inductor voltage
        if results.voltage(2) is not None:
            ax1.plot(time_ms, results.voltage(2), 'b-', linewidth=2)
            ax1.set_ylabel("Inductor Voltage (V)", fontsize=12)
            ax1.set_title("RL Circuit Response (R=100Ω, L=50mH)", fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Mark time constant
            tau = 0.05 / 100  # L/R = 50mH / 100Ω = 0.5ms
            ax1.axvline(tau * 1000, color='r', linestyle='--', alpha=0.5, label=f'τ = {tau*1000:.1f}ms')
            ax1.legend()
        
        # Plot current (from voltage source)
        if results.current("V1") is not None:
            current_ma = -results.current("V1") * 1000  # Convert to mA and flip sign
            ax2.plot(time_ms, current_ma, 'r-', linewidth=2)
            ax2.set_xlabel("Time (ms)", fontsize=12)
            ax2.set_ylabel("Current (mA)", fontsize=12)
            ax2.set_title("Circuit Current", fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            # Show steady state
            i_ss = 12 / 100 * 1000  # V/R in mA
            ax2.axhline(i_ss, color='g', linestyle='--', alpha=0.5, label=f'I_steady = {i_ss:.0f}mA')
            ax2.axvline(tau * 1000, color='r', linestyle='--', alpha=0.5, label=f'τ = {tau*1000:.1f}ms')
            ax2.legend()
    
    plt.tight_layout()
    output_file = "examples/output/rl_response.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {output_file}")
    
    return output_file


def generate_rc_filter():
    """Generate RC low-pass filter frequency response (mock data)."""
    print("\n4️⃣  Generating RC Filter Response (Mock)...")
    
    # Since AC analysis isn't implemented, we'll create a mock frequency response
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Generate frequency points
    freq = np.logspace(1, 6, 200)  # 10 Hz to 1 MHz
    
    # Calculate theoretical RC filter response
    R = 1000  # 1kΩ
    C = 100e-9  # 100nF
    fc = 1 / (2 * np.pi * R * C)  # Cutoff frequency
    
    # Magnitude response
    H_mag = 1 / np.sqrt(1 + (freq / fc) ** 2)
    H_db = 20 * np.log10(H_mag)
    
    # Phase response
    H_phase = -np.arctan(freq / fc) * 180 / np.pi
    
    # Plot magnitude
    ax1.semilogx(freq, H_db, 'b-', linewidth=2)
    ax1.axvline(fc, color='r', linestyle='--', alpha=0.5, label=f'f_c = {fc:.0f} Hz')
    ax1.axhline(-3, color='g', linestyle='--', alpha=0.5, label='-3 dB point')
    ax1.set_ylabel("Magnitude (dB)", fontsize=12)
    ax1.set_title(f"RC Low-Pass Filter (R={R}Ω, C={C*1e9:.0f}nF)", fontsize=14, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.legend()
    ax1.set_ylim(-60, 5)
    
    # Plot phase
    ax2.semilogx(freq, H_phase, 'r-', linewidth=2)
    ax2.axvline(fc, color='r', linestyle='--', alpha=0.5, label=f'f_c = {fc:.0f} Hz')
    ax2.axhline(-45, color='g', linestyle='--', alpha=0.5, label='-45° at f_c')
    ax2.set_xlabel("Frequency (Hz)", fontsize=12)
    ax2.set_ylabel("Phase (degrees)", fontsize=12)
    ax2.set_title("Phase Response", fontsize=12)
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend()
    ax2.set_ylim(-95, 5)
    
    plt.tight_layout()
    output_file = "examples/output/rc_filter.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {output_file}")
    
    return output_file


def generate_comparison_plot():
    """Generate comparison of different RC time constants."""
    print("\n5️⃣  Generating RC Time Constant Comparison...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Different RC combinations
    rc_configs = [
        ("1kΩ, 1µF", 1e3, 1e-6, '#FF6B6B'),
        ("10kΩ, 1µF", 10e3, 1e-6, '#4ECDC4'),
        ("10kΩ, 10µF", 10e3, 10e-6, '#45B7D1'),
        ("100kΩ, 10µF", 100e3, 10e-6, '#96CEB4'),
    ]
    
    for name, R, C, color in rc_configs:
        # Create circuit
        circuit = (
            Circuit(f"RC {name}")
            .add_voltage_source("V1", 1, 0, "5V")
            .add_resistor("R1", 1, 2, f"{R}")
            .add_capacitor("C1", 2, 0, f"{C}")
        )
        
        # Simulate
        engine = SimulationEngine()
        tau = R * C
        stop_time = min(5 * tau, 2.0)  # 5 time constants or 2 seconds max
        results = engine.simulate_transient(circuit, stop_time=stop_time, step_time=stop_time/500)
        
        if results.time is not None and results.voltage(2) is not None:
            time_ms = results.time * 1000
            voltage = results.voltage(2)
            ax.plot(time_ms, voltage, linewidth=2, label=f'{name} (τ={tau*1000:.1f}ms)', color=color)
    
    ax.axhline(5 * 0.632, color='gray', linestyle='--', alpha=0.3, label='63.2% of 5V')
    ax.set_xlabel("Time (ms)", fontsize=12)
    ax.set_ylabel("Voltage (V)", fontsize=12)
    ax.set_title("RC Circuit Charging: Time Constant Comparison", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 5.5)
    
    output_file = "examples/output/rc_comparison.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {output_file}")
    
    return output_file


def main():
    """Generate all plots."""
    print("=" * 60)
    print("🎨 Circuit Simulation Plot Generator")
    print("=" * 60)
    
    ensure_output_dir()
    
    plots = []
    
    try:
        plots.append(generate_voltage_divider())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        plots.append(generate_rc_charging())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        plots.append(generate_rl_response())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        plots.append(generate_rc_filter())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    try:
        plots.append(generate_comparison_plot())
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Plot Generation Complete!")
    print("=" * 60)
    print("\nGenerated plots:")
    for plot in plots:
        if plot:
            print(f"  • {plot}")
    
    print("\nTo view the plots, run:")
    print("  xdg-open examples/output/")
    print("\nOr view individual files:")
    for plot in plots:
        if plot:
            print(f"  xdg-open {plot}")


if __name__ == "__main__":
    main()