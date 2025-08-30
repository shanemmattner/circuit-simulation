# Circuit-Synth JSON Schema

## Overview

This document defines the JSON format used by circuit-synth for circuit interchange with circuit-simulation. Based on actual circuit-synth output analysis.

## JSON Structure

```json
{
  "name": "String - Circuit name",
  "description": "String - Circuit description", 
  "tstamps": "String - KiCad timestamp identifier",
  "source_file": "String - Source KiCad schematic file",
  "components": {
    "ComponentRef": {
      "symbol": "String - KiCad symbol library:name",
      "ref": "String - Component reference designator", 
      "value": "String - Component value (1k, 100nF, etc)",
      "footprint": "String - KiCad footprint library:name",
      "datasheet": "String - Datasheet URL or ~",
      "description": "String - Component description",
      "properties": {
        "key": "value - Additional KiCad properties"
      },
      "_extra_fields": {
        "key": "value - Extra component fields"
      },
      "pins": [
        {
          "pin_id": "String - Pin identifier",
          "name": "String - Pin name or ~",
          "func": "String - Pin function (passive, power, etc)",
          "unit": "Number - Unit number",
          "x": "Number - X coordinate",
          "y": "Number - Y coordinate", 
          "length": "Number - Pin length",
          "orientation": "Number - Pin orientation in degrees"
        }
      ]
    }
  },
  "nets": {
    "NetName": [
      {
        "component": "String - Component reference",
        "pin": {
          "number": "String - Pin number",
          "name": "String - Pin name or ~", 
          "type": "String - Pin type (passive, power, etc)"
        }
      }
    ]
  },
  "subcircuits": [],
  "annotations": [
    {
      "type": "String - Annotation type",
      "text": "String - Annotation text",
      "position": [x, y],
      "size": [width, height],
      "margins": [top, right, bottom, left],
      "text_size": "Number - Text size",
      "bold": "Boolean - Bold text",
      "italic": "Boolean - Italic text", 
      "text_color": "String - Text color",
      "background": "Boolean - Has background",
      "background_color": "String - Background color",
      "border": "Boolean - Has border",
      "border_width": "Number - Border width",
      "border_color": "String - Border color",
      "justify": "String - Text justification",
      "rotation": "Number - Rotation angle",
      "uuid": "String - Unique identifier"
    }
  ]
}
```

## Integration Layer Compatibility

The circuit-simulation integration layer handles:
1. **Pin Format Translation**: Converts nested pin objects to simple pin numbers
2. **Component Mapping**: Maps KiCad symbols to simulation components  
3. **Value Parsing**: Parses engineering notation (1k → 1000, 100nF → 100e-9)
4. **Validation**: Strict JSON schema validation with helpful error messages

## Usage

```python
from circuit_sim.circuit_synth_integration import simulate_from_circuit_synth

# Load circuit-synth JSON
with open("circuit.json", "r") as f:
    circuit_data = json.load(f)

# Simulate  
results = simulate_from_circuit_synth(circuit_data)
print(f"Output: {results.voltages['OUTPUT'][0]:.3f} V")
```

---

*Last updated: 2025-08-29*