"""
Pytest configuration and fixtures.
"""

import sys
import tempfile
import logging
from pathlib import Path

import pytest

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if src_path not in sys.path:
    sys.path.insert(0, str(src_path))

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')


@pytest.fixture
def simple_circuit():
    """Fixture providing a simple test circuit."""
    from circuit_sim import Circuit

    circuit = Circuit("Simple Test Circuit")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=0, resistance="1k")
    return circuit


@pytest.fixture
def rc_circuit():
    """Fixture providing an RC filter circuit."""
    from circuit_sim import Circuit

    circuit = Circuit("RC Filter")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="5V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")
    return circuit


@pytest.fixture
def voltage_divider():
    """Fixture providing a voltage divider circuit."""
    from circuit_sim import Circuit

    circuit = Circuit("Voltage Divider")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
    circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
    return circuit


# Visual Testing Framework Fixtures
@pytest.fixture
def visual_test_framework():
    """Fixture providing visual testing framework."""
    from visual_testing_framework import VisualTestFramework
    
    # Create temporary directory for test outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        framework = VisualTestFramework(temp_dir)
        yield framework


@pytest.fixture
def behavior_validator():
    """Fixture providing circuit behavior validator."""
    from visual_testing_framework import CircuitBehaviorValidator
    return CircuitBehaviorValidator()


@pytest.fixture
def reference_signal_generator():
    """Fixture providing reference signal generator."""
    from visual_testing_framework import ReferenceSignalGenerator
    return ReferenceSignalGenerator()


@pytest.fixture
def simulation_engine():
    """Fixture providing simulation engine."""
    from circuit_sim.simulator import SimulationEngine
    return SimulationEngine()


# Circuit fixtures for comprehensive testing
@pytest.fixture
def rc_lowpass_1khz():
    """RC low-pass filter with ~159 Hz cutoff (1kΩ, 1μF)."""
    from circuit_sim import Circuit
    
    circuit = Circuit("RC Low-pass 159Hz")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="1000")
    circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1e-6")
    return circuit


@pytest.fixture  
def rc_highpass_1khz():
    """RC high-pass filter with ~159 Hz cutoff (1kΩ, 1μF)."""
    from circuit_sim import Circuit
    
    circuit = Circuit("RC High-pass 159Hz")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_capacitor("C1", node1=1, node2=2, capacitance="1e-6")
    circuit.add_resistor("R1", node1=2, node2=0, resistance="1000")
    return circuit


@pytest.fixture
def rlc_bandpass_5khz():
    """RLC band-pass filter with ~5 kHz resonance."""
    from circuit_sim import Circuit
    
    circuit = Circuit("RLC Band-pass 5kHz")
    circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
    circuit.add_resistor("R1", node1=1, node2=2, resistance="100")
    circuit.add_inductor("L1", node1=2, node2=3, inductance="1e-3")
    circuit.add_capacitor("C1", node1=3, node2=0, capacitance="1e-6")
    return circuit


# Test data fixtures
@pytest.fixture
def known_good_ac_results():
    """Fixture providing known good AC analysis results for regression testing."""
    import numpy as np
    from circuit_sim.simulator.results import SimulationResults
    
    # Create reference AC results that we know should work
    results = SimulationResults("ac")
    
    # Frequency vector: 1 Hz to 100 kHz, logarithmic
    frequencies = np.logspace(0, 5, 50)  # 1 to 100,000 Hz
    results.set_frequency_vector(frequencies)
    
    # RC low-pass response (1kΩ, 1μF) - theoretical values
    omega = 2 * np.pi * frequencies
    tau = 1000 * 1e-6  # RC = 1ms
    H = 1 / (1 + 1j * omega * tau)
    
    # Add complex voltage data
    results.add_voltage(2, H)  # Output node
    results.add_voltage(1, np.ones_like(H, dtype=complex))  # Input node
    
    return results


# Pytest configuration options
def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--run-visual", 
        action="store_true", 
        default=False, 
        help="run visual comparison tests (requires PIL)"
    )
    parser.addoption(
        "--run-slow", 
        action="store_true", 
        default=False, 
        help="run slow tests including comprehensive parameter sweeps"
    )


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "visual: mark test as requiring visual comparison"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ac_analysis: mark test as AC analysis related"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--run-visual"):
        skip_visual = pytest.mark.skip(reason="need --run-visual option to run")
        for item in items:
            if "visual" in item.keywords:
                item.add_marker(skip_visual)
                
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
