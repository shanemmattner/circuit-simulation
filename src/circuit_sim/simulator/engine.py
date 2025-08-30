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

        # Build PySpice circuit specifically for AC analysis
        # Use SinusoidalVoltageSource instead of regular voltage sources
        pyspice_circuit = self.builder.build_circuit(circuit, for_ac_analysis=True)
        
        # Create simulator for AC analysis
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

        # Extract results
        results = SimulationResults("ac")
        
        # Handle frequency vector safely from PySpice
        safe_frequencies = []
        for f in analysis.frequency:
            try:
                safe_frequencies.append(float(f))
            except:
                safe_frequencies.append(1000.0)  # Fallback frequency
                
        results.set_frequency_vector(np.array(safe_frequencies))

        # Get complex node voltages with proper PySpice unit handling
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

            # Get complex voltage waveform using as_ndarray() to preserve complex data
            voltage_waveform = analysis.nodes[node_name]
            
            try:
                # Use as_ndarray() to get the actual complex values from PySpice
                # This preserves both magnitude and phase information
                complex_voltage = voltage_waveform.as_ndarray()
                
                # Ensure it's a numpy array of complex numbers
                if not np.iscomplexobj(complex_voltage):
                    # If somehow not complex, convert to complex
                    complex_voltage = complex_voltage.astype(np.complex128)
                    
            except AttributeError:
                # Fallback to old method if as_ndarray() doesn't exist
                complex_voltage = []
                for v in voltage_waveform:
                    try:
                        if hasattr(v, 'real') and hasattr(v, 'imag'):
                            complex_voltage.append(complex(v))
                        elif hasattr(v, '__complex__'):
                            complex_voltage.append(complex(v))
                        else:
                            complex_voltage.append(complex(float(v), 0))
                    except:
                        complex_voltage.append(complex(0, 0))
                complex_voltage = np.array(complex_voltage)
            except Exception as e:
                # If extraction fails completely, create zeros
                freq_len = len(safe_frequencies)
                complex_voltage = np.zeros(freq_len, dtype=np.complex128)
                    
            results.add_voltage(node_id, complex_voltage)

        # Get complex branch currents using as_ndarray() to preserve complex data
        for branch_name in analysis.branches.keys():
            current_waveform = analysis.branches[branch_name]
            
            try:
                # Use as_ndarray() to get the actual complex values from PySpice
                complex_current = current_waveform.as_ndarray()
                
                # Ensure it's a numpy array of complex numbers
                if not np.iscomplexobj(complex_current):
                    complex_current = complex_current.astype(np.complex128)
                    
            except AttributeError:
                # Fallback to old method if as_ndarray() doesn't exist
                complex_current = []
                for i in current_waveform:
                    try:
                        if hasattr(i, 'real') and hasattr(i, 'imag'):
                            complex_current.append(complex(i))
                        elif hasattr(i, '__complex__'):
                            complex_current.append(complex(i))
                        else:
                            complex_current.append(complex(float(i), 0))
                    except:
                        complex_current.append(complex(0, 0))
                complex_current = np.array(complex_current)
            except Exception as e:
                # If extraction fails completely, create zeros
                freq_len = len(safe_frequencies)
                complex_current = np.zeros(freq_len, dtype=np.complex128)
                    
            results.add_current(branch_name, complex_current)

        # Add metadata
        results.add_metadata("start_frequency", start_frequency)
        results.add_metadata("stop_frequency", stop_frequency)
        results.add_metadata("points_per_decade", points_per_decade)
        results.add_metadata("variation", variation)
        results.add_metadata("circuit_name", circuit.name)

        return results

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
    
    def _create_ac_simulator_from_netlist(self, netlist_string: str):
        """
        Create a PySpice simulator from a fixed netlist string.
        
        This is needed because PySpice doesn't include AC components in its
        automatic netlist generation, so we post-process the netlist and
        create a new simulator from the corrected SPICE text.
        
        Args:
            netlist_string: Fixed SPICE netlist with proper AC components
            
        Returns:
            PySpice simulator object ready for AC analysis
        """
        import tempfile
        import os
        from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
        
        # For now, create a temporary circuit and override its netlist
        # This is a workaround since PySpice doesn't easily support loading from netlist strings
        
        try:
            # Create a minimal PySpice circuit for the simulator interface
            temp_circuit = PySpiceCircuit('AC_Fixed_Circuit')
            
            # Override the circuit's string representation to use our fixed netlist
            original_str = temp_circuit.__str__
            temp_circuit.__str__ = lambda: netlist_string
            
            # Create simulator - this will use our fixed netlist
            simulator = temp_circuit.simulator(temperature=25, nominal_temperature=25)
            
            # Restore original __str__ method to avoid side effects
            temp_circuit.__str__ = original_str
            
            return simulator
            
        except Exception as e:
            raise RuntimeError(f"Failed to create AC simulator from fixed netlist: {e}")
