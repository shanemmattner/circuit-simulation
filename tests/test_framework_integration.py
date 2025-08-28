"""
Simple integration test to verify the visual testing framework works.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))


def test_framework_imports():
    """Test that all framework components can be imported."""

    try:
        from visual_testing_framework import (
            VisualTestFramework,
            CircuitBehaviorValidator,
            ReferenceSignalGenerator,
            VisualTestResult,
        )

        # Test basic instantiation
        framework = VisualTestFramework("test_output")
        validator = CircuitBehaviorValidator()
        reference_gen = ReferenceSignalGenerator()

        assert framework is not None
        assert validator is not None
        assert reference_gen is not None

    except ImportError as e:
        pytest.fail(f"Framework import failed: {e}")


def test_claude_helper_imports():
    """Test that Claude helper can be imported."""

    try:
        from claude_test_helper import ClaudeTestHelper

        helper = ClaudeTestHelper()
        assert helper is not None

        # Test command generation
        command = helper.get_test_command_for_claude("quick")
        assert "python" in command
        assert "tests" in command

    except ImportError as e:
        pytest.fail(f"Claude helper import failed: {e}")


def test_circuit_sim_imports():
    """Test that circuit simulation components work."""

    try:
        from circuit_sim import Circuit
        from circuit_sim.simulator import SimulationEngine

        # Test basic circuit creation
        circuit = Circuit("Test Circuit")
        circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="1V")
        circuit.add_resistor("R1", node1=1, node2=0, resistance="1000")

        assert len(circuit.components) == 2

        # Test engine creation (may fail if PySpice not available, which is expected)
        engine = SimulationEngine()
        assert engine is not None

    except ImportError as e:
        pytest.fail(f"Circuit simulation import failed: {e}")


if __name__ == "__main__":
    test_framework_imports()
    test_claude_helper_imports()
    test_circuit_sim_imports()
    print("✅ All integration tests passed!")
