# Feature: SPICE Netlist Import/Export

## 🎯 Objective
Implement universal circuit format support for importing and exporting netlists from major SPICE variants and EDA tools, enabling interoperability with existing design workflows.

## 📋 Requirements

### Import Support
- [ ] **SPICE Formats**
  - Standard SPICE (.cir, .sp)
  - PSpice (.cir)
  - HSPICE (.sp)
  - Spectre (.scs)
- [ ] **EDA Tool Formats**
  - KiCad (.net)
  - LTSpice (.asc)
  - Qucs (.sch)
  - gEDA (.sch)

### Export Support
- [ ] Standard SPICE netlist
- [ ] Spectre format
- [ ] Verilog-A behavioral models
- [ ] KiCad-compatible format
- [ ] Python circuit definition

### Parser Features
- [ ] Component model extraction
- [ ] Subcircuit definitions
- [ ] Parameter handling
- [ ] Include file resolution
- [ ] Error reporting with line numbers
- [ ] Syntax validation

## 🛠️ Technical Implementation

### File Structure
```
src/io/
├── __init__.py
├── parsers/
│   ├── spice_parser.py      # Standard SPICE
│   ├── pspice_parser.py     # PSpice format
│   ├── ltspice_parser.py    # LTSpice ASC
│   ├── kicad_parser.py      # KiCad netlist
│   └── base_parser.py       # Common parser base
├── exporters/
│   ├── spice_exporter.py    # Standard SPICE
│   ├── spectre_exporter.py  # Cadence Spectre
│   ├── verilog_exporter.py  # Verilog-A
│   └── python_exporter.py   # Python code
├── models/
│   ├── netlist.py          # Netlist data structure
│   ├── component.py        # Component definitions
│   └── subcircuit.py       # Subcircuit handling
└── utils/
    ├── tokenizer.py        # SPICE tokenization
    ├── unit_parser.py      # Value parsing
    └── model_library.py    # Component models
```

### SPICE Parser Implementation
```python
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class NetlistComponent:
    name: str
    type: str
    nodes: List[str]
    value: Optional[str] = None
    model: Optional[str] = None
    parameters: Dict[str, str] = None

class SPICEParser:
    """Parse SPICE netlist files."""
    
    def __init__(self):
        self.components = []
        self.models = {}
        self.subcircuits = {}
        self.parameters = {}
        
    def parse_file(self, filepath: str) -> 'Netlist':
        """Parse a SPICE netlist file."""
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Preprocess: handle line continuations
        processed_lines = self._handle_continuations(lines)
        
        # Parse each line
        for line_num, line in enumerate(processed_lines, 1):
            try:
                self._parse_line(line.strip(), line_num)
            except Exception as e:
                raise ParseError(f"Line {line_num}: {e}")
        
        return Netlist(
            components=self.components,
            models=self.models,
            subcircuits=self.subcircuits,
            parameters=self.parameters
        )
    
    def _parse_line(self, line: str, line_num: int):
        """Parse a single SPICE line."""
        if not line or line.startswith('*'):
            return  # Skip comments and empty lines
        
        # Title line (first non-comment line)
        if line_num == 1:
            self.title = line
            return
        
        # Control statements
        if line.startswith('.'):
            self._parse_control_statement(line)
            return
        
        # Component definitions
        first_char = line[0].upper()
        
        if first_char == 'R':
            self._parse_resistor(line)
        elif first_char == 'C':
            self._parse_capacitor(line)
        elif first_char == 'L':
            self._parse_inductor(line)
        elif first_char == 'V':
            self._parse_voltage_source(line)
        elif first_char == 'I':
            self._parse_current_source(line)
        elif first_char in ['Q', 'M']:
            self._parse_transistor(line)
        elif first_char == 'D':
            self._parse_diode(line)
        elif first_char == 'X':
            self._parse_subcircuit_call(line)
        else:
            raise ParseError(f"Unknown component type: {first_char}")
    
    def _parse_resistor(self, line: str):
        """Parse resistor definition: R<name> n1 n2 <value>"""
        tokens = line.split()
        if len(tokens) < 4:
            raise ParseError("Resistor requires name, two nodes, and value")
        
        name = tokens[0]
        node1, node2 = tokens[1], tokens[2]
        value = tokens[3]
        
        # Handle model-based resistors
        model = tokens[4] if len(tokens) > 4 else None
        
        component = NetlistComponent(
            name=name,
            type='resistor',
            nodes=[node1, node2],
            value=value,
            model=model
        )
        
        self.components.append(component)
    
    def _parse_control_statement(self, line: str):
        """Parse SPICE control statements."""
        tokens = line.split()
        command = tokens[0].lower()
        
        if command == '.model':
            self._parse_model_definition(line)
        elif command == '.param':
            self._parse_parameter_definition(line)
        elif command == '.subckt':
            self._parse_subcircuit_definition(line)
        elif command == '.include':
            self._parse_include_statement(line)
        elif command in ['.dc', '.ac', '.tran', '.op']:
            self._parse_analysis_statement(line)
        elif command == '.end':
            return  # End of netlist
        
    def _parse_model_definition(self, line: str):
        """Parse .MODEL statement."""
        # .MODEL DNAME DTYPE(PNAME1=VAL1 PNAME2=VAL2 ...)
        tokens = line.split()
        if len(tokens) < 3:
            raise ParseError("Model definition incomplete")
        
        model_name = tokens[1]
        model_type = tokens[2]
        
        # Extract parameters
        params = {}
        if len(tokens) > 3:
            param_str = ' '.join(tokens[3:])
            params = self._parse_parameter_list(param_str)
        
        self.models[model_name] = {
            'type': model_type,
            'parameters': params
        }
    
    def _handle_continuations(self, lines: List[str]) -> List[str]:
        """Handle SPICE line continuations (+)."""
        processed = []
        current_line = ""
        
        for line in lines:
            line = line.rstrip('\n\r')
            
            if line.startswith('+') and current_line:
                # Continuation line
                current_line += ' ' + line[1:].strip()
            else:
                if current_line:
                    processed.append(current_line)
                current_line = line
        
        if current_line:
            processed.append(current_line)
        
        return processed

class CircuitImporter:
    """High-level interface for importing circuits."""
    
    def __init__(self):
        self.parsers = {
            '.cir': SPICEParser,
            '.sp': SPICEParser,
            '.asc': LTSpiceParser,
            '.net': KiCadParser,
            '.sch': QucsParser
        }
    
    def import_circuit(self, filepath: str) -> Circuit:
        """Import circuit from various formats."""
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext not in self.parsers:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        parser = self.parsers[file_ext]()
        netlist = parser.parse_file(filepath)
        
        # Convert to internal Circuit format
        circuit = self._convert_to_circuit(netlist)
        
        return circuit
    
    def _convert_to_circuit(self, netlist: Netlist) -> Circuit:
        """Convert netlist to Circuit object."""
        circuit = Circuit(name=netlist.title or "Imported Circuit")
        
        for component in netlist.components:
            if component.type == 'resistor':
                circuit.add_resistor(
                    component.name,
                    component.nodes[0],
                    component.nodes[1],
                    component.value
                )
            elif component.type == 'capacitor':
                circuit.add_capacitor(
                    component.name,
                    component.nodes[0],
                    component.nodes[1],
                    component.value
                )
            # ... handle other component types
        
        return circuit
```

