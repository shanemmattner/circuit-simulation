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
]
