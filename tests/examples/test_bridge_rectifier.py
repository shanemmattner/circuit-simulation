"""Tests for bridge rectifier circuit."""

import numpy as np

from examples.power.bridge_rectifier import (
    BridgeRectifierCircuit,
    calculate_ripple,
    design_power_supply,
    simulate_rectifier,
)


class TestBridgeRectifier:
    """Test bridge rectifier implementation."""

    def test_basic_rectifier(self):
        """Test basic bridge rectifier."""
        circuit = BridgeRectifierCircuit(
            v_ac_rms=12,  # 12V AC RMS
            frequency=60,  # 60Hz
            load_resistance=100,
            filter_capacitor=None,  # No filtering
        )

        assert circuit.v_ac_rms == 12
        assert circuit.v_ac_peak == 12 * np.sqrt(2)
        assert circuit.frequency == 60

        # DC output without filter = 0.637 * Vpeak (theoretical)
        expected_dc = 0.637 * circuit.v_ac_peak
        assert abs(circuit.v_dc_no_load - expected_dc) < 1

    def test_with_filter_capacitor(self):
        """Test rectifier with smoothing capacitor."""
        circuit = BridgeRectifierCircuit(
            v_ac_rms=12,
            frequency=60,
            load_resistance=100,
            filter_capacitor=1000e-6,  # 1000µF
        )

        assert circuit.filter_capacitor == 1000e-6

        # Calculate ripple
        ripple = circuit.calculate_ripple_voltage()

        # Ripple should be small with large capacitor
        assert ripple < 2.0  # Less than 2V ripple
        assert ripple > 0.1  # But not zero

    def test_load_regulation(self):
        """Test load regulation."""
        circuit = BridgeRectifierCircuit(
            v_ac_rms=12, frequency=60, load_resistance=100, filter_capacitor=1000e-6
        )

        # No load voltage
        v_no_load = circuit.v_dc_no_load

        # Full load voltage
        v_full_load = circuit.calculate_output_voltage()

        # Voltage should drop under load
        assert v_full_load < v_no_load

        # Calculate regulation
        regulation = (v_no_load - v_full_load) / v_full_load * 100
        assert 0 < regulation < 20  # Reasonable regulation


class TestRectifierSimulation:
    """Test rectifier simulation."""

    def test_simulation_no_filter(self):
        """Test simulation without filter."""
        circuit = BridgeRectifierCircuit(v_ac_rms=12, frequency=60, load_resistance=100)

        results = simulate_rectifier(circuit, duration=50e-3)  # 3 cycles

        assert "time" in results
        assert "v_in" in results
        assert "v_out" in results
        assert "i_load" in results

        # Output should be rectified (all positive)
        v_out = np.array(results["v_out"])
        assert np.all(v_out >= -0.1)  # Allow small negative for diode drops

        # Should have twice the input frequency
        assert results.get("output_frequency", 0) > 100  # ~120Hz for 60Hz input

    def test_simulation_with_filter(self):
        """Test simulation with filter capacitor."""
        circuit = BridgeRectifierCircuit(
            v_ac_rms=12, frequency=60, load_resistance=100, filter_capacitor=1000e-6
        )

        results = simulate_rectifier(circuit, duration=100e-3)

        # Check ripple is reduced
        v_out = np.array(results["v_out"])

        # After initial transient, ripple should be small
        steady_state = v_out[len(v_out) // 2 :]
        ripple = np.max(steady_state) - np.min(steady_state)

        assert ripple < 2.0  # Less than 2V ripple


class TestRippleCalculation:
    """Test ripple calculations."""

    def test_ripple_calculation(self):
        """Test ripple voltage calculation."""
        circuit = BridgeRectifierCircuit(
            v_ac_rms=12, frequency=60, load_resistance=100, filter_capacitor=1000e-6
        )

        ripple_data = calculate_ripple(circuit)

        assert "ripple_voltage" in ripple_data
        assert "ripple_percent" in ripple_data
        assert "ripple_frequency" in ripple_data

        # Ripple frequency should be 2x input for full-wave
        assert ripple_data["ripple_frequency"] == 120

        # Ripple percentage should be reasonable
        assert 0 < ripple_data["ripple_percent"] < 20


class TestPowerSupplyDesign:
    """Test power supply design."""

    def test_design_power_supply(self):
        """Test designing complete power supply."""
        supply = design_power_supply(
            v_out=12,  # 12V DC output
            i_out=1,  # 1A output
            ripple_max=0.5,  # 0.5V max ripple
            v_ac_rms=15,  # 15V AC input
        )

        assert supply.filter_capacitor > 0
        assert supply.load_resistance == 12  # V/I

        # Check ripple meets spec
        ripple = supply.calculate_ripple_voltage()
        assert ripple <= 0.5
