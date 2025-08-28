#!/usr/bin/env python3
"""
Power Analysis Demo

Demonstrates power dissipation analysis capabilities including:
- Basic power calculations
- Component rating validation
- Power budget analysis
- MCP tool integration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.validation import PowerAnalyzer


def main():
    """Run power analysis demonstration."""
    print("🔋 Circuit Power Analysis Demo")
    print("=" * 40)

    # Create a voltage divider circuit
    circuit = Circuit("Power Analysis Demo")
    circuit.add_voltage_source("V1", 1, 0, "12V")
    circuit.add_resistor("R1", 1, 2, "1k")  # 1kΩ
    circuit.add_resistor("R2", 2, 0, "2k")  # 2kΩ
    circuit.add_resistor("R3", 1, 3, "500")  # 500Ω
    circuit.add_resistor("R4", 3, 0, "1k")  # 1kΩ

    print(f"\n📋 Circuit: {circuit.name}")
    print("Components:")
    for comp in circuit.components:
        comp_type = comp.get("type", "unknown")
        name = comp.get("name", "unnamed")
        if comp_type == "voltage_source":
            print(f"  {name}: {comp.get('dc_value', 'unknown')} voltage source")
        elif comp_type == "resistor":
            print(f"  {name}: {comp.get('resistance', 'unknown')}Ω resistor")

    # Simulate the circuit
    print("\n⚡ Running DC Simulation...")
    engine = SimulationEngine()

    try:
        results = engine.simulate_dc(circuit)
        print("✅ Simulation completed successfully")

        # Show node voltages
        print("\n📊 Node Voltages:")
        for node_id in results.nodes:
            voltage = results.voltage(node_id)
            if voltage is not None:
                print(f"  V({node_id}) = {voltage[0]:.3f}V")

        # Perform power analysis using built-in method
        print("\n🔋 Power Analysis:")
        power_analysis = results.analyze_power(circuit)

        print(f"Valid: {power_analysis.is_valid}")
        print(f"Total Power Dissipated: {power_analysis.total_power:.3f}W")

        # Show component power breakdown
        print("\n💡 Component Power Dissipation:")
        for name, info in power_analysis.component_power.items():
            print(
                f"  {name}: {info.power:.3f}W @ {info.voltage:.3f}V, {info.current:.3f}A ({info.method})"
            )

        # Show source power
        print("\n🔌 Source Power:")
        for name, info in power_analysis.source_power.items():
            supplying = "supplying" if info.power < 0 else "consuming"
            print(f"  {name}: {abs(info.power):.3f}W ({supplying})")

        # Show power budget
        budget = power_analysis.power_budget
        print("\n📈 Power Budget:")
        print(f"  Total Supplied: {budget['total_supplied']:.3f}W")
        print(f"  Total Dissipated: {budget['total_dissipated']:.3f}W")
        print(f"  Efficiency: {budget['efficiency']*100:.1f}%")
        print(f"  Power Balance: {budget['balance']:.6f}W")

        # Test with component ratings
        print("\n🏷️  Component Rating Validation:")
        component_ratings = {
            "R1": 0.25,  # 1/4W
            "R2": 0.5,  # 1/2W
            "R3": 1.0,  # 1W
            "R4": 0.125,  # 1/8W
        }

        # Create analyzer with custom thresholds
        analyzer = PowerAnalyzer(
            power_warning_threshold=0.1,  # 100mW warning
            power_error_threshold=2.0,  # 2W error
        )

        rating_analysis = analyzer.analyze_power(circuit, results, component_ratings)

        print(
            f"Rating Validation: {'✅ PASS' if rating_analysis.is_valid else '❌ FAIL'}"
        )

        for name, info in rating_analysis.component_power.items():
            rating = info.rating
            if rating:
                utilization = (info.power / rating) * 100
                status = (
                    "✅" if utilization < 80 else "⚠️" if utilization < 100 else "❌"
                )
                print(
                    f"  {name}: {info.power:.3f}W / {rating}W ({utilization:.1f}%) {status}"
                )

        # Show any issues
        if rating_analysis.issues:
            print("\n❌ Issues Found:")
            for issue in rating_analysis.issues:
                print(f"  - {issue.message}")
                if issue.suggestion:
                    print(f"    💡 {issue.suggestion}")

        if rating_analysis.warnings:
            print("\n⚠️  Warnings:")
            for warning in rating_analysis.warnings:
                print(f"  - {warning.message}")

        # Power optimization suggestions
        print("\n🔧 Power Optimization Tips:")
        if power_analysis.total_power > 1.0:
            print("  - Consider using higher resistance values to reduce power")
            print("  - Ensure adequate heat dissipation for high-power components")

        if budget["efficiency"] < 0.95:
            print("  - Check for unexpected power losses")

        max_component_power = max(
            [info.power for info in power_analysis.component_power.values()]
        )
        if max_component_power > 0.5:
            print(
                f"  - Component with highest power ({max_component_power:.3f}W) may need heat sink"
            )

        print("\n✨ Demo completed successfully!")
        print(f"   Circuit analyzed: {len(circuit.components)} components")
        print(f"   Power calculated: {len(power_analysis.component_power)} components")
        print(f"   Total power: {power_analysis.total_power:.3f}W")

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
