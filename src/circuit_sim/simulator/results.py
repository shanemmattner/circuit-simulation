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

    def magnitude(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get magnitude of complex voltage at a node.

        Args:
            node: Node identifier

        Returns:
            Magnitude array or None if node not found
        """
        voltage = self.voltage(node)
        if voltage is None:
            return None
        return np.abs(voltage)

    def magnitude_db(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get magnitude in dB of complex voltage at a node.

        Args:
            node: Node identifier

        Returns:
            Magnitude in dB array or None if node not found
        """
        magnitude = self.magnitude(node)
        if magnitude is None:
            return None
        # Avoid log of zero by using a minimum value
        magnitude_safe = np.maximum(magnitude, 1e-12)
        return 20 * np.log10(magnitude_safe)

    def phase_rad(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get phase in radians of complex voltage at a node.

        Args:
            node: Node identifier

        Returns:
            Phase in radians array or None if node not found
        """
        voltage = self.voltage(node)
        if voltage is None:
            return None
        return np.angle(voltage)

    def phase_deg(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get phase in degrees of complex voltage at a node.

        Args:
            node: Node identifier

        Returns:
            Phase in degrees array or None if node not found
        """
        phase_rad = self.phase_rad(node)
        if phase_rad is None:
            return None
        return np.degrees(phase_rad)

    @property
    def nodes(self) -> List[Union[int, str]]:
        """Get list of nodes with voltage data."""
        return list(self._node_voltages.keys())

    @property
    def components(self) -> List[str]:
        """Get list of components with current data."""
        return list(self._branch_currents.keys())

    def plot(self, *signals: str, save_to: Optional[str] = None, show: bool = True):
        """
        Plot simulation results.

        Args:
            signals: Signal names to plot (e.g., "V(2)", "I(R1)")
            save_to: Optional file path to save the plot
            show: Whether to display the plot (default True)
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

        if save_to:
            plt.savefig(save_to, dpi=150, bbox_inches="tight")

        if show:
            plt.show()

    def plot_bode(self, signal: str, title: str = "Bode Plot", show: bool = True):
        """
        Generate Bode plot (magnitude and phase vs frequency) for AC analysis.

        Args:
            signal: Signal to plot (e.g., "V(2)" for voltage at node 2)
            title: Plot title
            show: Whether to display the plot

        Returns:
            Dictionary with plot data for testing/export

        Raises:
            ValueError: If not AC analysis or signal not found
            ImportError: If matplotlib not available
        """
        if self.analysis_type != "ac":
            raise ValueError("Bode plots are only available for AC analysis")

        if self.frequency is None:
            raise ValueError("No frequency data available")

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError(
                "matplotlib is required for plotting. Install with: pip install matplotlib"
            )

        # Parse signal specification
        if signal.upper().startswith("V(") and signal.endswith(")"):
            # Voltage signal
            node = signal[2:-1]  # Extract node from "V(node)"
            try:
                node = int(node)
            except ValueError:
                pass

            voltage = self.voltage(node)
            if voltage is None:
                raise ValueError(f"Node {node} not found in results")

            # Calculate magnitude and phase
            magnitude_db = self.magnitude_db(node)
            phase_deg = self.phase_deg(node)

            if magnitude_db is None or phase_deg is None:
                raise ValueError(f"Cannot calculate magnitude/phase for node {node}")

        else:
            raise ValueError(f"Signal format '{signal}' not supported. Use V(node) format.")

        # Create Bode plot with two subplots
        fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(10, 8))

        # Magnitude plot
        ax_mag.semilogx(self.frequency, magnitude_db, 'b-', linewidth=2)
        ax_mag.set_ylabel('Magnitude (dB)')
        ax_mag.grid(True, which='both', alpha=0.3)
        ax_mag.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        ax_mag.axhline(y=-3, color='r', linestyle='--', alpha=0.5, label='-3dB')
        ax_mag.legend()

        # Phase plot
        ax_phase.semilogx(self.frequency, phase_deg, 'r-', linewidth=2)
        ax_phase.set_xlabel('Frequency (Hz)')
        ax_phase.set_ylabel('Phase (°)')
        ax_phase.grid(True, which='both', alpha=0.3)
        ax_phase.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        ax_phase.axhline(y=-45, color='r', linestyle='--', alpha=0.5, label='-45°')
        ax_phase.axhline(y=-90, color='r', linestyle='--', alpha=0.5, label='-90°')
        ax_phase.legend()

        plt.suptitle(title)
        plt.tight_layout()

        # Return plot data for testing
        plot_data = {
            "magnitude_db": magnitude_db,
            "phase_deg": phase_deg,
            "frequencies": self.frequency,
            "signal": signal,
            "title": title
        }

        if show:
            plt.show()

        return plot_data

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
