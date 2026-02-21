"""
Simulation time prediction module.

This module provides functionality to estimate simulation runtime
based on circuit complexity metrics and simulation parameters.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from .complexity import CircuitComplexityMetrics, ComplexityScore


class AnalysisType(Enum):
    """Types of circuit analysis that can be performed."""

    DC = "dc"
    TRANSIENT = "transient"
    AC = "ac"
    OPERATING_POINT = "operating_point"


@dataclass
class SimulationParameters:
    """Parameters for a simulation that affect runtime.

    Attributes:
        analysis_type: Type of analysis to perform
        stop_time: End time for transient simulation (seconds)
        step_time: Time step for simulation (seconds)
        start_time: Start time for simulation (seconds), default 0
        max_time_step: Maximum internal time step (seconds)
        temperature: Simulation temperature in Celsius
        nominal_temperature: Nominal temperature in Celsius
    """

    analysis_type: AnalysisType
    stop_time: Optional[float] = None
    step_time: Optional[float] = None
    start_time: float = 0.0
    max_time_step: Optional[float] = None
    temperature: float = 25.0
    nominal_temperature: float = 25.0

    @classmethod
    def dc(cls) -> "SimulationParameters":
        """Create DC analysis parameters."""
        return cls(analysis_type=AnalysisType.DC)

    @classmethod
    def transient(
        cls,
        stop_time: float,
        step_time: Optional[float] = None,
        start_time: float = 0.0,
    ) -> "SimulationParameters":
        """Create transient analysis parameters.

        Args:
            stop_time: End time for simulation (seconds)
            step_time: Time step for output (seconds), defaults to stop_time/1000
            start_time: Start time for simulation (seconds)

        Returns:
            SimulationParameters for transient analysis
        """
        return cls(
            analysis_type=AnalysisType.TRANSIENT,
            stop_time=stop_time,
            step_time=step_time,
            start_time=start_time,
        )

    @classmethod
    def ac(
        cls,
        start_frequency: float,
        stop_frequency: float,
        points_per_decade: int = 10,
    ) -> "SimulationParameters":
        """Create AC analysis parameters.

        Args:
            start_frequency: Starting frequency (Hz)
            stop_frequency: Ending frequency (Hz)
            points_per_decade: Number of points per decade

        Returns:
            SimulationParameters for AC analysis
        """
        return cls(
            analysis_type=AnalysisType.AC,
            stop_time=stop_frequency,  # Use frequency as stop_time equivalent
            step_time=float(points_per_decade),  # Store points per decade
        )


@dataclass
class SimulationTimePrediction:
    """Prediction of simulation runtime.

    Attributes:
        estimated_seconds: Estimated runtime in seconds
        confidence: Confidence level of the prediction (0-1)
        time_steps: Estimated number of time steps
        matrix_solves: Estimated number of matrix solves required
        breakdown: Detailed breakdown of time estimates
    """

    estimated_seconds: float
    confidence: float = 0.8
    time_steps: int = 0
    matrix_solves: int = 0
    breakdown: dict = None

    def __post_init__(self) -> None:
        """Initialize mutable fields."""
        if self.breakdown is None:
            self.breakdown = {}

    @property
    def estimated_milliseconds(self) -> float:
        """Get estimated runtime in milliseconds."""
        return self.estimated_seconds * 1000

    @property
    def estimated_minutes(self) -> float:
        """Get estimated runtime in minutes."""
        return self.estimated_seconds / 60.0

    def __str__(self) -> str:
        """String representation of the prediction."""
        if self.estimated_seconds < 1:
            time_str = f"{self.estimated_milliseconds:.1f}ms"
        elif self.estimated_seconds < 60:
            time_str = f"{self.estimated_seconds:.2f}s"
        else:
            time_str = f"{self.estimated_minutes:.2f}min"

        return (
            f"SimulationTimePrediction(\n"
            f"  estimated_time={time_str},\n"
            f"  confidence={self.confidence:.0%},\n"
            f"  time_steps={self.time_steps},\n"
            f"  matrix_solves={self.matrix_solves}\n"
            f")"
        )


class SimulationTimePredictor:
    """Predicts simulation runtime based on circuit complexity and parameters.

    This class uses circuit complexity metrics and simulation parameters
    to estimate how long a simulation will take to run.
    """

    # Base time constants (in seconds)
    BASE_TIME_DC: float = 0.01  # Base time for DC analysis per node
    BASE_TIME_TRANSIENT: float = 0.001  # Base time per time step
    BASE_TIME_AC: float = 0.005  # Base time per frequency point

    # Complexity multipliers
    NODE_MULTIPLIER: float = 0.001  # Time per node
    COMPONENT_MULTIPLIER: float = 0.0005  # Time per component
    REACTIVE_MULTIPLIER: float = 0.002  # Time per reactive element
    NONLINEAR_MULTIPLIER: float = 0.01  # Time per nonlinear element (Newton-Raphson iterations)

    # Time step factors
    TRANSIENT_STEP_FACTOR: float = 1000  # Default steps per simulation duration

    def __init__(self) -> None:
        """Initialize the predictor with default constants."""
        pass

    def predict(
        self,
        complexity: Union[CircuitComplexityMetrics, ComplexityScore],
        params: SimulationParameters,
    ) -> SimulationTimePrediction:
        """Predict simulation runtime.

        Args:
            complexity: Circuit complexity metrics or score
            params: Simulation parameters

        Returns:
            SimulationTimePrediction with estimated runtime

        Raises:
            ValueError: If parameters are invalid for the analysis type
        """
        # Extract metrics from complexity
        if isinstance(complexity, CircuitComplexityMetrics):
            metrics = complexity.topology
            score = complexity.overall_score
        else:
            metrics = None
            score = complexity

        # Validate parameters
        if params.analysis_type == AnalysisType.TRANSIENT:
            if params.stop_time is None or params.stop_time <= 0:
                raise ValueError("stop_time is required for transient analysis")
            if params.start_time >= params.stop_time:
                raise ValueError("start_time must be less than stop_time")

        # Calculate based on analysis type
        if params.analysis_type in (AnalysisType.DC, AnalysisType.OPERATING_POINT):
            return self._predict_dc(metrics, score)
        elif params.analysis_type == AnalysisType.TRANSIENT:
            return self._predict_transient(metrics, score, params)
        elif params.analysis_type == AnalysisType.AC:
            return self._predict_ac(metrics, score, params)
        else:
            raise ValueError(f"Unknown analysis type: {params.analysis_type}")

    def _predict_dc(
        self,
        metrics: Optional,  # Can be None if only ComplexityScore provided
        score: Optional[ComplexityScore],
    ) -> SimulationTimePrediction:
        """Predict DC analysis runtime.

        Args:
            metrics: Topology metrics (may be None)
            score: Complexity score

        Returns:
            Prediction for DC analysis
        """
        # Extract values safely
        node_count = score.node_count if score else 0
        component_count = score.component_count if score else 0
        reactive_count = score.reactive_element_count if score else 0

        # Count nonlinear from metrics if available
        nonlinear_count = 0
        if metrics:
            nonlinear_count = metrics.nonlinear_count

        # Calculate base time
        base_time = self.BASE_TIME_DC

        # Calculate multipliers
        node_time = node_count * self.NODE_MULTIPLIER
        component_time = component_count * self.COMPONENT_MULTIPLIER
        reactive_time = reactive_count * self.REACTIVE_MULTIPLIER
        nonlinear_time = nonlinear_count * self.NONLINEAR_MULTIPLIER * 10  # Newton-Raphson iterations

        # Total estimated time
        estimated_seconds = base_time + node_time + component_time + reactive_time + nonlinear_time

        # DC is typically fast - set a minimum
        estimated_seconds = max(estimated_seconds, 0.001)  # 1ms minimum

        breakdown = {
            "base_time": base_time,
            "node_time": node_time,
            "component_time": component_time,
            "reactive_time": reactive_time,
            "nonlinear_time": nonlinear_time,
        }

        # Estimate matrix solves (DC uses ~3-10 iterations typically)
        matrix_solves = max(3, node_count // 2)

        return SimulationTimePrediction(
            estimated_seconds=estimated_seconds,
            confidence=0.85,
            time_steps=1,
            matrix_solves=matrix_solves,
            breakdown=breakdown,
        )

    def _predict_transient(
        self,
        metrics: Optional,
        score: Optional[ComplexityScore],
        params: SimulationParameters,
    ) -> SimulationTimePrediction:
        """Predict transient analysis runtime.

        Args:
            metrics: Topology metrics
            score: Complexity score
            params: Transient simulation parameters

        Returns:
            Prediction for transient analysis
        """
        # Extract values
        node_count = score.node_count if score else 0
        component_count = score.component_count if score else 0
        reactive_count = score.reactive_element_count if score else 0

        nonlinear_count = 0
        if metrics:
            nonlinear_count = metrics.nonlinear_count

        # Calculate time steps
        duration = params.stop_time - params.start_time
        if params.step_time:
            time_steps = max(1, int(duration / params.step_time))
        else:
            # Default: 1000 steps or based on duration
            time_steps = max(1, int(duration * self.TRANSIENT_STEP_FACTOR))

        # Adjust for max_time_step if specified
        if params.max_time_step:
            max_steps = int(duration / params.max_time_step)
            time_steps = max(time_steps, max_steps)

        # Calculate base time per time step
        base_time_per_step = self.BASE_TIME_TRANSIENT

        # Calculate time per step with complexity factors
        node_factor = 1 + (node_count * 0.01)  # 1% per node
        component_factor = 1 + (component_count * 0.005)  # 0.5% per component
        reactive_factor = 1 + (reactive_count * 0.02)  # 2% per reactive element
        nonlinear_factor = 1 + (nonlinear_count * 0.1)  # 10% per nonlinear element

        # Combined factor
        complexity_factor = (
            node_factor * component_factor * reactive_factor * nonlinear_factor
        )

        # Total estimated time
        time_per_step = base_time_per_step * complexity_factor
        estimated_seconds = time_steps * time_per_step

        breakdown = {
            "time_steps": time_steps,
            "base_time_per_step": base_time_per_step,
            "node_factor": node_factor,
            "component_factor": component_factor,
            "reactive_factor": reactive_factor,
            "nonlinear_factor": nonlinear_factor,
            "complexity_factor": complexity_factor,
            "time_per_step": time_per_step,
        }

        # Transient has lower confidence due to variable convergence
        confidence = 0.75

        # Adjust confidence based on circuit complexity
        if score and score.weighted_score > 50:
            confidence = 0.6  # Lower confidence for very complex circuits
        elif score and score.weighted_score < 10:
            confidence = 0.9  # Higher confidence for simple circuits

        return SimulationTimePrediction(
            estimated_seconds=estimated_seconds,
            confidence=confidence,
            time_steps=time_steps,
            matrix_solves=time_steps * max(5, node_count),  # More iterations for transient
            breakdown=breakdown,
        )

    def _predict_ac(
        self,
        metrics: Optional,
        score: Optional[ComplexityScore],
        params: SimulationParameters,
    ) -> SimulationTimePrediction:
        """Predict AC (frequency) analysis runtime.

        Args:
            metrics: Topology metrics
            score: Complexity score
            params: AC simulation parameters

        Returns:
            Prediction for AC analysis
        """
        # Extract values
        node_count = score.node_count if score else 0
        component_count = score.component_count if score else 0
        reactive_count = score.reactive_element_count if score else 0

        # Calculate frequency points
        start_freq = params.start_time  # Reusing start_time for start frequency
        stop_freq = params.stop_time  # Reusing stop_time for stop frequency
        points_per_step = params.step_time or 10  # Default 10 points per decade

        if stop_freq and start_freq and stop_freq > start_freq:
            # Calculate decades
            decades = stop_freq / start_freq if start_freq > 0 else 1
            frequency_points = int(decades * points_per_step)
        else:
            frequency_points = 100  # Default

        frequency_points = max(frequency_points, 1)

        # Base time per frequency point
        base_time_per_point = self.BASE_TIME_AC

        # Calculate complexity factors (similar to transient)
        node_factor = 1 + (node_count * 0.01)
        component_factor = 1 + (component_count * 0.005)
        reactive_factor = 1 + (reactive_count * 0.01)  # Reactive elements affect AC more

        complexity_factor = node_factor * component_factor * reactive_factor

        # Total estimated time
        time_per_point = base_time_per_point * complexity_factor
        estimated_seconds = frequency_points * time_per_point

        breakdown = {
            "frequency_points": frequency_points,
            "base_time_per_point": base_time_per_point,
            "node_factor": node_factor,
            "component_factor": component_factor,
            "reactive_factor": reactive_factor,
            "complexity_factor": complexity_factor,
            "time_per_point": time_per_point,
        }

        return SimulationTimePrediction(
            estimated_seconds=estimated_seconds,
            confidence=0.8,
            time_steps=frequency_points,
            matrix_solves=frequency_points * max(2, node_count // 4),
            breakdown=breakdown,
        )


def predict_simulation_time(
    complexity: Union[CircuitComplexityMetrics, ComplexityScore],
    analysis_type: Union[str, AnalysisType],
    stop_time: Optional[float] = None,
    step_time: Optional[float] = None,
    **kwargs,
) -> SimulationTimePrediction:
    """Convenience function to predict simulation time.

    Args:
        complexity: Circuit complexity metrics or score
        analysis_type: Type of analysis ("dc", "transient", "ac")
        stop_time: End time for transient simulation (seconds)
        step_time: Time step for simulation (seconds)
        **kwargs: Additional parameters passed to SimulationParameters

    Returns:
        SimulationTimePrediction with estimated runtime

    Example:
        >>> from circuit_sim.analysis import predict_simulation_time, ComplexityScore
        >>> score = ComplexityScore(node_count=5, component_count=10, reactive_element_count=2)
        >>> score.calculate_score()
        >>> prediction = predict_simulation_time(score, "transient", stop_time=0.01, step_time=1e-6)
        >>> print(f"Estimated time: {prediction.estimated_milliseconds:.1f}ms")
    """
    # Convert string to enum if needed
    if isinstance(analysis_type, str):
        analysis_type = AnalysisType(analysis_type.lower())

    # Create parameters based on analysis type
    if analysis_type == AnalysisType.DC:
        params = SimulationParameters.dc()
    elif analysis_type == AnalysisType.TRANSIENT:
        params = SimulationParameters.transient(
            stop_time=stop_time,
            step_time=step_time,
            start_time=kwargs.get("start_time", 0.0),
        )
    elif analysis_type == AnalysisType.AC:
        params = SimulationParameters.ac(
            start_frequency=kwargs.get("start_frequency", 1),
            stop_frequency=kwargs.get("stop_frequency", stop_time or 1e6),
            points_per_decade=kwargs.get("points_per_decade", 10),
        )
    else:
        params = SimulationParameters(analysis_type=analysis_type)

    # Create predictor and predict
    predictor = SimulationTimePredictor()
    return predictor.predict(complexity, params)
