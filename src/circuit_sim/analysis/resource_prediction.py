"""
Resource prediction module for circuit simulation.

This module provides tools to estimate memory requirements and computation time
for circuit simulations based on circuit complexity and analysis type.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from ..circuit import Circuit


@dataclass
class ResourcePrediction:
    """Predicted resource requirements for circuit simulation.
    
    Attributes:
        estimated_time_seconds: Estimated simulation time in seconds
        estimated_memory_mb: Estimated peak memory usage in megabytes
        confidence: Confidence level ("high", "medium", or "low")
        factors: Dictionary of factors used in the prediction
    """

    estimated_time_seconds: float
    estimated_memory_mb: float
    confidence: str
    factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert prediction to dictionary."""
        return {
            "estimated_time_seconds": self.estimated_time_seconds,
            "estimated_memory_mb": self.estimated_memory_mb,
            "confidence": self.confidence,
            "factors": self.factors,
        }


class ResourcePredictor:
    """Predicts resource requirements for circuit simulation."""

    # Memory constants (in MB)
    BASE_MEMORY_MB: float = 1.0  # Base overhead
    NODE_MEMORY_MB: float = 0.01  # Memory per node (for matrix)
    COMPONENT_MEMORY_MB: float = 0.005  # Memory per component
    REACTIVE_MEMORY_MB: float = 0.02  # Additional memory per reactive element
    NONLINEAR_MEMORY_MB: float = 0.05  # Additional memory per nonlinear element

    # Time constants (in seconds)
    BASE_TIME_SECONDS: float = 0.1  # Base overhead
    NODE_TIME_SECONDS: float = 0.001  # Time per node
    COMPONENT_TIME_SECONDS: float = 0.0005  # Time per component
    ITERATION_OVERHEAD: float = 1.5  # Multiplier for iterative solvers

    # Analysis type multipliers
    ANALYSIS_MULTIPLIERS: Dict[str, Dict[str, float]] = {
        "dc": {"time": 1.0, "memory": 1.0},
        "transient": {"time": 2.0, "memory": 3.0},
        "ac": {"time": 1.5, "memory": 2.5},
    }

    def predict(
        self,
        circuit: Union[Circuit, Dict[str, Any]],
        simulation_type: str = "dc",
        stop_time: Optional[float] = None,
        timestep: Optional[float] = None,
    ) -> ResourcePrediction:
        """Predict resource requirements for a circuit simulation.
        
        Args:
            circuit: Circuit to analyze (Circuit object or dict with component info)
            simulation_type: Type of analysis ("dc", "transient", or "ac")
            stop_time: Simulation stop time (for transient analysis)
            timestep: Simulation timestep (for transient analysis)
            
        Returns:
            ResourcePrediction with estimated time and memory
            
        Raises:
            ValueError: If simulation_type is invalid or parameters are invalid
        """
        # Validate simulation type
        valid_types = ["dc", "transient", "ac"]
        if simulation_type not in valid_types:
            raise ValueError(
                f"Invalid simulation_type: {simulation_type}. "
                f"Must be one of {valid_types}"
            )

        # Validate transient parameters
        if simulation_type == "transient":
            if stop_time is not None and stop_time <= 0:
                raise ValueError("stop_time must be positive")
            if timestep is not None and timestep <= 0:
                raise ValueError("timestep must be positive")

        # Extract circuit metrics
        if isinstance(circuit, Circuit):
            metrics = self._extract_metrics(circuit)
        else:
            metrics = circuit

        num_nodes = metrics.get("num_nodes", 1)
        num_components = metrics.get("num_components", 0)
        num_reactive = metrics.get("num_reactive", 0)
        num_nonlinear = metrics.get("num_nonlinear", 0)
        has_feedback = metrics.get("has_feedback", False)

        # Calculate base memory
        memory = self.BASE_MEMORY_MB
        memory += num_nodes * self.NODE_MEMORY_MB
        memory += num_components * self.COMPONENT_MEMORY_MB
        memory += num_reactive * self.REACTIVE_MEMORY_MB
        memory += num_nonlinear * self.NONLINEAR_MEMORY_MB

        # Apply simulation type multiplier
        memory_multiplier = self.ANALYSIS_MULTIPLIERS[simulation_type]["memory"]

        # Additional memory for transient (time points)
        if simulation_type == "transient" and stop_time is not None and timestep:
            num_points = int(stop_time / timestep) + 1
            # Memory for storing time-domain results
            memory += (num_points * num_nodes * 8) / (1024 * 1024)  # 8 bytes per float

        # Additional memory for AC (complex numbers)
        if simulation_type == "ac" and stop_time is not None:
            # Estimate frequency points
            import math
            num_freq = max(10, int(math.log10(stop_time) * 10) + 1) if stop_time > 0 else 10
            memory += (num_freq * num_nodes * 16) / (1024 * 1024)  # 16 bytes per complex

        memory *= memory_multiplier

        # Calculate base time
        time = self.BASE_TIME_SECONDS
        time += num_nodes * self.NODE_TIME_SECONDS
        time += num_components * self.COMPONENT_TIME_SECONDS

        # Feedback loops require more iterations
        if has_feedback:
            time *= self.ITERATION_OVERHEAD

        # Nonlinear elements require more computation
        if num_nonlinear > 0:
            time *= (1 + num_nonlinear * 0.5)

        # Apply simulation type multiplier
        time_multiplier = self.ANALYSIS_MULTIPLIERS[simulation_type]["time"]
        time *= time_multiplier

        # Transient simulation time scales with number of time points
        if simulation_type == "transient" and stop_time is not None and timestep:
            num_points = int(stop_time / timestep) + 1
            time *= (1 + num_points / 1000)

        # Determine confidence level
        confidence = self._determine_confidence(
            num_nodes=num_nodes,
            num_components=num_components,
            num_nonlinear=num_nonlinear,
            simulation_type=simulation_type,
        )

        # Build factors dictionary
        factors = {
            "num_nodes": float(num_nodes),
            "num_components": float(num_components),
            "num_reactive": float(num_reactive),
            "num_nonlinear": float(num_nonlinear),
            "simulation_type": simulation_type,
            "has_feedback": float(has_feedback),
        }

        return ResourcePrediction(
            estimated_time_seconds=time,
            estimated_memory_mb=memory,
            confidence=confidence,
            factors=factors,
        )

    def _extract_metrics(self, circuit: Circuit) -> Dict[str, Any]:
        """Extract metrics from a Circuit object."""
        num_nodes = len(circuit.nodes)
        num_components = len(circuit.components)

        # Count component types
        num_reactive = 0
        num_nonlinear = 0

        for comp in circuit.components:
            comp_type = comp.get("type", "")
            if comp_type in ("capacitor", "inductor"):
                num_reactive += 1
            if comp_type in ("diode", "bjt_transistor", "mosfet", "led", "zener"):
                num_nonlinear += 1

        # Check for feedback (simplified - check if any node connects back to earlier nodes)
        has_feedback = self._detect_feedback(circuit)

        return {
            "num_nodes": num_nodes,
            "num_components": num_components,
            "num_reactive": num_reactive,
            "num_nonlinear": num_nonlinear,
            "has_feedback": has_feedback,
        }

    def _detect_feedback(self, circuit: Circuit) -> bool:
        """Detect if circuit has feedback loops (simplified detection)."""
        # Simple heuristic: if circuit has more complex connectivity
        # For now, check if there are multiple paths between nodes
        # This is a simplified version
        if len(circuit.components) < 3:
            return False

        # More components = higher chance of feedback
        # But this is a rough heuristic
        return len(circuit.components) > 10

    def _determine_confidence(
        self,
        num_nodes: int,
        num_components: int,
        num_nonlinear: int,
        simulation_type: str,
    ) -> str:
        """Determine confidence level based on circuit complexity."""
        # Simple circuits have high confidence
        if num_nodes <= 10 and num_components <= 20 and num_nonlinear == 0:
            return "high"

        # Medium complexity
        if num_nodes <= 50 and num_components <= 100 and num_nonlinear <= 5:
            return "medium"

        # High complexity or nonlinear elements
        return "low"


def predict_simulation_resources(
    circuit: Circuit,
    simulation_type: str = "dc",
    stop_time: Optional[float] = None,
    timestep: Optional[float] = None,
) -> ResourcePrediction:
    """Convenience function to predict simulation resources.
    
    Args:
        circuit: Circuit to analyze
        simulation_type: Type of analysis ("dc", "transient", or "ac")
        stop_time: Simulation stop time (for transient analysis)
        timestep: Simulation timestep (for transient analysis)
        
    Returns:
        ResourcePrediction with estimated time and memory
    """
    predictor = ResourcePredictor()
    return predictor.predict(
        circuit=circuit,
        simulation_type=simulation_type,
        stop_time=stop_time,
        timestep=timestep,
    )
