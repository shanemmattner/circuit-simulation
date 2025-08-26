"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if src_path not in sys.path:
    sys.path.insert(0, str(src_path))


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
