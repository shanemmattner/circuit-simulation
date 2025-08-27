#!/usr/bin/env python3
"""
Improve Node Labeling in Reports

Add clear node identification that maps to circuit topology:
- Node 1: Input (voltage source positive terminal)  
- Node 2: Output (between R and C in RC filter)
- Node GND: Ground/reference

This makes reports much more usable for understanding results.
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit
from circuit_sim.simulator import SimulationEngine
from circuit_sim.reports import ReportGenerator


def analyze_circuit_topology(circuit: Circuit) -> dict:
    """Analyze circuit topology to create meaningful node labels"""
    
    node_info = {}
    
    # Analyze each component to understand node roles
    for component in circuit.components:
        comp_type = component.get("type", "unknown")
        
        if comp_type == "voltage_source":
            pos_node = component.get("positive")
            neg_node = component.get("negative")
            
            if pos_node and pos_node != 0 and pos_node != "gnd":
                node_info[pos_node] = {"role": "input", "description": "Voltage source positive (circuit input)"}
            if neg_node and neg_node != 0 and neg_node != "gnd":
                node_info[neg_node] = {"role": "reference", "description": "Voltage source negative"}
        
        elif comp_type in ["resistor", "capacitor", "inductor"]:
            node1 = component.get("node1")
            node2 = component.get("node2")
            
            # Try to identify output nodes (common patterns)
            for node in [node1, node2]:
                if node and node != 0 and node != "gnd":
                    if node not in node_info:
                        node_info[node] = {"role": "unknown", "description": "Circuit node"}
                    
                    # Update with component context
                    if comp_type == "capacitor" and node == node1:
                        # Often the node before a capacitor to ground is an output
                        if node2 == 0 or node2 == "gnd":
                            node_info[node]["role"] = "output" 
                            node_info[node]["description"] = f"Circuit output (before {component.get('name', 'C')} to ground)"
                    
                    elif comp_type == "resistor" and node == node2:
                        # Node between resistors could be output
                        if node not in [comp.get("positive") for comp in circuit.components if comp.get("type") == "voltage_source"]:
                            node_info[node]["role"] = "intermediate"
                            node_info[node]["description"] = f"Intermediate node (after {component.get('name', 'R')})"
    
    return node_info


def create_test_with_clear_labeling():
    """Create a test report with clear node labeling"""
    print("🏷️  Testing Clear Node Labeling")
    print("=" * 40)
    
    # RC Low-Pass Filter with clear topology
    circuit = Circuit("RC Low-Pass Filter")
    circuit.add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k") 
    circuit.add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF")
    
    print("📊 Circuit Topology:")
    print("   V1(1V) → Node 1 → R1(1k) → Node 2 → C1(1uF) → GND")
    print("   Node 1: Input (voltage source)")
    print("   Node 2: Output (filter output, before capacitor)")
    
    # Analyze topology
    topology = analyze_circuit_topology(circuit)
    print(f"\n🔍 Detected Topology:")
    for node, info in topology.items():
        print(f"   Node {node}: {info['role']} - {info['description']}")
    
    # Run simulation and check what nodes we get
    engine = SimulationEngine()
    
    try:
        ac_results = engine.simulate_ac(circuit, start_frequency=1, stop_frequency=10000, points_per_decade=20)
        print(f"\n📊 AC Simulation Results:")
        print(f"   Available nodes: {ac_results.nodes}")
        
        for node in ac_results.nodes:
            if node != 0:
                voltage = ac_results.voltage(node)
                if voltage is not None:
                    magnitude = abs(voltage[0])  # First frequency point
                    magnitude_db = 20 * np.log10(max(magnitude, 1e-12))
                    
                    # Get node description
                    node_desc = topology.get(node, {}).get("description", f"Node {node}")
                    role = topology.get(node, {}).get("role", "unknown")
                    
                    print(f"   Node {node} ({role}): {magnitude:.6f}V ({magnitude_db:.2f}dB)")
                    print(f"      Description: {node_desc}")
                    
                    # Provide interpretation
                    if role == "input":
                        print(f"      💡 This should be flat at 0dB (voltage source)")
                    elif role == "output":  
                        print(f"      💡 This should show filter response (interesting for Bode plot)")
                    
        return ac_results, topology
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return None, topology


def suggest_improved_chart_titles(topology: dict) -> dict:
    """Suggest better chart titles based on circuit topology"""
    
    suggestions = {}
    
    for node, info in topology.items():
        role = info["role"]
        description = info["description"]
        
        if role == "input":
            suggestions[node] = {
                "title": f"Input Response - Node {node}",
                "subtitle": "Voltage Source Output (should be flat)",
                "chart_priority": "low",  # Less interesting for AC analysis
            }
        elif role == "output":
            suggestions[node] = {
                "title": f"Filter Output - Node {node}", 
                "subtitle": "Circuit Response (shows filtering effect)",
                "chart_priority": "high",  # Most interesting for AC analysis
            }
        else:
            suggestions[node] = {
                "title": f"Node {node} Response",
                "subtitle": f"Intermediate circuit point", 
                "chart_priority": "medium",
            }
    
    return suggestions


def main():
    """Test improved node labeling"""
    print("🏷️  Node Labeling Improvement Test")
    print("=" * 50)
    
    # Test with RC filter
    ac_results, topology = create_test_with_clear_labeling()
    
    if ac_results:
        # Generate improved chart title suggestions
        chart_suggestions = suggest_improved_chart_titles(topology)
        
        print(f"\n📊 Chart Title Suggestions:")
        for node, suggestion in chart_suggestions.items():
            priority = suggestion["chart_priority"]
            priority_icon = {"high": "🎯", "medium": "📊", "low": "📉"}[priority]
            
            print(f"   {priority_icon} Node {node}: {suggestion['title']}")
            print(f"      Subtitle: {suggestion['subtitle']}")
            print(f"      Priority: {priority}")
        
        print(f"\n💡 Implementation Ideas:")
        print(f"   1. Use descriptive titles: 'Filter Output' instead of 'Node 2'")
        print(f"   2. Add node topology diagram to reports")  
        print(f"   3. Show component values in context: 'After R1(1k)'")
        print(f"   4. Prioritize interesting nodes for AC analysis")
        print(f"   5. Add hover tooltips explaining node significance")


if __name__ == "__main__":
    main()