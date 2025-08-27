# Known Limitations

## AC Analysis Phase Information

**Issue**: PySpice AC analysis returns real-only values instead of complex values, causing phase plots to show 0° everywhere.

**Root Cause**: PySpice `UnitValue` class (Unit.py:892) casts complex values to real with warning:
```
ComplexWarning: Casting complex values to real discards the imaginary part
```

**Impact**: 
- ✅ **Magnitude response**: Perfect (shows proper filter rolloff)
- ❌ **Phase response**: Always 0° (should show 0° to ±90° for reactive circuits)

**Affected Circuits**:
- RC filters (should show -90° to 0° phase shift)
- RL circuits (should show 0° to +90° phase shift)  
- RLC resonant circuits (should show phase transitions)

**Current Status**: 
- **Reports are still valuable** with excellent magnitude analysis
- **Interactive Plotly charts** work perfectly for magnitude
- **Professional quality** maintained with descriptive node labeling

**Potential Solutions** (for future):
1. **Override PySpice result extraction** to preserve complex data before unit conversion
2. **Patch PySpice UnitValue class** to handle complex numbers
3. **Use raw ngspice interface** directly (bypass PySpice)
4. **Switch to alternative Python SPICE library** (lcapy, ahkab, etc.)

**Workaround**: 
- Focus on magnitude analysis for now
- Add theoretical phase calculations for reference
- Document expected phase behavior in reports

**Testing**: Our robust testing framework detects this issue automatically:
```bash
python3 tests/test_robust_simulation_behavior.py
# FAILS with: "RC filter should have imaginary voltage components"
```

---

**Note**: This limitation does not affect the core value of the simulation platform. The magnitude analysis is accurate and professionally presented with excellent interactive visualization.