"""
Circuit analysis module for transfer functions and stability analysis.
"""

from .transfer_function import TransferFunction
from .stability import StabilityMetrics, calculate_stability_margins
from .time_domain import (
    step_response,
    impulse_response,
    calculate_rise_time,
    calculate_settling_time,
    calculate_overshoot,
)
from .resource_prediction import (
    ResourcePrediction,
    ResourcePredictor,
    predict_simulation_resources,
)
from .time_prediction import (
    AnalysisType,
    SimulationParameters,
    SimulationTimePrediction,
    SimulationTimePredictor,
    predict_simulation_time,
)
from .complexity import (
    ComponentType,
    ReactiveType,
    TopologyType,
    NodeMetrics,
    ComponentMetrics,
    TopologyMetrics,
    ComplexityScore,
    CircuitComplexityMetrics,
    ComponentCounts,
    SourceComplexity,
)
from .solver_settings import (
    SolverType,
    TimestepStrategy,
    SolverSettings,
    recommend_solver_type,
    recommend_timestep_settings,
    recommend_convergence_tolerances,
    recommend_iteration_limits,
    suggest_solver_settings,
)

__all__ = [
    "TransferFunction",
    "StabilityMetrics",
    "calculate_stability_margins",
    "step_response",
    "impulse_response",
    "calculate_rise_time",
    "calculate_settling_time",
    "calculate_overshoot",
    "ResourcePrediction",
    "ResourcePredictor",
    "predict_simulation_resources",
    "AnalysisType",
    "SimulationParameters",
    "SimulationTimePrediction",
    "SimulationTimePredictor",
    "predict_simulation_time",
    "ComponentType",
    "ReactiveType",
    "TopologyType",
    "NodeMetrics",
    "ComponentMetrics",
    "TopologyMetrics",
    "ComplexityScore",
    "CircuitComplexityMetrics",
    "ComponentCounts",
    "SourceComplexity",
    "SolverType",
    "TimestepStrategy",
    "SolverSettings",
    "recommend_solver_type",
    "recommend_timestep_settings",
    "recommend_convergence_tolerances",
    "recommend_iteration_limits",
    "suggest_solver_settings",
]
