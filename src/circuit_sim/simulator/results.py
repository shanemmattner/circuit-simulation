"""
Simulation results container.

Provides a clean interface to access simulation data.
"""

from typing import Dict, List, Optional, Union

import numpy as np


class SimulationResults:
    """Container for simulation results."""

    def __init__(self, analysis_type: str):
        """
        Initialize results container.

        Args:
            analysis_type: Type of analysis ("dc", "transient", "ac")
        """
        self.analysis_type = analysis_type
        self._time: Optional[np.ndarray] = None
        self._frequency: Optional[np.ndarray] = None
        self._node_voltages: Dict[Union[int, str], np.ndarray] = {}
        self._branch_currents: Dict[str, np.ndarray] = {}
        self._metadata: Dict[str, any] = {}

    def set_time_vector(self, time: np.ndarray):
        """Set the time vector for transient analysis."""
        self._time = np.array(time)

    def set_frequency_vector(self, frequency: np.ndarray):
        """Set the frequency vector for AC analysis."""
        self._frequency = np.array(frequency)

    def add_voltage(self, node: Union[int, str], voltage: Union[float, np.ndarray]):
        """
        Add voltage data for a node.

        Args:
            node: Node identifier
            voltage: Voltage value(s)
        """
        if isinstance(voltage, (int, float)):
            self._node_voltages[node] = np.array([voltage])
        else:
            self._node_voltages[node] = np.array(voltage)

    def add_current(self, component: str, current: Union[float, np.ndarray]):
        """
        Add current data for a component.

        Args:
            component: Component name
            current: Current value(s)
        """
        if isinstance(current, (int, float)):
            self._branch_currents[component] = np.array([current])
        else:
            self._branch_currents[component] = np.array(current)

    def add_metadata(self, key: str, value: any):
        """Add metadata about the simulation."""
        self._metadata[key] = value

    @property
    def time(self) -> Optional[np.ndarray]:
        """Get time vector for transient analysis."""
        return self._time

    @property
    def frequency(self) -> Optional[np.ndarray]:
        """Get frequency vector for AC analysis."""
        return self._frequency

    def voltage(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get voltage at a specific node.

        Args:
            node: Node identifier

        Returns:
            Voltage array or None if node not found
        """
        # Handle ground node
        if node == 0 or str(node).lower() == "gnd":
            # Ground is always 0V
            if self._time is not None:
                return np.zeros_like(self._time)
            elif self._frequency is not None:
                return np.zeros_like(self._frequency)
            else:
                return np.array([0.0])

        return self._node_voltages.get(node)

    def current(self, component: str) -> Optional[np.ndarray]:
        """
        Get current through a component.

        Args:
            component: Component name

        Returns:
            Current array or None if component not found
        """
        return self._branch_currents.get(component)

    @property
    def nodes(self) -> List[Union[int, str]]:
        """Get list of nodes with voltage data."""
        return list(self._node_voltages.keys())

    @property
    def components(self) -> List[str]:
        """Get list of components with current data."""
        return list(self._branch_currents.keys())

    def plot(self, *signals: str):
        """
        Plot simulation results.

        Args:
            signals: Signal names to plot (e.g., "V(2)", "I(R1)")
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError(
                "matplotlib is required for plotting. Install with: pip install matplotlib"
            )

        if not signals:
            # Default: plot all node voltages
            signals = [f"V({node})" for node in self.nodes if node != 0]

        fig, ax = plt.subplots()

        for signal in signals:
            if signal.upper().startswith("V("):
                # Voltage signal
                node = signal[2:-1]  # Extract node from "V(node)"
                try:
                    node = int(node)
                except ValueError:
                    pass  # Keep as string

                voltage = self.voltage(node)
                if voltage is not None:
                    if self.analysis_type == "transient" and self._time is not None:
                        ax.plot(self._time, voltage, label=signal)
                        ax.set_xlabel("Time (s)")
                    elif self.analysis_type == "ac" and self._frequency is not None:
                        ax.semilogx(self._frequency, 20 * np.log10(np.abs(voltage)), label=signal)
                        ax.set_xlabel("Frequency (Hz)")
                    else:
                        # DC or single point
                        ax.bar([signal], [voltage[0]], label=signal)
                        ax.set_xlabel("Node")

            elif signal.upper().startswith("I("):
                # Current signal
                component = signal[2:-1]  # Extract component from "I(component)"
                current = self.current(component)
                if current is not None:
                    if self.analysis_type == "transient" and self._time is not None:
                        ax.plot(self._time, current, label=signal)
                        ax.set_xlabel("Time (s)")
                    elif self.analysis_type == "ac" and self._frequency is not None:
                        ax.semilogx(self._frequency, 20 * np.log10(np.abs(current)), label=signal)
                        ax.set_xlabel("Frequency (Hz)")
                    else:
                        # DC or single point
                        ax.bar([signal], [current[0]], label=signal)
                        ax.set_xlabel("Component")

        # Set y-axis label
        if self.analysis_type == "ac":
            ax.set_ylabel("Magnitude (dB)")
        elif any(s.upper().startswith("V(") for s in signals):
            ax.set_ylabel("Voltage (V)")
        else:
            ax.set_ylabel("Current (A)")

        ax.set_title(f"{self.analysis_type.upper()} Analysis Results")
        ax.legend()
        ax.grid(True)

        plt.show()

    def __repr__(self) -> str:
        """String representation."""
        info = [f"SimulationResults(type={self.analysis_type}"]

        if self._node_voltages:
            info.append(f"nodes={len(self._node_voltages)}")

        if self._branch_currents:
            info.append(f"components={len(self._branch_currents)}")

        if self._time is not None:
            info.append(f"time_points={len(self._time)}")

        if self._frequency is not None:
            info.append(f"freq_points={len(self._frequency)}")

        return ", ".join(info) + ")"
