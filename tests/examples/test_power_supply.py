"""Tests for complete power supply circuit."""

import numpy as np

from examples.power.power_supply import (
    PowerSupplyCircuit,
    calculate_efficiency,
    design_regulated_supply,
    simulate_power_supply,
)


class TestPowerSupply:
    """Test power supply implementation."""

    def test_linear_regulator(self):
        """Test linear regulated power supply."""
        circuit = PowerSupplyCircuit(
            v_ac_input=15,  # 15V AC RMS
            v_dc_output=12,  # 12V DC regulated
            i_max=1.0,  # 1A max current
            regulator_type="linear",
        )

        assert circuit.v_ac_input == 15
        assert circuit.v_dc_output == 12
        assert circuit.i_max == 1.0

        # Check regulation
        regulation = circuit.calculate_load_regulation()
        assert regulation < 5  # Less than 5% regulation

    def test_switching_regulator(self):
        """Test switching power supply."""
        circuit = PowerSupplyCircuit(
            v_ac_input=15,
            v_dc_output=5,  # Step down to 5V
            i_max=2.0,
            regulator_type="switching",
            switching_freq=100e3,  # 100kHz
        )

        assert circuit.regulator_type == "switching"
        assert circuit.switching_freq == 100e3

        # Switching should be more efficient
        efficiency = circuit.calculate_efficiency()
        assert efficiency > 80  # >80% efficiency

    def test_ripple_rejection(self):
        """Test ripple rejection."""
        circuit = PowerSupplyCircuit(
            v_ac_input=12, v_dc_output=9, i_max=0.5, regulator_type="linear"
        )

        # Calculate ripple rejection ratio
        ripple_rejection = circuit.calculate_ripple_rejection()
        assert ripple_rejection > 40  # >40dB rejection


class TestPowerSupplySimulation:
    """Test power supply simulation."""

    def test_load_transient(self):
        """Test load transient response."""
        circuit = PowerSupplyCircuit(
            v_ac_input=15, v_dc_output=12, i_max=1.0, regulator_type="linear"
        )

        results = simulate_power_supply(
            circuit, load_profile="step", duration=100e-3  # Step load change
        )

        assert "time" in results
        assert "v_out" in results
        assert "i_load" in results

        # Output should stay regulated
        v_out = np.array(results["v_out"])
        steady_state = v_out[len(v_out) // 2 :]

        # Check regulation
        assert np.mean(steady_state) > 11.5
        assert np.mean(steady_state) < 12.5


class TestEfficiency:
    """Test efficiency calculations."""

    def test_efficiency_calculation(self):
        """Test power supply efficiency."""
        circuit = PowerSupplyCircuit(
            v_ac_input=15, v_dc_output=12, i_max=1.0, regulator_type="linear"
        )

        eff_data = calculate_efficiency(circuit, load_current=0.5)

        assert "efficiency" in eff_data
        assert "power_in" in eff_data
        assert "power_out" in eff_data
        assert "power_loss" in eff_data

        # Linear regulator efficiency
        assert 60 < eff_data["efficiency"] < 85


class TestDesign:
    """Test power supply design."""

    def test_design_regulated_supply(self):
        """Test designing regulated supply."""
        supply = design_regulated_supply(
            v_out=5.0,  # 5V output
            i_out=2.0,  # 2A output
            ripple_max=50e-3,  # 50mV ripple
            v_ac_available=12,  # 12V AC available
        )

        assert supply.v_dc_output == 5.0
        assert supply.i_max >= 2.0

        # Should meet ripple spec
        ripple = supply.calculate_output_ripple()
        assert ripple <= 50e-3
