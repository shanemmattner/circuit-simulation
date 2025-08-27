"""
Simulation engine that runs PySpice simulations.
"""

from typing import Optional

import numpy as np

from ..circuit import Circuit
from .builder import PySpiceBuilder
from .results import SimulationResults


class SimulationEngine:
    """Runs circuit simulations using PySpice."""

    def __init__(self):
        """Initialize the simulation engine."""
        self.builder = PySpiceBuilder()

    def simulate_dc(self, circuit: Circuit) -> SimulationResults:
        """
        Run DC operating point analysis.

        Args:
            circuit: Circuit to simulate

        Returns:
            SimulationResults with DC voltages and currents

        Raises:
            ImportError: If PySpice/ngspice not available
            RuntimeError: If simulation fails to converge
        """
        # Build PySpice circuit
        pyspice_circuit = self.builder.build_circuit(circuit)

        # Create simulator
        try:
            simulator = pyspice_circuit.simulator(temperature=25, nominal_temperature=25)
        except Exception as e:
            if "NgSpice" in str(e) or "ngspice" in str(e).lower():
                raise ImportError(
                    "ngspice is not installed. Install it with:\n"
                    "  Ubuntu/Debian: sudo apt-get install ngspice\n"
                    "  macOS: brew install ngspice\n"
                    "  Windows: Download from http://ngspice.sourceforge.net/"
                )
            raise RuntimeError(f"Failed to create simulator: {e}")

        # Run DC operating point analysis
        try:
            analysis = simulator.operating_point()
        except Exception as e:
            raise RuntimeError(f"DC simulation failed: {e}")

        # Extract results
        results = SimulationResults("dc")

        # Get node voltages
        for node in analysis.nodes.values():
            node_name = str(node)
            # PySpice node format is like "1" or "2", extract the number/name
            if node_name.startswith("v(") and node_name.endswith(")"):
                node_id = node_name[2:-1]
            else:
                node_id = node_name

            # Convert node ID to int if possible
            try:
                node_id = int(node_id)
            except ValueError:
                pass  # Keep as string

            # Get voltage value
            voltage = float(node)
            results.add_voltage(node_id, voltage)

        # Get branch currents (if available)
        for branch in analysis.branches.values():
            branch_name = str(branch)
            current = float(branch)
            results.add_current(branch_name, current)

        # Add metadata
        results.add_metadata("temperature", 25)
        results.add_metadata("circuit_name", circuit.name)

        return results

    def simulate_transient(
        self,
        circuit: Circuit,
        stop_time: float,
        step_time: Optional[float] = None,
        start_time: float = 0,
        max_time_step: Optional[float] = None,
    ) -> SimulationResults:
        """
        Run transient (time-domain) analysis.

        Args:
            circuit: Circuit to simulate
            stop_time: End time for simulation (seconds)
            step_time: Time step for output (seconds), defaults to stop_time/1000
            start_time: Start time for simulation (seconds), default 0
            max_time_step: Maximum internal time step (seconds)

        Returns:
            SimulationResults with time-varying voltages and currents

        Raises:
            ImportError: If PySpice/ngspice not available
            RuntimeError: If simulation fails
        """
        # Set defaults
        if step_time is None:
            step_time = stop_time / 1000

        # Build PySpice circuit
        pyspice_circuit = self.builder.build_circuit(circuit)

        # Create simulator
        try:
            simulator = pyspice_circuit.simulator(temperature=25, nominal_temperature=25)
        except Exception as e:
            if "NgSpice" in str(e) or "ngspice" in str(e).lower():
                raise ImportError(
                    "ngspice is not installed. Install it with:\n"
                    "  Ubuntu/Debian: sudo apt-get install ngspice\n"
                    "  macOS: brew install ngspice\n"
                    "  Windows: Download from http://ngspice.sourceforge.net/"
                )
            raise RuntimeError(f"Failed to create simulator: {e}")

        # Run transient analysis
        try:
            if max_time_step:
                analysis = simulator.transient(
                    step_time=step_time,
                    start_time=start_time,
                    end_time=stop_time,
                    max_time=max_time_step,
                )
            else:
                analysis = simulator.transient(
                    step_time=step_time, start_time=start_time, end_time=stop_time
                )
        except Exception as e:
            raise RuntimeError(f"Transient simulation failed: {e}")

        # Extract results
        results = SimulationResults("transient")

        # Get time vector
        time = np.array([float(t) for t in analysis.time])
        results.set_time_vector(time)

        # Get node voltages over time
        for node_name in analysis.nodes.keys():
            # Extract node identifier
            if node_name.startswith("v(") and node_name.endswith(")"):
                node_id = node_name[2:-1]
            else:
                node_id = node_name

            # Convert to int if possible
            try:
                node_id = int(node_id)
            except ValueError:
                pass

            # Get voltage waveform
            voltage = np.array([float(v) for v in analysis.nodes[node_name]])
            results.add_voltage(node_id, voltage)

        # Get branch currents over time (if available)
        for branch_name in analysis.branches.keys():
            current = np.array([float(i) for i in analysis.branches[branch_name]])
            results.add_current(branch_name, current)

        # Add metadata
        results.add_metadata("start_time", start_time)
        results.add_metadata("stop_time", stop_time)
        results.add_metadata("step_time", step_time)
        results.add_metadata("circuit_name", circuit.name)

        return results

    def simulate_ac(
        self,
        circuit: Circuit,
        start_frequency: float,
        stop_frequency: float,
        points_per_decade: int = 10,
        variation: str = "dec",
    ) -> SimulationResults:
        """
        Run AC (frequency-domain) analysis.

        Args:
            circuit: Circuit to simulate
            start_frequency: Starting frequency (Hz)
            stop_frequency: Ending frequency (Hz)
            points_per_decade: Number of points per decade (for log scale)
            variation: Frequency variation type ("dec" or "lin")

        Returns:
            SimulationResults with frequency response

        Raises:
            ImportError: If PySpice/ngspice not available
            RuntimeError: If simulation fails
        """
        # Generate frequency vector
        frequencies = self._generate_frequency_vector(
            start_frequency, stop_frequency, points_per_decade, variation
        )
        
        # Build PySpice circuit
        pyspice_circuit = self.builder.build_circuit(circuit)

        # Create simulator
        try:
            simulator = pyspice_circuit.simulator(temperature=25, nominal_temperature=25)
        except Exception as e:
            if "NgSpice" in str(e) or "ngspice" in str(e).lower():
                raise ImportError(
                    "ngspice is not installed. Install it with:\n"
                    "  Ubuntu/Debian: sudo apt-get install ngspice\n"
                    "  macOS: brew install ngspice\n"
                    "  Windows: Download from http://ngspice.sourceforge.net/"
                )
            raise RuntimeError(f"Failed to create simulator: {e}")

        # Run AC analysis
        try:
            if variation == "dec":
                # Use PySpice AC analysis with decade variation
                analysis = simulator.ac(
                    start_frequency=start_frequency,
                    stop_frequency=stop_frequency,
                    number_of_points=points_per_decade,
                    variation="dec"
                )
            else:
                # Linear variation - calculate total points
                num_points = len(frequencies)
                analysis = simulator.ac(
                    start_frequency=start_frequency,
                    stop_frequency=stop_frequency,
                    number_of_points=num_points,
                    variation="lin"
                )
        except Exception as e:
            raise RuntimeError(f"AC simulation failed: {e}")

        # Extract results
        results = SimulationResults("ac")
        results.set_frequency_vector(frequencies)

        # Get complex node voltages using as_ndarray() to preserve complex data
        for node_name in analysis.nodes.keys():
            # Extract node identifier  
            node_id = node_name
            
            # Convert to int if possible
            try:
                node_id = int(node_name)
            except ValueError:
                pass

            # Get complex voltage waveform using as_ndarray() method
            waveform = analysis.nodes[node_name]
            if hasattr(waveform, 'as_ndarray'):
                # This preserves complex data
                complex_voltage = waveform.as_ndarray()
            else:
                # Fallback: reconstruct from real/imag parts
                real_part = np.array([float(v) for v in waveform.real])
                imag_part = np.array([float(v) for v in waveform.imag])
                complex_voltage = real_part + 1j * imag_part
                
            results.add_voltage(node_id, complex_voltage)

        # Get complex branch currents (if available)
        for branch_name in analysis.branches.keys():
            waveform = analysis.branches[branch_name]
            if hasattr(waveform, 'as_ndarray'):
                complex_current = waveform.as_ndarray()
            else:
                # Fallback: reconstruct from real/imag parts
                real_part = np.array([float(i) for i in waveform.real])
                imag_part = np.array([float(i) for i in waveform.imag])
                complex_current = real_part + 1j * imag_part
                
            results.add_current(branch_name, complex_current)

        # Add metadata
        results.add_metadata("start_frequency", start_frequency)
        results.add_metadata("stop_frequency", stop_frequency)
        results.add_metadata("points_per_decade", points_per_decade)
        results.add_metadata("variation", variation)
        results.add_metadata("circuit_name", circuit.name)

        return results

    def _generate_frequency_vector(
        self,
        start_freq: float,
        stop_freq: float,
        points_per_decade: int,
        variation: str
    ) -> np.ndarray:
        """Generate frequency vector for AC analysis."""
        if variation == "dec":
            # Logarithmic (decade) variation
            num_decades = np.log10(stop_freq / start_freq)
            num_points = int(num_decades * points_per_decade) + 1
            return np.logspace(
                np.log10(start_freq),
                np.log10(stop_freq),
                num_points
            )
        else:
            # Linear variation
            return np.linspace(start_freq, stop_freq, 1000)

    def _calculate_component_impedance(
        self, 
        component_type: str, 
        value: float, 
        frequency: float
    ) -> complex:
        """
        Calculate complex impedance of a component at given frequency.
        
        Args:
            component_type: Type of component ("resistor", "capacitor", "inductor")
            value: Component value (resistance, capacitance, inductance)
            frequency: Frequency in Hz
            
        Returns:
            Complex impedance Z = R + jX
            
        Raises:
            ValueError: If component type is not supported
        """
        omega = 2 * np.pi * frequency  # Angular frequency
        
        if component_type == "resistor":
            # Resistor: Z = R (purely real)
            return complex(value, 0)
            
        elif component_type == "capacitor":
            # Capacitor: Z = 1/(jωC) = -j/(ωC)
            if value == 0:
                raise ValueError("Capacitor value cannot be zero")
            reactance = -1.0 / (omega * value)
            return complex(0, reactance)
            
        elif component_type == "inductor":
            # Inductor: Z = jωL
            reactance = omega * value
            return complex(0, reactance)
            
        else:
            raise ValueError(f"Unsupported component type: {component_type}")
