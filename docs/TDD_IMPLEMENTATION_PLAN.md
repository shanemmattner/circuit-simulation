# 15-Minute TDD Implementation Plan: SPICE Netlist Import/Export

## 🎯 **Objective**
Build SPICE and KiCad import/export using Test-Driven Development in focused 15-minute segments.

## ⏰ **Segment Breakdown (8 segments = 2 hours)**

### **Segment 1: Foundation Setup (15 min)**
**Goal**: Copy circuit-synth models and set up basic structure
- [ ] Copy `models.py` and `json_loader.py` from circuit-synth
- [ ] Create `src/io/` directory structure  
- [ ] Write first failing test for model loading
- [ ] Make test pass

**Test**: Load a SPICE model (2N3904) and verify parameters
```python
def test_load_spice_model():
    model_lib = ModelLibrary()
    model = model_lib.get_model("2N3904")
    assert model.model_type == "NPN"
    assert model.parameters["BF"] == 416.4
```

### **Segment 2: SPICE Tokenizer (15 min)**  
**Goal**: Parse basic SPICE syntax into tokens
- [ ] Write failing test for SPICE line parsing
- [ ] Implement basic tokenizer
- [ ] Handle line continuations (+)
- [ ] Make all tests pass

**Test**: Parse resistor line
```python
def test_spice_tokenizer():
    tokenizer = SpiceTokenizer()
    tokens = tokenizer.parse_line("R1 1 2 1k")
    assert tokens == ["R1", "1", "2", "1k"]
```

### **Segment 3: Component Parser (15 min)**
**Goal**: Convert SPICE components to Circuit objects
- [ ] Write failing test for resistor parsing
- [ ] Implement component parser base class
- [ ] Add resistor, capacitor, inductor parsing
- [ ] Make tests pass

**Test**: Parse and create Circuit components
```python
def test_parse_resistor():
    parser = SpiceParser()
    component = parser.parse_component("R1 node1 node2 1k")
    assert component.name == "R1"
    assert component.value == "1k"
```

### **Segment 4: Voltage/Current Sources (15 min)**
**Goal**: Handle active components and sources  
- [ ] Write failing tests for V and I sources
- [ ] Implement source parsing (DC, AC, transient)
- [ ] Handle complex source definitions
- [ ] Make tests pass

**Test**: Parse voltage source
```python
def test_parse_voltage_source():
    parser = SpiceParser()
    source = parser.parse_component("V1 vdd gnd DC 5V")
    assert source.dc_value == "5V"
```

### **Segment 5: Subcircuit Support (15 min)**
**Goal**: Parse .SUBCKT definitions
- [ ] Write failing test for subcircuit parsing
- [ ] Implement .SUBCKT/.ENDS handling
- [ ] Parse port definitions
- [ ] Make tests pass

**Test**: Parse subcircuit definition
```python
def test_parse_subcircuit():
    parser = SpiceParser()
    subckt = parser.parse_subcircuit([
        ".SUBCKT OPAMP inp inn vcc vee out",
        "R1 inp 1 1meg",
        ".ENDS"
    ])
    assert len(subckt.ports) == 5
```

### **Segment 6: KiCad Netlist Bridge (15 min)**
**Goal**: Import KiCad netlists using circuit-synth logic
- [ ] Write failing test for KiCad netlist import
- [ ] Copy and adapt circuit-synth netlist parsing
- [ ] Convert KiCad format to Circuit objects
- [ ] Make tests pass

**Test**: Import KiCad netlist
```python  
def test_import_kicad_netlist():
    importer = KiCadImporter()
    circuit = importer.load_netlist("test.net")
    assert len(circuit.components) > 0
```

### **Segment 7: Hierarchical Simulation (15 min)**
**Goal**: Individual and group subcircuit simulation
- [ ] Write failing test for subcircuit simulation
- [ ] Implement testbench generation
- [ ] Run individual subcircuit tests
- [ ] Make tests pass

**Test**: Simulate subcircuit individually
```python
def test_simulate_subcircuit():
    subcircuit = load_subcircuit("power_supply")
    testbench = generate_testbench(subcircuit)
    results = engine.simulate_dc(testbench)
    assert results.get_voltage("vout") > 3.0
```

### **Segment 8: Integration & Export (15 min)**
**Goal**: Export back to SPICE format
- [ ] Write failing test for SPICE export
- [ ] Implement SPICE netlist generation
- [ ] Round-trip test (import → export → import)
- [ ] Make tests pass

**Test**: Round-trip conversion
```python
def test_round_trip_spice():
    original = import_spice("test.cir")
    exported = export_spice(original)
    reimported = import_spice(exported)
    assert circuits_equal(original, reimported)
```

## 📋 **TDD Workflow Per Segment**

1. **Red** (2 min): Write failing test
2. **Green** (8 min): Implement minimum code to pass
3. **Refactor** (3 min): Clean up and optimize  
4. **Document** (2 min): Update docstrings/comments

## 🧪 **Test Strategy**

### **Test Fixtures Directory**
```
tests/fixtures/netlist_io/
├── spice/
│   ├── simple_resistor.cir
│   ├── voltage_divider.cir
│   ├── subcircuit_example.cir
│   └── complex_hierarchy.cir
├── kicad/
│   ├── simple.net
│   └── hierarchical.net
└── circuit_synth/
    ├── esp32_example.json
    └── stm32_example.json
```

### **Test Categories**
1. **Unit**: Individual parser components
2. **Integration**: Full file parsing
3. **Round-trip**: Import/export cycles
4. **Regression**: Real-world files

## 📊 **Success Metrics Per Segment**
- All tests pass ✅
- Code coverage >80% 📊
- No breaking changes to existing API 🔒
- Clear error messages for failures ⚠️

## 🔄 **After Each Segment**
1. Run full test suite: `uv run pytest`
2. Update memory-bank with decisions made
3. Commit progress: `uv run python .claude/commands/commit.py`
4. Document any architectural decisions

Ready to start **Segment 1**? 🎯