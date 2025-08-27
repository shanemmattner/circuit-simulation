# PRD: KiCad Import Phase 3 - Model Library Integration

## Document Information
- **Version**: 1.0
- **Date**: 2025-01-27
- **Status**: Draft - Ready for Implementation
- **Scope**: Phase 3 of KiCad Import Enhancement
- **Prerequisite**: Phase 1 Parser Robustness (Complete)

## Problem Statement

While Phase 1 gave us robust parsing, imported KiCad circuits only support basic R/L/C components. Real-world KiCad designs contain:

- **Transistors** (BJT, MOSFET, JFET)
- **Diodes** (signal, power, Zener, LED)  
- **Integrated Circuits** (op-amps, logic gates, regulators)
- **Complex Components** (transformers, crystals, connectors)

These currently either fail to import or import as unsupported components, making simulation impossible.

## Goal

Transform the KiCad parser from "basic component import" to "simulation-ready circuit import" by automatically mapping KiCad symbols to appropriate SPICE models from our existing model library.

## Success Metrics

- **Component Coverage**: Support 90% of common KiCad symbols
- **Model Accuracy**: Use appropriate SPICE models (not just defaults)
- **User Override**: Allow manual model selection for critical components
- **Graceful Degradation**: Unknown components get basic behavioral models
- **Performance**: Model lookup <100ms per component

## Proposed Solution

### Core Architecture

```python
# Smart component mapper with fallback strategies
class ComponentModelMapper:
    def __init__(self, model_library: SpiceModelLoader):
        self.model_library = model_library  # Existing 50k+ models
        self.mapping_strategies = [
            ExactSymbolMatch(),      # "Device:2N3904" → 2N3904 model
            FuzzySymbolMatch(),      # "Device:NPN" → generic NPN
            ComponentTypeMatch(),    # All "Q*" → BJT behavioral
            DefaultBehavioral()      # Unknown → basic behavioral
        ]
    
    def map_component(self, kicad_symbol: str, ref: str, value: str) -> ComponentModel:
        """Map KiCad symbol to best available SPICE model."""
        for strategy in self.mapping_strategies:
            model = strategy.find_model(kicad_symbol, ref, value)
            if model:
                return model
        return None  # Should never happen with DefaultBehavioral
```

### Implementation Strategy

#### 1. Component Type Detection
```python
class ComponentTypeDetector:
    """Classify KiCad symbols into simulation categories."""
    
    PATTERNS = {
        'transistor_bjt': ['*NPN*', '*PNP*', '*2N*', '*BC*'],
        'transistor_mosfet': ['*MOSFET*', '*FET*', '*IRF*'], 
        'diode': ['*Diode*', '*1N*', '*LED*'],
        'opamp': ['*OpAmp*', '*LM*', '*TL*'],
        'logic': ['*74*', '*4*', '*AND*', '*OR*'],
        'regulator': ['*Regulator*', '*78*', '*79*']
    }
```

#### 2. Model Selection Priority
1. **Exact Match**: KiCad value matches model library ("2N3904" → 2N3904.lib)  
2. **Symbol Match**: KiCad symbol maps to model ("Device:2N3904" → 2N3904.lib)
3. **Generic Type**: Component type gets generic model (NPN → generic_npn.lib)
4. **Behavioral**: Unknown gets behavioral model (VCVS, resistor, etc.)

#### 3. User Override System
```python
# Allow users to override automatic mappings
override_config = {
    "U1": "LM358",           # Force specific model  
    "Q*": "2N3904",          # Pattern-based override
    "D*": "1N4148",          # Default diode model
}
```

### Component Support Plan

#### Immediate Priority (Week 1)
- **BJT Transistors**: NPN/PNP with 2N3904/2N3906 defaults
- **Diodes**: Signal/power with 1N4148/1N4007 defaults  
- **MOSFETs**: N/P-channel with IRF540/IRF9540 defaults

#### Secondary Priority (Week 2) 
- **Op-Amps**: Behavioral models (LM358, TL072, etc.)
- **Logic Gates**: Behavioral digital models
- **Voltage Regulators**: 78xx/79xx series

#### Future Expansion
- **RF Components**: S-parameter models
- **Power Components**: Thermal models
- **Custom Components**: User-defined models

## Technical Implementation

### 1. Model Library Integration
```python
# Extend existing SpiceModelLoader
class EnhancedModelLoader(SpiceModelLoader):
    """Enhanced model loader with KiCad symbol mapping."""
    
    def find_model_for_symbol(self, kicad_symbol: str, value: str = "") -> Optional[str]:
        """Find best SPICE model for KiCad symbol."""
        # Check exact value match first
        if value and self.has_model(value):
            return self.get_model(value)
            
        # Parse symbol for model hints
        model_hints = self._extract_model_hints(kicad_symbol, value)
        
        # Search model library
        return self._search_models(model_hints)
```

