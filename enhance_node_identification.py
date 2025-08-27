#!/usr/bin/env python3
"""
Enhance Node Identification in Charts

Add intelligent node labeling that explains what each node represents in the circuit.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from circuit_sim import Circuit


def analyze_circuit_for_node_meanings(circuit: Circuit) -> dict:
    """Analyze circuit to determine what each node represents"""
    
    node_meanings = {
        0: {"label": "GND", "description": "Ground reference", "role": "reference"},
        "gnd": {"label": "GND", "description": "Ground reference", "role": "reference"}
    }
    
    # Track voltage sources (inputs)
    voltage_source_nodes = []
    
    # Track output patterns
    output_candidates = []
    
    for component in circuit.components:
        comp_type = component.get("type", "")
        name = component.get("name", "")
        
        if comp_type == "voltage_source":
            pos_node = component.get("positive")
            if pos_node not in [0, "gnd"]:
                voltage_source_nodes.append(pos_node)
                node_meanings[pos_node] = {
                    "label": f"VIN ({name})",
                    "description": f"Input from voltage source {name}",
                    "role": "input"
                }
        
        elif comp_type == "resistor":
            node1, node2 = component.get("node1"), component.get("node2")
            
            # If resistor connects to ground, the other node might be an output
            if node2 in [0, "gnd"] and node1 not in voltage_source_nodes:
                output_candidates.append(node1)
                
        elif comp_type == "capacitor":
            node1, node2 = component.get("node1"), component.get("node2")
            
            # Capacitor to ground often indicates filter output
            if node2 in [0, "gnd"] and node1 not in voltage_source_nodes:
                output_candidates.append(node1)
                node_meanings[node1] = {
                    "label": f"VOUT (before {name})",
                    "description": f"Filter output before {name} to ground",
                    "role": "output"
                }
    
    # Label remaining nodes
    for node in circuit.nodes:
        if node not in node_meanings and node not in [0, "gnd"]:
            if node in voltage_source_nodes:
                continue  # Already labeled
            elif node in output_candidates:
                if node not in node_meanings:
                    node_meanings[node] = {
                        "label": f"VOUT",
                        "description": "Circuit output", 
                        "role": "output"
                    }
            else:
                node_meanings[node] = {
                    "label": f"Node {node}",
                    "description": f"Intermediate circuit node",
                    "role": "intermediate"
                }
    
    return node_meanings


def demonstrate_improved_labeling():
    """Show how improved labeling would look"""
    
    circuits = {
        "RC Low-Pass Filter": lambda: Circuit("RC Low-Pass Filter")
            .add_voltage_source("V1", positive=1, negative="gnd", dc_value="1V")
            .add_resistor("R1", node1=1, node2=2, resistance="1k")
            .add_capacitor("C1", node1=2, node2="gnd", capacitance="1uF"),
        
        "Voltage Divider": lambda: Circuit("Voltage Divider")
            .add_voltage_source("V1", positive=1, negative="gnd", dc_value="10V")
            .add_resistor("R1", node1=1, node2=2, resistance="1k")
            .add_resistor("R2", node1=2, node2="gnd", resistance="1k"),
        
        "Pi Filter": lambda: Circuit("Pi Low-Pass Filter")
            .add_voltage_source("V1", positive=1, negative="gnd", dc_value="5V")
            .add_capacitor("C1", node1=1, node2="gnd", capacitance="10uF")
            .add_inductor("L1", node1=1, node2=2, inductance="1mH")
            .add_capacitor("C2", node1=2, node2="gnd", capacitance="10uF")
            .add_resistor("R_load", node1=2, node2="gnd", resistance="50"),
    }
    
    print("🏷️  Node Identification Examples")
    print("=" * 50)
    
    for circuit_name, circuit_func in circuits.items():
        circuit = circuit_func()
        meanings = analyze_circuit_for_node_meanings(circuit)
        
        print(f"\n📊 {circuit_name}:")
        print(f"   Components: {len(circuit.components)}, Nodes: {len(circuit.nodes)}")
        
        for node in sorted(circuit.nodes):
            if node in meanings:
                info = meanings[node]
                role_icon = {"input": "📥", "output": "📤", "intermediate": "🔗", "reference": "⚡"}
                icon = role_icon.get(info["role"], "📍")
                
                print(f"   {icon} {info['label']}: {info['description']}")
        
        print(f"   💡 For Bode plots: Focus on output nodes ({[k for k, v in meanings.items() if v.get('role') == 'output']})")


def create_chart_title_improvements():
    """Create examples of improved chart titles"""
    
    examples = {
        "Before": [
            "Bode Plot - V(Node 2)",
            "Magnitude - V(Node 2)", 
            "Phase - V(Node 2)"
        ],
        "After": [
            "Filter Output Response - V(Node 2)",
            "Output Magnitude - V(Node 2) [Filter Response]",
            "Output Phase - V(Node 2) [RC Time Constant Effect]"
        ]
    }
    
    print(f"\n🎨 Chart Title Improvements:")
    print(f"=" * 35)
    
    for category, titles in examples.items():
        print(f"\n{category}:")
        for title in titles:
            print(f"   {title}")
    
    print(f"\n📝 Additional Context Ideas:")
    print(f"   • Add circuit diagram annotation: 'Node 2: Between R1 and C1'")
    print(f"   • Show component values in title: 'RC Filter Output (R=1kΩ, C=1μF)'")
    print(f"   • Add expected behavior: 'Should show -20dB/decade rolloff'")
    print(f"   • Include cutoff frequency: 'fc = 159 Hz'")


if __name__ == "__main__":
    demonstrate_improved_labeling()
    create_chart_title_improvements()