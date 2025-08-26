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
        raise NotImplementedError("AC analysis will be implemented in Phase 2")
