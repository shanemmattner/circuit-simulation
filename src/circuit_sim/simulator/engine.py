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
            NotImplementedError: AC analysis not yet fully implemented
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

        # Run AC analysis - use direct ngspice approach to get complex data
        try:
            if variation == "dec":
                # Use PySpice AC analysis with decade variation
                analysis = simulator.ac(
                    start_frequency=start_frequency,
                    stop_frequency=stop_frequency,
                    number_of_points=points_per_decade,
                    variation="dec",
                )
            else:
                # Linear variation - calculate total points
                num_points = len(frequencies)
                analysis = simulator.ac(
                    start_frequency=start_frequency,
                    stop_frequency=stop_frequency,
                    number_of_points=num_points,
                    variation="lin",
                )
        except Exception as e:
            raise RuntimeError(f"AC simulation failed: {e}")

        # Try to get complex data directly from analysis if available
        complex_data_available = self._check_complex_data_available(analysis)

        # Extract results
        results = SimulationResults("ac")
        
        # Get actual frequency vector from analysis (more accurate than our generated one)
        try:
            # Extract numeric values from PySpice FrequencyValue objects
            frequency_values = []
            for freq in analysis.frequency:
                if hasattr(freq, 'value'):
                    # PySpice FrequencyValue object - extract numeric value
                    frequency_values.append(float(freq.value))
                else:
                    # Already numeric
                    frequency_values.append(float(freq))
            
            actual_frequencies = np.array(frequency_values)
            results.set_frequency_vector(actual_frequencies)
        except Exception as e:
            import logging
            logging.warning(f"Failed to extract frequency vector from PySpice: {e}")
            # Fallback to our generated frequency vector
            results.set_frequency_vector(frequencies)

        # Get complex node voltages
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

            # Get complex voltage waveform - handle PySpice voltage units properly
            voltage_data = analysis.nodes[node_name]
            
            # Extract complex values from PySpice WaveForm using numpy
            try:
                # Use numpy to directly interpret the WaveForm as complex array
                # This preserves the complex data that individual UnitValue objects lose
                complex_voltage = np.array(voltage_data, dtype=complex)
                
                # Verify we got the complex data
                if not np.iscomplexobj(complex_voltage):
                    import logging
                    logging.warning(f"Node {node_id} numpy conversion didn't preserve complex type")
                    # Force complex dtype
                    complex_voltage = complex_voltage.astype(complex)
                
                # Verify we have meaningful data
                if len(complex_voltage) == 0:
                    import logging
                    logging.warning(f"Node {node_id} returned empty voltage data")
                    complex_voltage = np.array([complex(0, 0)], dtype=complex)
                
            except Exception as e:
                # Fallback: try simpler conversion
                import logging
                logging.error(f"Failed to extract voltage for node {node_id}: {e}")
                
                try:
                    # Try direct numpy conversion as last resort
                    complex_voltage = np.array(voltage_data, dtype=complex)
                except:
                    # Ultimate fallback - zero voltage
                    complex_voltage = np.array([complex(0, 0)], dtype=complex)
            
            results.add_voltage(node_id, complex_voltage)

        # Get complex branch currents (if available)
        for branch_name in analysis.branches.keys():
            complex_current = np.array([complex(i) for i in analysis.branches[branch_name]])
            results.add_current(branch_name, complex_current)

        # Add metadata
        results.add_metadata("start_frequency", start_frequency)
        results.add_metadata("stop_frequency", stop_frequency)
        results.add_metadata("points_per_decade", points_per_decade)
        results.add_metadata("variation", variation)
        results.add_metadata("circuit_name", circuit.name)

        return results

    def _check_complex_data_available(self, analysis) -> bool:
        """Check if PySpice analysis contains complex data."""
        try:
            for node_name in analysis.nodes.keys():
                node_data = analysis.nodes[node_name]
                for v in node_data:
                    if hasattr(v, '_value'):
                        # Check if _value is complex or if we can access the raw complex data
                        val = v._value
                        if hasattr(val, 'imag') and val.imag != 0:
                            return True
                    break  # Just check first value
                break
            return False
        except:
            return False

    def _extract_complex_data_manual(self, analysis) -> dict:
        """Manually extract complex data by directly accessing ngspice data structures."""
        complex_data = {}
        
        # Try to access the raw simulation data from PySpice/ngspice
        try:
            # Access the raw ngspice data if possible
            if hasattr(analysis, '_simulation') and hasattr(analysis._simulation, 'plot'):
                plot = analysis._simulation.plot
                if hasattr(plot, 'data'):
                    # Extract complex data from raw ngspice plot data
                    for node_name in analysis.nodes.keys():
                        if node_name in plot.data:
                            raw_data = plot.data[node_name]
                            if hasattr(raw_data, 'real') and hasattr(raw_data, 'imag'):
                                complex_voltages = raw_data.real + 1j * raw_data.imag
                                complex_data[node_name] = complex_voltages
                                
            # Alternative: try to reconstruct from magnitude/phase if available            
            if not complex_data:
                for node_name in analysis.nodes.keys():
                    if hasattr(analysis, 'magnitude') and hasattr(analysis, 'phase'):
                        mag_data = getattr(analysis.magnitude, node_name, None)
                        phase_data = getattr(analysis.phase, node_name, None)
                        if mag_data is not None and phase_data is not None:
                            # Reconstruct complex from magnitude/phase
                            magnitude = np.array([float(m.value if hasattr(m, 'value') else m) for m in mag_data])
                            phase_rad = np.array([float(p.value if hasattr(p, 'value') else p) for p in phase_data])
                            complex_voltages = magnitude * np.exp(1j * phase_rad)
                            complex_data[node_name] = complex_voltages
                            
        except Exception as e:
            import logging
            logging.debug(f"Failed to extract complex data manually: {e}")
            
        return complex_data

    def _generate_frequency_vector(
        self, start_freq: float, stop_freq: float, points_per_decade: int, variation: str
    ) -> np.ndarray:
        """Generate frequency vector for AC analysis."""
        if variation == "dec":
            # Logarithmic (decade) variation
            num_decades = np.log10(stop_freq / start_freq)
            num_points = int(num_decades * points_per_decade) + 1
            return np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)
        else:
            # Linear variation
            return np.linspace(start_freq, stop_freq, 1000)
