"""
Network analysis functions for circuit analysis.

Provides functions for calculating Thevenin equivalent parameters,
including open-circuit voltage (Vth) and Thevenin resistance (Rth).
"""

from typing import Dict, Union

from ..circuit import Circuit
from ..simulator import SimulationEngine


def calculate_open_circuit_voltage(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> float:
    """Calculate open-circuit voltage between two terminals.

    The open-circuit voltage (Vth) is the voltage that appears across
    the two terminals when nothing is connected between them.
    This is also known as the Thevenin voltage.

    Args:
        circuit: Circuit to analyze
        terminal_pos: Positive terminal node
        terminal_neg: Negative terminal node

    Returns:
        Open-circuit voltage in Volts (V_pos - V_neg)

    Raises:
        ValueError: If terminals are invalid
        RuntimeError: If simulation fails

    Example:
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> vth = calculate_open_circuit_voltage(circuit, 2, 0)
        >>> print(f"Vth = {vth:.2f}V")  # Should be ~5V
    """
    # Normalize terminal names
    if terminal_pos == "gnd":
        terminal_pos = 0
    if terminal_neg == "gnd":
        terminal_neg = 0

    # Validate terminals exist in circuit
    if terminal_pos not in circuit.nodes:
        raise ValueError(f"Terminal {terminal_pos} not found in circuit")
    if terminal_neg not in circuit.nodes:
        raise ValueError(f"Terminal {terminal_neg} not found in circuit")

    # Run DC operating point simulation
    engine = SimulationEngine()
    results = engine.simulate_dc(circuit)

    # Get voltages at both terminals
    voltage_pos = results.voltage(terminal_pos)
    voltage_neg = results.voltage(terminal_neg)

    if voltage_pos is None:
        raise RuntimeError(f"Could not get voltage at terminal {terminal_pos}")
    if voltage_neg is None:
        raise RuntimeError(f"Could not get voltage at terminal {terminal_neg}")

    # Open-circuit voltage is the difference
    # Get the last value (DC value) from the voltage array
    v_pos = float(voltage_pos[-1]) if len(voltage_pos) > 0 else float(voltage_pos[0])
    v_neg = float(voltage_neg[-1]) if len(voltage_neg) > 0 else float(voltage_neg[0])

    return v_pos - v_neg


def calculate_thevenin_resistance(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> float:
    """Calculate Thevenin resistance seen from two terminals.

    The Thevenin resistance (Rth) is the equivalent resistance looking
    into the circuit from the specified terminals with all independent
    sources set to zero (voltage sources replaced by short circuits,
    current sources replaced by open circuits).

    Args:
        circuit: Circuit to analyze
        terminal_pos: Positive terminal node
        terminal_neg: Negative terminal node

    Returns:
        Thevenin resistance in Ohms

    Raises:
        ValueError: If terminals are invalid
        RuntimeError: If simulation fails

    Example:
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> rth = calculate_thevenin_resistance(circuit, 2, 0)
        >>> print(f"Rth = {rth:.0f}Ω")  # Should be ~500Ω
    """
    # Normalize terminal names
    if terminal_pos == "gnd":
        terminal_pos = 0
    if terminal_neg == "gnd":
        terminal_neg = 0

    # Validate terminals exist in circuit
    if terminal_pos not in circuit.nodes:
        raise ValueError(f"Terminal {terminal_pos} not found in circuit")
    if terminal_neg not in circuit.nodes:
        raise ValueError(f"Terminal {terminal_neg} not found in circuit")

    # Create a modified circuit with sources set to zero
    modified_circuit = _zero_sources(circuit)

    # Run DC operating point simulation
    engine = SimulationEngine()
    results = engine.simulate_dc(modified_circuit)

    # Get voltages at both terminals
    voltage_pos = results.voltage(terminal_pos)
    voltage_neg = results.voltage(terminal_neg)

    if voltage_pos is None:
        raise RuntimeError(f"Could not get voltage at terminal {terminal_pos}")
    if voltage_neg is None:
        raise RuntimeError(f"Could not get voltage at terminal {terminal_neg}")

    # Calculate voltage difference
    v_pos = float(voltage_pos[-1]) if len(voltage_pos) > 0 else float(voltage_pos[0])
    v_neg = float(voltage_neg[-1]) if len(voltage_neg) > 0 else float(voltage_neg[0])
    voltage_diff = v_pos - v_neg

    # Inject a test current and measure the voltage response
    # Rth = V_test / I_test
    test_circuit = _inject_test_current(modified_circuit, terminal_pos, terminal_neg)
    test_results = engine.simulate_dc(test_circuit)

    # Get the voltage at terminal_pos with the test current
    test_voltage_pos = test_results.voltage(terminal_pos)
    test_voltage_neg = test_results.voltage(terminal_neg)

    if test_voltage_pos is None or test_voltage_neg is None:
        raise RuntimeError("Failed to get test voltage for Rth calculation")

    t_v_pos = float(test_voltage_pos[-1]) if len(test_voltage_pos) > 0 else float(test_voltage_pos[0])
    t_v_neg = float(test_voltage_neg[-1]) if len(test_voltage_neg) > 0 else float(test_voltage_neg[0])
    test_voltage_diff = t_v_pos - t_v_neg

    # The change in voltage divided by the test current gives Rth
    # Using 1A test current for simplicity
    TEST_CURRENT = 1.0  # 1 Ampere

    # Rth = (V_with_test - V_without_test) / I_test
    rth = abs(test_voltage_diff - voltage_diff) / TEST_CURRENT

    return rth


def _zero_sources(circuit: Circuit) -> Circuit:
    """Create a copy of the circuit with all sources set to zero.

    Voltage sources are replaced with short circuits (0V sources).
    Current sources are replaced with open circuits (0A sources).

    Args:
        circuit: Original circuit

    Returns:
        New circuit with sources zeroed
    """
    # Create a new circuit with the same name
    new_circuit = Circuit(circuit.name + "_zeroed")

    # Copy all components
    for comp in circuit.components:
        comp_type = comp.get("type")

        if comp_type == "voltage_source":
            # Replace voltage source with 0V source (short circuit)
            new_circuit.add_voltage_source(
                name=comp["name"],
                positive=comp["positive"],
                negative=comp["negative"],
                dc_value="0V",
            )
        elif comp_type == "current_source":
            # Replace current source with 0A source (open circuit)
            # We add a very high resistance in series to simulate open circuit
            new_circuit.add_resistor(
                name=f"open_{comp['name']}",
                node1=comp["positive"],
                node2=comp["negative"],
                resistance="1G",  # 1 Giga-ohm = open circuit
            )
        elif comp_type == "resistor":
            new_circuit.add_resistor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                resistance=comp["resistance"],
            )
        elif comp_type == "capacitor":
            new_circuit.add_capacitor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                capacitance=comp["capacitance"],
            )
        elif comp_type == "inductor":
            new_circuit.add_inductor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                inductance=comp["inductance"],
            )
        elif comp_type == "diode":
            new_circuit.add_diode(
                name=comp["name"],
                anode=comp["anode"],
                cathode=comp["cathode"],
                model=comp.get("model", "1N4148"),
            )
        elif comp_type == "bjt_transistor":
            new_circuit.add_bjt_transistor(
                name=comp["name"],
                collector=comp["collector"],
                base=comp["base"],
                emitter=comp["emitter"],
                model=comp.get("model", "2N3904"),
            )
        # Add other component types as needed

    return new_circuit


