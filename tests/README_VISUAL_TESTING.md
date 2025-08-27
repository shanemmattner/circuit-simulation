# Visual Testing Framework for Circuit Simulation

This directory contains a comprehensive testing framework specifically designed to catch the types of issues discovered in our AC analysis implementation, including:

- **Complex Value Validation**: Ensures AC analysis returns complex values with phase information
- **Circuit Behavior Testing**: Validates simulation results against theoretical expectations
- **Visual Chart Comparison**: Compares generated plots with reference images
- **Regression Prevention**: Catches subtle issues that standard unit tests miss

## 🚨 Critical Issues This Framework Catches

### 1. AC Analysis Real-Only Values Bug
**Problem**: PySpice AC analysis returning only real values instead of complex values, causing phase plots to show 0° instead of proper phase shifts.

**Detection**: `validate_ac_complex_values()` function checks that:
- AC voltage data is stored as complex numpy arrays
- Imaginary parts are non-zero (indicating phase information)
- Phase values show meaningful variation across frequency range

### 2. Circuit Physics Validation
**Problem**: Simulation results that look "reasonable" but don't match circuit theory.

**Detection**: Behavior validation functions check:
- RC filter cutoff frequencies match theoretical calculations
- Phase response follows expected patterns (-90° to 0° for low-pass)
- Magnitude response shows proper rolloff characteristics

### 3. Chart Generation Issues
**Problem**: Charts that render but show incorrect data due to complex value handling issues.

**Detection**: Visual comparison tests:
- Generate reference Bode plots from theoretical calculations
- Compare with actual simulation-generated plots
- Identify discrepancies in magnitude and phase representations

## 🛠️ Framework Components

### Core Files

1. **`visual_testing_framework.py`** - Main framework with validation classes
2. **`test_ac_analysis_behavior.py`** - Comprehensive pytest test suite
3. **`run_comprehensive_ac_tests.py`** - Test runner with Claude Code friendly reports
4. **`claude_test_helper.py`** - Utilities for Claude Code interaction

### Test Categories

#### Unit Tests (`test_ac_analysis_behavior.py`)
- **AC Complex Value Tests**: Verify complex data types and phase information
- **Behavior Validation Tests**: Check circuit responses against theory
- **Parameter Sweep Tests**: Test with different component values
- **Edge Case Tests**: Handle extreme frequencies and error conditions

#### Visual Tests (`visual_testing_framework.py`)
- **Reference Generation**: Create theoretical Bode plots
- **Simulation Plotting**: Generate charts from AC analysis results
- **Image Comparison**: Pixel-level comparison with intelligent diff analysis
- **Chart Quality Assessment**: Verify professional chart generation

#### Integration Tests (`run_comprehensive_ac_tests.py`)
- **Environment Testing**: Verify Docker simulation setup
- **End-to-End Workflow**: Test complete analysis pipeline
- **Report Generation**: Validate comprehensive reporting system

## 🚀 Quick Start for Claude Code

### Run All Tests
```bash
# Quick test (recommended for first run)
python tests/run_comprehensive_ac_tests.py

# Full test suite with visual comparison
python tests/run_comprehensive_ac_tests.py --visual --slow

# Only PyTest suite
pytest tests/test_ac_analysis_behavior.py -v
```

### Diagnose Specific Issues
```bash
# Get targeted diagnosis
python tests/claude_test_helper.py --diagnose

# Generate targeted test code for specific issues
python tests/claude_test_helper.py --generate-test complex_values
python tests/claude_test_helper.py --generate-test rc_behavior
python tests/claude_test_helper.py --generate-test chart_generation
```

### Quick Issue Check
```bash
# Run just the critical AC analysis tests
pytest tests/test_ac_analysis_behavior.py::TestACAnalysisBehavior::test_ac_analysis_returns_complex_values -v
```

## 📊 Understanding Test Results

### Test Result Interpretation

#### ✅ All Tests Pass
- AC analysis working correctly with complex values
- Circuit behavior matches theoretical expectations  
- Chart generation pipeline functioning properly

#### ❌ Complex Values Test Fails
**Issue**: AC analysis returning real-only values
**Action**: Check `src/circuit_sim/simulator/builder.py` voltage source configuration
**Look for**: PySpice AC source setup, should use `"DC 0 AC 1"` syntax

#### ❌ Behavior Validation Fails
**Issue**: Simulation math doesn't match circuit theory
**Action**: Check component value parsing and frequency vector generation
**Look for**: Calculation errors in `src/circuit_sim/simulator/engine.py`

#### ❌ Visual Comparison Fails
**Issue**: Charts render but show wrong data
**Action**: Check chart generation with complex AC data
**Look for**: Magnitude/phase extraction in chart generation code

### Claude Code Friendly Output

The framework generates reports specifically designed for AI analysis:

```markdown
## 🚨 Critical Issues Requiring Immediate Attention

- ❌ CRITICAL: AC analysis returning real-only values instead of complex
- ❌ CRITICAL: Circuit behavior doesn't match theoretical expectations

## 🤖 Recommendations for Claude Code

### Immediate Actions:
- 1. Check PySpice AC source configuration in src/circuit_sim/simulator/builder.py
- 2. Verify voltage sources use 'DC 0 AC 1' syntax for AC analysis
- 3. Ensure AC analysis results are stored as complex numpy arrays
```

## 🎯 Specific Test Cases

### RC Low-Pass Filter Test
```python
def test_rc_lowpass_comprehensive():
    """Test RC low-pass filter behavior comprehensively."""
    
    # Creates 1kΩ, 1μF RC filter (cutoff ~159 Hz)
    # Validates:
    # - Complex AC values present
    # - DC gain ≈ 0 dB
    # - Cutoff gain ≈ -3 dB  
    # - Phase: 0° → -45° → -90°
    # - Visual Bode plot comparison
```