### 2. Circuit Enhancement
```python
# Enhance KiCadParser to use model mapper
class EnhancedKiCadParser(KiCadParser):
    def __init__(self):
        super().__init__()
        self.model_mapper = ComponentModelMapper(SpiceModelLoader())
        
    def _create_circuit_component(self, circuit, ref, symbol, value):
        """Enhanced component creation with model mapping."""
        # Get appropriate model
        model = self.model_mapper.map_component(symbol, ref, value)
        
        # Create component with model
        if model.type == 'bjt':
            circuit.add_bjt_transistor(ref, model.nodes, model.spice_model)
        elif model.type == 'diode':
            circuit.add_diode(ref, model.nodes, model.spice_model)
        # etc.
```

### 3. New Circuit API Methods
```python
# Extend Circuit class for new component types
class Circuit:
    def add_bjt_transistor(self, name: str, collector: str, base: str, 
                          emitter: str, model: str = "2N3904"):
        """Add BJT transistor with SPICE model."""
        
    def add_mosfet(self, name: str, drain: str, gate: str, source: str,
                   bulk: str, model: str = "IRF540"):
        """Add MOSFET with SPICE model."""
        
    def add_diode(self, name: str, anode: str, cathode: str, 
                  model: str = "1N4148"):
        """Add diode with SPICE model."""
        
    def add_opamp(self, name: str, inputs: list, outputs: list,
                  model: str = "LM358"):
        """Add op-amp with behavioral model."""
```

## Test-Driven Development Plan

### Phase 3A: Core Model Mapping (Week 1)
**15-minute chunks:**
1. Set up model library integration tests
2. Implement ComponentTypeDetector with pattern matching
3. Build ExactSymbolMatch strategy
4. Add FuzzySymbolMatch with Levenshtein distance
5. Create DefaultBehavioral fallback
6. Test with real KiCad transistor/diode symbols

### Phase 3B: Circuit Integration (Week 1)  
**15-minute chunks:**
7. Extend Circuit API for new component types
8. Integrate model mapper into KiCadParser
9. Add user override configuration
10. Test end-to-end: KiCad → models → simulation
11. Performance optimization and caching
12. Error handling and user feedback

### Phase 3C: Component Library Expansion (Week 2)
**15-minute chunks:**
13. Add comprehensive transistor support  
14. Implement diode variants (Zener, LED, power)
15. Create op-amp behavioral models
16. Add logic gate support
17. Implement voltage regulator models
18. Test with complex multi-component circuits

### Phase 3D: Polish and Documentation (Week 2)
**15-minute chunks:**
19. User configuration system
20. Model override capabilities
21. Performance benchmarking
22. Comprehensive documentation
23. Integration testing with real designs
24. Memory bank and progress updates

## Example User Experience

### Before Phase 3:
```
❌ Import failed with issues
  ✗ 3 component(s) failed to import
  • ERROR: Q1 - Unsupported component type: NPN
  • ERROR: D1 - Unsupported component type: Diode  
  • ERROR: U1 - Unsupported component type: LM358
```

### After Phase 3:
```
✅ Import successful  
  ✓ 6 components imported successfully
  📚 Model assignments:
  • R1: resistor = 10k
  • R2: resistor = 10k  
  • Q1: BJT_NPN = 2N3904 (auto-selected)
  • D1: diode = 1N4148 (auto-selected)
  • U1: opamp = LM358 (exact match)
  • C1: capacitor = 100uF
  
🚀 Circuit ready for simulation!
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model library integration complexity | High | Use existing SpiceModelLoader, incremental approach |
| Performance with large model library | Medium | Caching, lazy loading, indexed search |
| Model accuracy for simulation | High | Conservative defaults, user override capability |
| Breaking existing functionality | High | Maintain backward compatibility, comprehensive testing |

## Success Criteria

### Functional Requirements
- [ ] 90% of common KiCad symbols supported
- [ ] Automatic model selection for transistors, diodes, op-amps
- [ ] User override capability for critical components  
- [ ] Graceful degradation for unknown components
- [ ] End-to-end simulation of complex imported circuits

### Performance Requirements  
- [ ] Model lookup <100ms per component
- [ ] Memory usage <50MB additional for model cache
- [ ] Import time increase <20% compared to Phase 1

### User Experience
- [ ] Clear model assignment feedback
- [ ] Easy override configuration
- [ ] Actionable warnings for unknown components
- [ ] Comprehensive documentation with examples

## Dependencies

- Phase 1 Parser Robustness (Complete)
- Existing SpiceModelLoader (50k+ models)
- Circuit API extensibility
- SPICE simulation engine compatibility

---

**This PRD transforms the KiCad parser from "basic import" to "simulation-ready import" by leveraging our existing model library intelligently. The phased approach ensures incremental value delivery while maintaining system reliability.**