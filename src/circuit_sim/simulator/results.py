"""
Simulation results container.

Provides a clean interface to access simulation data.
"""

from typing import Dict, List, Optional, Union, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..analysis import TransferFunction


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

    def get_voltage(self, node: Union[int, str]) -> Optional[np.ndarray]:
        """
        Get voltage at a specific node (alias for voltage() method).
        
        This method provides compatibility with test frameworks that expect
        get_voltage() method name.

        Args:
            node: Node identifier

        Returns:
            Voltage array or None if node not found
        """
        return self.voltage(node)
    
    def get_frequency_vector(self) -> Optional[np.ndarray]:
        """
        Get frequency vector for AC analysis (alias for frequency property).
        
        This method provides compatibility with test frameworks that expect
        get_frequency_vector() method name.

        Returns:
            Frequency array or None if not available
        """
        return self.frequency

    @property
    def nodes(self) -> List[Union[int, str]]:
        """Get list of nodes with voltage data."""
        return list(self._node_voltages.keys())

    @property
    def components(self) -> List[str]:
        """Get list of components with current data."""
        return list(self._branch_currents.keys())

    @property
    def voltages(self) -> Dict[Union[int, str], np.ndarray]:
        """Get all node voltage data."""
        return self._node_voltages

    @property
    def currents(self) -> Dict[str, np.ndarray]:
        """Get all component current data."""
        return self._branch_currents

    @property
    def metadata(self) -> Dict[str, any]:
        """Get simulation metadata."""
        return self._metadata

    def analyze_power(self, circuit, component_ratings: Optional[Dict[str, float]] = None):
        """
        Analyze power dissipation in the circuit.
        
        Args:
            circuit: Circuit object used for simulation
            component_ratings: Optional component power ratings
            
        Returns:
            PowerAnalysisResult with power information
            
        Raises:
            ImportError: If validation module not available
            NotImplementedError: If not DC analysis
        """
        try:
            from ..validation import PowerAnalyzer
        except ImportError:
            raise ImportError("Power analysis requires validation module")
            
        analyzer = PowerAnalyzer()
        return analyzer.analyze_power(circuit, self, component_ratings)
        
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
    
    def to_transfer_function(
        self,
        input_node: Union[int, str],
        output_node: Union[int, str],
        reference: Union[int, str] = 0
    ) -> "TransferFunction":
        """
        Extract transfer function from AC analysis results.
        
        Args:
            input_node: Input node identifier
            output_node: Output node identifier
            reference: Reference node (default: ground/0)
            
        Returns:
            TransferFunction object H(s) = Vout/Vin
            
        Raises:
            ValueError: If not AC analysis or nodes not found
        """
        if self.analysis_type != "ac":
            raise ValueError("Transfer function extraction requires AC analysis results")
        
        if self._frequency is None:
            raise ValueError("No frequency data available")
        
        # Get voltages
        vin = self.voltage(input_node)
        vout = self.voltage(output_node)
        
        if vin is None:
            raise ValueError(f"Input node '{input_node}' not found in results")
        if vout is None:
            raise ValueError(f"Output node '{output_node}' not found in results")
        
        # Handle reference node if not ground
        if reference != 0:
            vref = self.voltage(reference)
            if vref is not None:
                vin = vin - vref
                vout = vout - vref
        
        # Calculate transfer function H(jω) = Vout/Vin
        with np.errstate(divide='ignore', invalid='ignore'):
            h_jw = vout / vin
        
        # Check for valid transfer function data
        if np.all(h_jw == 0):
            raise ValueError("Transfer function is identically zero - check circuit connectivity")
        
        if np.any(np.isnan(h_jw)) or np.any(np.isinf(h_jw)):
            raise ValueError(
                "Invalid transfer function data: simulation may have failed or "
                "circuit may have connectivity issues. Check AC analysis setup."
            )
        
        # Convert frequency from Hz to rad/s
        omega = 2 * np.pi * self._frequency
        
        # Create transfer function from frequency response
        from ..analysis import TransferFunction
        return TransferFunction.from_frequency_response(omega, h_jw)