### Complex Value Validation Test
```python
def test_ac_complex_values():
    """Specifically test for complex value bug."""
    
    # Checks:
    # - np.iscomplexobj(voltage_data) == True
    # - Non-zero imaginary parts present
    # - Meaningful phase variation across frequency
```

### Behavioral Physics Test
```python  
def test_circuit_physics():
    """Test circuit behavior against theory."""
    
    # Validates:
    # - Cutoff frequency calculation: f_c = 1/(2πRC)
    # - Transfer function magnitude and phase
    # - Component value parsing accuracy
```

## 🔧 Advanced Usage

### Custom Circuit Testing

```python
from visual_testing_framework import VisualTestFramework

framework = VisualTestFramework()

# Test your own circuit
circuit = Circuit("My Circuit")
# ... add components ...

ac_results = engine.simulate_ac(circuit, 1, 10000, 20)
test_results = framework.test_rc_lowpass_circuit_comprehensive()

for result in test_results:
    print(result.claude_assessment())
```

### Reference Signal Generation

```python
from visual_testing_framework import ReferenceSignalGenerator

ref_gen = ReferenceSignalGenerator()

# Generate theoretical response
frequencies = np.logspace(1, 5, 100)  # 10 Hz to 100 kHz
magnitude_db, phase_deg = ref_gen.rc_lowpass_response(
    frequencies, R_ohms=1000, C_farads=1e-6
)

# Compare with simulation results
```

### Custom Behavior Validation

```python
from visual_testing_framework import CircuitBehaviorValidator

validator = CircuitBehaviorValidator()

# Validate AC analysis has complex values
complex_result = validator.validate_ac_complex_values(ac_results, node_id=2)

if not complex_result.passed:
    print("❌ AC analysis issue:", complex_result.issues)
    
# Validate RC filter behavior
behavior_result = validator.validate_rc_lowpass_behavior(
    circuit, ac_results, R_ohms=1000, C_farads=1e-6
)

print(behavior_result.claude_assessment())
```

## 📁 Output Files

### Test Reports
- `tests/comprehensive_ac_output/claude_ac_analysis_report.md` - Main Claude Code report
- `tests/comprehensive_ac_output/test_results.json` - Raw test data
- `tests/comprehensive_ac_output/pytest_ac_results.xml` - PyTest XML results

### Visual Outputs  
- `tests/visual_output/references/` - Theoretical reference plots
- `tests/visual_output/actuals/` - Simulation-generated plots
- `tests/visual_output/diffs/` - Visual difference analysis

### Coverage Reports
- `tests/comprehensive_ac_output/coverage_html/` - HTML coverage report
- `tests/comprehensive_ac_output/coverage.json` - Coverage data

## 🚨 Emergency Debugging

### AC Analysis Completely Broken?
```bash
# Run minimal test to isolate issue
python -c "
from claude_test_helper import ClaudeTestHelper
helper = ClaudeTestHelper()
diagnosis = helper.diagnose_ac_analysis_issue()
print('Issues found:', len(diagnosis['issues_found']))
for issue in diagnosis['issues_found']:
    print(f'- {issue[\"type\"]}: {issue[\"description\"]}')
"
```

### Need to Test PySpice Directly?
```bash
# Run PySpice isolation test
python tests/test_ac_analysis_behavior.py::TestACAnalysisRegression::test_pyspice_ac_source_configuration_bug -v -s
```

### Generate Minimal Failing Test?
```bash
# Get targeted test code
python tests/claude_test_helper.py --generate-test complex_values > test_debug.py
python test_debug.py
```

## 💡 Best Practices for Claude Code

### 1. Always Run Comprehensive Tests After AC Analysis Changes
```bash
python tests/run_comprehensive_ac_tests.py
```

### 2. Use Targeted Tests for Specific Issues
```bash
# Complex values issue
pytest tests/test_ac_analysis_behavior.py -k "complex_values" -v

# Behavior validation issue  
pytest tests/test_ac_analysis_behavior.py -k "behavior" -v

# Chart generation issue
pytest tests/test_ac_analysis_behavior.py -k "chart" -v
```

### 3. Check Test Output for Action Items
Look for sections like:
- `🚨 Critical Issues Requiring Immediate Attention`
- `🤖 Recommendations for Claude Code`
- `📊 Physics Analysis` with specific measurement data

### 4. Validate Fixes with Regression Tests
```bash
# After making changes, ensure no regressions
pytest tests/test_ac_analysis_behavior.py::TestACAnalysisRegression -v
```

## 🔍 Troubleshooting

### Common Issues

#### "PIL not found" Error
```bash
pip install pillow  # For visual image comparison
```

#### "NgSpice not found" Error  
```bash
# Run in Docker environment
docker-compose run --rm circuit-sim python tests/run_comprehensive_ac_tests.py
```

#### Tests Pass but Charts Still Wrong?
- Check if tests are using correct node IDs for measurement
- Verify chart generation uses the same AC results as validation
- Look for data conversion issues between simulation and visualization

#### Visual Tests Always Fail?
```bash
# Run without visual comparison first
python tests/run_comprehensive_ac_tests.py

# Then add visual testing
python tests/run_comprehensive_ac_tests.py --visual
```

---

This testing framework is specifically designed to prevent and catch the AC analysis issues we discovered. It provides both automated detection and human-readable reports that guide Claude Code to the exact source of problems and their solutions.