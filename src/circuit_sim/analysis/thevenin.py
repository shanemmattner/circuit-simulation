"""
Thevenin and Norton equivalent circuit analysis.

Provides functions for calculating Thevenin equivalent parameters
and Norton current (In = Vth/Rth).
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Union

from ..circuit import Circuit


@dataclass
class TheveninResult:
    """Result of Thevenin/Norton equivalent analysis.
    
    Attributes:
        rth: Thevenin resistance in Ohms
        vth: Thevenin voltage in Volts (None if not calculated)
        in_value: Norton current in Amps (calculated as Vth/Rth if Vth is available)
        terminals: Tuple of (terminal_pos, terminal_neg)
    """

    rth: float
    vth: Optional[float]
    terminals: Tuple[Union[int, str], Union[int, str]]

    @property
    def in_value(self) -> Optional[float]:
        """Calculate Norton current (In = Vth/Rth).
        
        Returns:
            Norton current in Amps, or None if Vth is not available.
        """
        if self.vth is None:
            return None
        return self.vth / self.rth


def calculate_rth(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> float:
    """Calculate Thevenin resistance (Rth) seen from two terminals.

    The Thevenin resistance is the equivalent resistance looking into
    the circuit from the specified terminals with all independent sources
    set to zero (voltage sources replaced by short circuits, current sources
    replaced by open circuits).

    Args:
        circuit: Circuit to analyze
        terminal_pos: Positive terminal
        terminal_neg: Negative terminal

    Returns:
        Thevenin resistance in Ohms

    Raises:
        ValueError: If terminals are invalid

    Example:
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> rth = calculate_rth(circuit, terminal_pos=2, terminal_neg=0)
        >>> print(f"Rth = {rth:.0f}Ω")  # Should be ~500Ω
    """
    from .network import calculate_thevenin_resistance

    return calculate_thevenin_resistance(circuit, terminal_pos, terminal_neg)


def calculate_thevenin(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> Dict[str, float]:
    """Calculate Thevenin equivalent circuit parameters.

    Returns the open-circuit voltage (Vth) and Thevenin resistance (Rth)
    as seen from the specified terminals. Also calculates Norton current.

    Args:
        circuit: Circuit to analyze
        terminal_pos: Positive terminal of the two-terminal network
        terminal_neg: Negative terminal of the two-terminal network

    Returns:
        Dictionary with:
        - 'vth': Open-circuit voltage (Thevenin voltage) in Volts
        - 'rth': Thevenin resistance in Ohms
        - 'in': Norton current (Vth/Rth) in Amps

    Raises:
        ValueError: If terminals are invalid
        RuntimeError: If simulation fails

    Example:
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> thevenin = calculate_thevenin(circuit, 2, 0)
        >>> print(f"Vth={thevenin['vth']:.2f}V, Rth={thevenin['rth']:.0f}Ω, In={thevenin['in']*1000:.2f}mA")
    """
    from .network import calculate_open_circuit_voltage, calculate_thevenin_resistance

    # Calculate open-circuit voltage (Vth)
    vth = calculate_open_circuit_voltage(circuit, terminal_pos, terminal_neg)

    # Calculate Thevenin resistance (Rth)
    rth = calculate_thevenin_resistance(circuit, terminal_pos, terminal_neg)

    # Calculate Norton current (In = Vth/Rth)
    in_value = vth / rth

    return {"vth": vth, "rth": rth, "in": in_value}


def calculate_norton_current(
    circuit: Circuit,
    terminal_pos: Union[int, str],
    terminal_neg: Union[int, str],
) -> float:
    """Calculate Norton current (short-circuit current).

    The Norton current is the current that would flow through a short circuit
    connected between the two terminals. It is calculated as In = Vth / Rth.

    Args:
        circuit: Circuit to analyze
        terminal_pos: Positive terminal
        terminal_neg: Negative terminal

    Returns:
        Norton current in Amps (flowing from positive to negative terminal)

    Raises:
        ValueError: If terminals are invalid
        RuntimeError: If simulation fails

    Example:
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> in_current = calculate_norton_current(circuit, 2, 0)
        >>> print(f"In = {in_current*1000:.2f}mA")  # Should be ~5mA
    """
    thevenin = calculate_thevenin(circuit, terminal_pos, terminal_neg)
    return thevenin["in"]


class TheveninAnalyzer:
    """Analyzer for Thevenin and Norton equivalent circuits.

    Provides methods to calculate Thevenin resistance, voltage, and Norton current
    for two-terminal networks.

    Example:
        >>> analyzer = TheveninAnalyzer()
        >>> circuit = Circuit("Voltage Divider")
        >>> circuit.add_voltage_source("V1", positive=1, negative=0, dc_value="10V")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_resistor("R2", node1=2, node2=0, resistance="1k")
        >>> result = analyzer.calculate_thevenin(circuit, 2, 0)
        >>> print(f"Vth={result.vth:.2f}V, Rth={result.rth:.0f}Ω, In={result.in_value*1000:.2f}mA")
    """

    def calculate_rth(
        self,
        circuit: Circuit,
        terminal_pos: Union[int, str],
        terminal_neg: Union[int, str],
    ) -> TheveninResult:
        """Calculate Thevenin resistance.

        Args:
            circuit: Circuit to analyze
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            TheveninResult with rth calculated (vth will be None)
        """
        rth = calculate_rth(circuit, terminal_pos, terminal_neg)
        return TheveninResult(rth=rth, vth=None, terminals=(terminal_pos, terminal_neg))

    def calculate_thevenin(
        self,
        circuit: Circuit,
        terminal_pos: Union[int, str],
        terminal_neg: Union[int, str],
    ) -> TheveninResult:
        """Calculate Thevenin equivalent parameters.

        Calculates both Thevenin voltage (Vth) and resistance (Rth),
        and derives the Norton current (In = Vth/Rth).

        Args:
            circuit: Circuit to analyze
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            TheveninResult with vth, rth, and in_value calculated
        """
        result = calculate_thevenin(circuit, terminal_pos, terminal_neg)
        return TheveninResult(
            rth=result["rth"],
            vth=result["vth"],
            terminals=(terminal_pos, terminal_neg),
        )

    def calculate_norton(
        self,
        circuit: Circuit,
        terminal_pos: Union[int, str],
        terminal_neg: Union[int, str],
    ) -> TheveninResult:
        """Calculate Norton current (alias for calculate_thevenin).

        Args:
            circuit: Circuit to analyze
            terminal_pos: Positive terminal
            terminal_neg: Negative terminal

        Returns:
            TheveninResult with Norton current calculated
        """
        return self.calculate_thevenin(circuit, terminal_pos, terminal_neg)
