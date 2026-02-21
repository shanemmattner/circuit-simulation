# Circuit Schematic Generation Libraries - Research Report

## Executive Summary

This report evaluates three Python libraries for generating circuit schematics as SVG output:
- **Schemdraw** - Pure Python circuit drawing library
- **Lcapy** - Circuit analysis with optional schematic drawing
- **svgwrite** / **svglib** - Low-level SVG generation

**Recommendation**: **Schemdraw** is the best choice for this project due to its native SVG support, rich component library, and declarative Python API that aligns well with the existing circuit representation.

---

## Library Comparison

### 1. Schemdraw

**Purpose**: Declarative circuit drawing in Python

**SVG Support**: ✅ Native SVG backend (`schemdraw.Svg`)

**Strengths**:
- Clean, Pythonic declarative API
- Native SVG output (no intermediate formats)
- Rich built-in component library (resistors, capacitors, inductors, ICs, transistors, op-amps, etc.)
- Active maintenance and development
- Easy to extend with custom components
- Supports flow-based and block diagrams too

**Weaknesses**:
- Drawing is manual/structural (you describe the layout)
- No automatic netlist-to-schematic conversion
- Limited automatic layout algorithms

**Use Case**: Programmatic circuit generation, documentation, reports

**Example**:
```python
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing() as d:
    d.add(elm.Vsourcesinusoidal().label('5V'))
    d.add(elm.Resistor().right().label('1k'))
    d.add(elm.Capacitor().down().label('1uF'))
    d.add(elm.GND())
    
# Output to SVG
d.save('circuit.svg')
```

---

### 2. Lcapy

**Purpose**: Circuit analysis + schematic drawing

**SVG Support**: ⚠️ Limited; primarily for notebook documentation

**Strengths**:
- Symbolic circuit analysis (netlist → equations, transfer functions)
- Can draw simple schematics from netlists
- Good for educational purposes
- Supports mixed-signal analysis

**Weaknesses**:
- Drawing is secondary to analysis
- Less flexible for custom diagram layouts
- SVG output is a side effect, not primary feature
- Less active maintenance

**Use Case**: When you need both analysis AND drawing from the same netlist

**Example**:
```python
from lcapy import Circuit

cct = Circuit('''
V1 1 0 5
R1 1 2 1k
C1 2 0 1u
''')

# Draw schematic
cct.draw()
# Saves to file (but limited control)
```

---

### 3. svgwrite / svglib

**Purpose**: Low-level SVG generation

**SVG Support**: ✅ Excellent (it's what they do)

**Strengths**:
- Full control over every SVG element
- Can render any graphic
- Good for custom diagrams

**Weaknesses**:
- No circuit primitives - you'd build everything from lines/rectangles/circles
- No component library
- Would require significant custom code to draw circuits
- Steeper development curve

**Use Case**: Only if you need full control or have custom component shapes not available elsewhere

---

## Integration with This Project

### Current Project Structure

The project already has:
- `Circuit` class with component methods (`add_resistor`, `add_capacitor`, etc.)
- Components stored as dictionaries with type, name, and node information
- Visualization module with Plotly-based plotting

### Proposed Integration Approach

Schemdraw can be integrated with the existing `Circuit` class:

```python
from schemdraw import Drawing
import schemdraw.elements as elm

def circuit_to_schemdraw(circuit: Circuit) -> Drawing:
    """Convert circuit_sim Circuit to Schemdraw Drawing."""
    d = Drawing()
    
    # Map nodes to positions (simplified)
    # This would need a layout algorithm
    
    for comp in circuit.components:
        if comp['type'] == 'resistor':
            d.add(elm.Resistor().label(comp['resistance']))
        elif comp['type'] == 'capacitor':
            d.add(elm.Capacitor().label(comp['capacitance']))
        # ... etc
    
    return d
```

### Key Considerations

1. **Layout Algorithm**: Schemdraw is declarative (you describe connections), not automatic. You'd need to develop a layout algorithm to convert node connections to x,y positions.

2. **Component Mapping**: The existing component types (resistor, capacitor, inductor, voltage_source, etc.) map well to Schemdraw elements.

3. **SVG Output**: Native support - `d.save('output.svg')` works directly.

---

## Alternative Approaches

### KiCad / ngspice Integration
The project already uses ngspice. Consider:
- Generate netlist → Use KiCad to open → Export SVG
- More complex but more powerful

### Graphviz
- Good for automatic layout
- No circuit primitives (would need custom elements)
- Simpler than Schemdraw for pure topology

---

## Recommendation

| Criterion | Schemdraw | Lcapy | svgwrite |
|-----------|-----------|-------|----------|
| SVG Support | ✅ Native | ⚠️ Limited | ✅ Excellent |
| Component Library | ✅ Rich | ⚠️ Basic | ❌ None |
| API Fit | ✅ Pythonic | ⚠️ Mixed | ❌ Low-level |
| Maintenance | ✅ Active | ⚠️ Slow | ✅ Active |
| Learning Curve | ✅ Low | ✅ Low | ❌ High |

**Winner: Schemdraw**

For this project:
1. **Add schemdraw as a dependency**
2. **Create a `SchematicGenerator` class** that converts Circuit objects to SVG
3. **Implement a simple layout algorithm** (could start with left-to-right topological layout)
4. **Integrate with the reports module** for SVG output in reports

---

## Next Steps

1. **Install and test Schemdraw**: `pip install schemdraw`
2. **Create a prototype**: Convert a simple circuit to SVG
3. **Develop layout algorithm**: Map circuit topology to schematic positions
4. **Integrate with reporting**: Add SVG export to report generator

---

## References

- Schemdraw GitHub: https://github.com/cdelker/schemdraw
- Schemdraw Documentation: https://cdelker.github.io/schemdraw/
- Lcapy Documentation: https://lcapy.readthedocs.io/
- svgwrite Documentation: https://svgwrite.readthedocs.io/
