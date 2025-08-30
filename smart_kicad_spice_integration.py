#!/usr/bin/env python3
"""
Smart KiCad-Spice Integration using KiCad-Spice-Library
Much more scalable than hardcoded component mappings.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Set

KICAD_SPICE_LIBRARY = Path("/Users/shanemattner/Desktop/circuit-simulation/submodules/KiCad-Spice-Library")

class SmartSpiceMapper:
    """Maps KiCad components to SPICE models using KiCad-Spice-Library."""
    
    def __init__(self):
        self.supported_models: Set[str] = set()
        self.load_supported_models()
    
    def load_supported_models(self):
        """Load all supported SPICE model names."""
        supported_file = KICAD_SPICE_LIBRARY / "Supported.txt"
        if supported_file.exists():
            with open(supported_file, 'r') as f:
                self.supported_models = {line.strip().lower() for line in f}
            print(f"📚 Loaded {len(self.supported_models)} SPICE models")
        else:
            print("⚠️  KiCad-Spice-Library not found - falling back to basic models")
    
    def find_spice_model(self, value: str, symbol: str, ref: str) -> Optional[str]:
        """Smart SPICE model lookup based on component info."""
        
        # 1. Try value field first (most reliable)
        if value and value.lower() in self.supported_models:
            return value
        
        # 2. Extract model from value field patterns
        model_patterns = [
            r'([A-Z0-9]+)',        # BC546, 2N3904, LM358
            r'([0-9]+[A-Z][0-9]+)', # 2N3904, 1N4148  
            r'(LM[0-9]+)',         # LM358, LM741
            r'(BC[0-9]+[A-Z]?)',   # BC546B, BC547
            r'([0-9]+N[0-9]+)',    # 1N4148, 2N7000
        ]
        
        for pattern in model_patterns:
            if value:
                match = re.search(pattern, value.upper())
                if match and match.group(1).lower() in self.supported_models:
                    return match.group(1)
        
        # 3. Extract from symbol name
        symbol_patterns = {
            'Device:Q_NPN_CBE': ['2N3904', 'BC546B', '2N2222'],      # NPN defaults
            'Device:Q_PNP_CBE': ['2N3906', 'BC556B', '2N2907'],      # PNP defaults  
            'Device:D': ['1N4148', '1N4007', 'LED_Red'],             # Diode defaults
            'Amplifier_Operational:LM358': ['LM358'],                # Op-amp specific
            'Device:Q_NMOS_GDS': ['2N7000', 'BS250', 'IRF540'],     # NMOS defaults
            'Device:Q_PMOS_GDS': ['BS250', 'IRF9540'],              # PMOS defaults
        }
        
        if symbol in symbol_patterns:
            for candidate in symbol_patterns[symbol]:
                if candidate.lower() in self.supported_models:
                    return candidate
        
        # 4. Generic defaults based on component type
        generic_defaults = {
            'D': 'DefaultDiode',
            'Q': 'DefaultNPN' if 'NPN' in symbol else 'DefaultPNP',
            'U': 'LM358',  # Op-amp reference
        }
        
        if ref and ref[0] in generic_defaults:
            return generic_defaults[ref[0]]
            
        return None
    
    def get_spice_lib_path(self, model_name: str) -> Optional[Path]:
        """Find the .lib file for a specific SPICE model."""
        if not model_name:
            return None
            
        # Search in Models directory
        for lib_file in KICAD_SPICE_LIBRARY.glob("Models/**/*.lib"):
            with open(lib_file, 'r', errors='ignore') as f:
                content = f.read().lower()
                if f".model {model_name.lower()}" in content:
                    return lib_file
        return None


def enhanced_convert_to_circuit(json_data: Dict) -> 'Circuit':
    """Enhanced circuit conversion using smart SPICE model mapping."""
    from circuit_sim.circuit import Circuit
    
    circuit = Circuit(json_data["name"])
    mapper = SmartSpiceMapper()
    
    for comp_name, comp_data in json_data["components"].items():
        symbol = comp_data["symbol"]
        value = comp_data.get("value", "")
        ref = comp_data.get("ref", comp_name)
        
        pins = _get_component_pins(comp_name, json_data["nets"])
        
        # Basic components (no SPICE model needed)
        if symbol == "Device:R" and len(pins) >= 2:
            circuit.add_resistor(comp_name, pins[0], pins[1], value)
            
        elif symbol == "Device:C" and len(pins) >= 2:
            circuit.add_capacitor(comp_name, pins[0], pins[1], value)
            
        elif symbol == "Device:L" and len(pins) >= 2:
            circuit.add_inductor(comp_name, pins[0], pins[1], value)
            
        elif symbol == "Device:V" and len(pins) >= 2:
            circuit.add_voltage_source(comp_name, pins[0], pins[1], value)
        
        # Complex components (SPICE model needed)
        elif symbol == "Device:D" and len(pins) >= 2:
            model = mapper.find_spice_model(value, symbol, ref)
            if model:
                circuit.add_diode(comp_name, pins[0], pins[1], model)
                print(f"🔍 Mapped {comp_name} → SPICE model: {model}")
            else:
                print(f"⚠️  No SPICE model found for diode {comp_name} ({value})")
                
        elif "Q_NPN_CBE" in symbol and len(pins) >= 3:
            model = mapper.find_spice_model(value, symbol, ref)
            if model:
                circuit.add_bjt_transistor(comp_name, pins[0], pins[1], pins[2], 
                                         transistor_type="NPN", model=model)
                print(f"🔍 Mapped {comp_name} → SPICE model: {model}")
            else:
                print(f"⚠️  No SPICE model found for NPN {comp_name} ({value})")
                
        elif "Q_PNP_CBE" in symbol and len(pins) >= 3:
            model = mapper.find_spice_model(value, symbol, ref)
            if model:
                circuit.add_bjt_transistor(comp_name, pins[0], pins[1], pins[2],
                                         transistor_type="PNP", model=model)
                print(f"🔍 Mapped {comp_name} → SPICE model: {model}")
            else:
                print(f"⚠️  No SPICE model found for PNP {comp_name} ({value})")
                
        elif "Amplifier" in symbol and len(pins) >= 5:
            model = mapper.find_spice_model(value, symbol, ref)
            if model:
                # Assuming pins: [out, in-, in+, V+, V-]
                circuit.add_opamp(comp_name, pins[0], pins[1], pins[2], pins[3], pins[4], model)
                print(f"🔍 Mapped {comp_name} → SPICE model: {model}")
            else:
                print(f"⚠️  No SPICE model found for op-amp {comp_name} ({value})")
        
        else:
            print(f"🔄 Skipped unsupported component {comp_name} ({symbol})")
    
    return circuit


def _get_component_pins(comp_name: str, nets: Dict) -> list:
    """Get the pin connections for a component (from integration layer)."""
    pin_to_net = {}
    
    for net_name, connections in nets.items():
        for connection in connections:
            if connection["component"] == comp_name:
                pin_data = connection["pin"]
                
                if isinstance(pin_data, dict):
                    pin_num = pin_data["number"]
                else:
                    pin_num = pin_data
                
                pin_to_net[pin_num] = net_name
    
    pins = []
    for pin_num in sorted(pin_to_net.keys()):
        pins.append(pin_to_net[pin_num])
    
    return pins


if __name__ == "__main__":
    # Demo the smart mapper
    mapper = SmartSpiceMapper()
    
    test_components = [
        ("BC546B", "Device:Q_NPN_CBE", "Q1"),
        ("1N4148", "Device:D", "D1"), 
        ("LM358", "Amplifier_Operational:LM358", "U1"),
        ("2N7000", "Device:Q_NMOS_GDS", "Q2"),
        ("unknown_part", "Device:D", "D2"),
    ]
    
    print("🧪 Smart SPICE Model Mapping Demo")
    print("=" * 50)
    
    for value, symbol, ref in test_components:
        model = mapper.find_spice_model(value, symbol, ref)
        status = "✅" if model else "❌"
        print(f"{status} {ref} ({value}) → {model or 'No model found'}")