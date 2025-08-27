#!/usr/bin/env python3
"""
Test script to verify ngspice is working correctly in Docker.
Run with: docker-compose run circuit-sim python examples/test_docker_ngspice.py
"""

import sys
import os


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")

    try:
        import numpy as np

        print(f"  ✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"  ✗ NumPy import failed: {e}")
        return False

    try:
        import matplotlib

        print(f"  ✓ Matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"  ✗ Matplotlib import failed: {e}")
        return False

    try:
        import PySpice

        print(f"  ✓ PySpice {PySpice.__version__}")
    except ImportError as e:
        print(f"  ✗ PySpice import failed: {e}")
        return False

    try:
        from circuit_sim import Circuit

        print(f"  ✓ circuit_sim package")
    except ImportError as e:
        print(f"  ✗ circuit_sim import failed: {e}")
        return False

    return True


def test_ngspice_library():
    """Test that ngspice library is accessible."""
    print("\nTesting ngspice library...")

    # Check environment variable
    lib_path = os.environ.get("PYSPICE_NGSPICE_LIBRARY", "")
    if lib_path:
        print(f"  PYSPICE_NGSPICE_LIBRARY = {lib_path}")
        if os.path.exists(lib_path):
            print(f"  ✓ Library file exists")
        else:
            print(f"  ✗ Library file not found at {lib_path}")
            return False
    else:
        print("  ⚠ PYSPICE_NGSPICE_LIBRARY not set")

    # Try to import PySpice's NgSpice module
    try:
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared

        print("  ✓ NgSpiceShared module imported")

        # Try to create an instance (this will fail if ngspice lib not found)
        try:
            ngspice = NgSpiceShared.new_instance()
            print("  ✓ NgSpice instance created successfully!")
            return True
        except Exception as e:
            print(f"  ✗ Failed to create NgSpice instance: {e}")
            return False

    except ImportError as e:
        print(f"  ✗ NgSpiceShared import failed: {e}")
        return False


def test_simple_circuit():
    """Test creating and simulating a simple circuit."""
    print("\nTesting simple circuit simulation...")

    try:
        from circuit_sim import Circuit
        from circuit_sim.simulator import SimulationEngine

        # Create a simple voltage divider
        circuit = Circuit("Test Voltage Divider")
        circuit.add_voltage_source("V1", 1, 0, "10V")
        circuit.add_resistor("R1", 1, 2, "1k")
        circuit.add_resistor("R2", 2, 0, "1k")

        print(f"  ✓ Circuit created: {circuit}")

        # Try to simulate
        engine = SimulationEngine()
        try:
            results = engine.simulate_dc(circuit)
            print("  ✓ DC simulation completed successfully!")

            # Check results
            v1 = results.voltage(1)
            v2 = results.voltage(2)
            if v1 is not None and v2 is not None:
                print(f"    Node 1: {v1[0]:.2f}V")
                print(f"    Node 2: {v2[0]:.2f}V (expected ~5V)")
                return True
            else:
                print("  ✗ Could not extract voltage results")
                return False

        except Exception as e:
            print(f"  ✗ Simulation failed: {e}")
            return False

    except Exception as e:
        print(f"  ✗ Circuit creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Docker NgSpice Test Suite")
    print("=" * 60)

    success = True

    # Run tests
    if not test_imports():
        success = False

    if not test_ngspice_library():
        success = False
        print("\n⚠ NgSpice library not working.")
        print("  This is expected if ngspice is not installed in the container.")
        print("  The Docker image should have ngspice pre-installed.")

    if not test_simple_circuit():
        success = False
        print("\n⚠ Circuit simulation not working.")
        print("  This requires a working ngspice installation.")

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Docker environment is working correctly.")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        print("\nTo fix ngspice issues in Docker:")
        print("1. Ensure the Dockerfile installs ngspice correctly")
        print("2. Check that PYSPICE_NGSPICE_LIBRARY points to the right path")
        print("3. Verify the ngspice library is compatible with PySpice")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