def _inject_test_current(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> Circuit:
    """Inject a test current between two terminals to measure resistance.

    Args:
        circuit: Circuit to modify
        terminal_pos: Positive terminal
        terminal_neg: Negative terminal

    Returns:
        New circuit with test current injected
    """
    # Create a new circuit
    new_circuit = Circuit(circuit.name + "_test")

    # Copy all components from the zeroed source circuit
    for comp in circuit.components:
        comp_type = comp.get("type")

        if comp_type == "voltage_source":
            new_circuit.add_voltage_source(
                name=comp["name"],
                positive=comp["positive"],
                negative=comp["negative"],
                dc_value=comp["dc_value"],
            )
        elif comp_type == "current_source":
            # Skip current sources (open circuits)
            continue
        elif comp_type == "resistor":
            new_circuit.add_resistor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                resistance=comp["resistance"],
            )
        elif comp_type == "capacitor":
            new_circuit.add_capacitor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                capacitance=comp["capacitance"],
            )
        elif comp_type == "inductor":
            new_circuit.add_inductor(
                name=comp["name"],
                node1=comp["node1"],
                node2=comp["node2"],
                inductance=comp["inductance"],
            )
        elif comp_type == "diode":
            new_circuit.add_diode(
                name=comp["name"],
                anode=comp["anode"],
                cathode=comp["cathode"],
                model=comp.get("model", "1N4148"),
            )
        elif comp_type == "bjt_transistor":
            new_circuit.add_bjt_transistor(
                name=comp["name"],
                collector=comp["collector"],
                base=comp["base"],
                emitter=comp["emitter"],
                model=comp.get("model", "2N3904"),
            )

    # Add a 1A test current source from terminal_neg to terminal_pos
    # (flowing from negative to positive terminal)
    new_circuit.add_current_source(
        name="I_TEST",
        positive=terminal_pos,
        negative=terminal_neg,
        dc_value="1A",
    )

    return new_circuit