### Export Implementation
```python
class SPICEExporter:
    """Export Circuit to SPICE netlist format."""
    
    def export_circuit(self, circuit: Circuit, filepath: str):
        """Export circuit to SPICE netlist."""
        with open(filepath, 'w') as f:
            # Title line
            f.write(f"* {circuit.name}\n")
            f.write(f"* Generated by circuit-simulation library\n")
            f.write(f"* {datetime.now().isoformat()}\n\n")
            
            # Components
            for component in circuit.components:
                spice_line = self._component_to_spice(component)
                f.write(f"{spice_line}\n")
            
            # Analysis commands
            f.write("\n* Analysis\n")
            f.write(".OP\n")
            f.write(".END\n")
    
    def _component_to_spice(self, component) -> str:
        """Convert component to SPICE line."""
        if component.type == 'resistor':
            return f"{component.name} {component.pos} {component.neg} {component.value}"
        elif component.type == 'capacitor':
            return f"{component.name} {component.pos} {component.neg} {component.value}"
        # ... handle other types
```

## 📊 Success Criteria
- [ ] Parse 95% of standard SPICE files correctly
- [ ] Handle all common component types
- [ ] Preserve component parameters
- [ ] Generate valid netlists
- [ ] Error messages are helpful
- [ ] Performance: <1s for 1000 components

## 🔗 Dependencies
- Depends on: Core circuit API
- Blocks: None  
- Related: #2 (Examples can be imported), #3 (API file upload)

## 📚 Resources
- [SPICE Reference](http://bwrcs.eecs.berkeley.edu/Classes/IcBook/SPICE/)
- [KiCad File Formats](https://www.kicad.org/help/file-formats/)
- [LTSpice Documentation](https://www.analog.com/ltspice)

## ✅ Acceptance Criteria
1. Successfully imports example files from each format
2. Exported netlists simulate in external tools
3. Error handling is robust
4. Component models are preserved
5. Performance requirements met

## 🏷️ Labels
`enhancement` `import-export` `interoperability` `priority-medium`

## 📝 Branch
`feature/netlist-io`

## ⏱️ Estimated Effort
**Time**: 4-5 days
**Complexity**: High
**Priority**: Medium