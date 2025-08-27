# Feature: Round-Trip circuit-synth Integration

## 🎯 Objective
Implement bidirectional conversion between circuit-simulation library and circuit-synth JSON format, enabling seamless workflow integration between circuit design and circuit simulation.

## 📋 Requirements

### Core Bidirectional Flow
- [ ] **Import**: circuit-synth JSON → Circuit API → Simulation
- [ ] **Export**: Circuit API → circuit-synth JSON → KiCad generation
- [ ] **Preservation**: Maintain all circuit-synth metadata (symbols, footprints, pins)
- [ ] **Validation**: Ensure round-trip fidelity

### Integration Points
- [ ] Use circuit-synth hierarchical JSON as native import format
- [ ] Export simulation results back to circuit-synth compatible format
- [ ] Preserve KiCad symbol library references
- [ ] Maintain pin mapping and connectivity data

### Workflow Support
- [ ] **Design Flow**: circuit-synth design → simulation validation → refinement
- [ ] **Analysis Flow**: Import existing circuit-synth projects for simulation
- [ ] **Documentation**: Simulation results integrated with circuit-synth reports

## 🛠️ Technical Implementation

### File Structure
```
src/io/
├── circuit_synth_integration/
│   ├── __init__.py
│   ├── json_importer.py        # circuit-synth JSON → Circuit API
│   ├── json_exporter.py        # Circuit API → circuit-synth JSON  
│   ├── metadata_bridge.py      # Preserve KiCad metadata
│   ├── pin_mapper.py          # Map pins to simulation nodes
│   └── hierarchy_flattener.py  # Convert hierarchy for simulation
├── validation/
│   ├── round_trip_tester.py   # Test conversion fidelity
│   └── compatibility_checker.py # Check circuit-synth compatibility
```

### Example Usage
```python
from circuit_sim.io import CircuitSynthImporter, CircuitSynthExporter

# Import from circuit-synth
importer = CircuitSynthImporter()
circuit = importer.load_from_json("ESP32_Dev_Board.json")

# Simulate
engine = SimulationEngine()
results = engine.simulate_dc(circuit)

# Export results back to circuit-synth format
exporter = CircuitSynthExporter()
enhanced_json = exporter.export_with_simulation_data(
    circuit, results, original_json_path="ESP32_Dev_Board.json"
)

# Enhanced JSON now includes simulation validation data
```

## 📊 Success Criteria
- [ ] 100% round-trip fidelity for circuit-synth JSON
- [ ] All KiCad metadata preserved during conversion
- [ ] Simulation results enhance circuit-synth workflow
- [ ] No data loss in bidirectional conversion

## 🔗 Dependencies
- Depends on: Core Circuit API, circuit-synth submodule
- Blocks: None
- Related: #8 (Netlist I/O), circuit-synth repository

## ✅ Acceptance Criteria
1. Import any circuit-synth JSON file successfully
2. Export preserves all original metadata  
3. Round-trip conversion is lossless
4. Simulation data adds value to circuit-synth workflow

## 🏷️ Labels
`enhancement` `integration` `circuit-synth` `priority-medium`

## 📝 Branch
`feature/circuit-synth-integration`

## ⏱️ Estimated Effort
**Time**: 2-3 days
**Complexity**: Medium  
**Priority**: Medium (enables future workflow enhancements)