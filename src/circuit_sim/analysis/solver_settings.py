"""
Solver settings suggestion module.

This module provides logic to recommend appropriate solver types (direct/iterative),
timestep settings, and convergence tolerances based on circuit complexity score
and circuit characteristics.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from .complexity import CircuitComplexityMetrics


class SolverType(Enum):
    """Types of solvers available for circuit simulation."""

    DIRECT = "direct"  # Direct LU decomposition solver
    ITERATIVE = "iterative"  # Iterative solver (GMRES, etc.)


class TimestepStrategy(Enum):
    """Strategy for determining timestep size."""

    FIXED = "fixed"  # Fixed timestep
    ADAPTIVE = "adaptive"  # Adaptive timestep based on circuit behavior


@dataclass
class SolverSettings:
    """
    Recommended solver settings for a circuit.

    Attributes:
        solver_type: Recommended solver type (direct or iterative)
        timestep_strategy: Recommended timestep strategy
        step_time: Recommended output time step in seconds
        max_time_step: Recommended maximum internal timestep in seconds
        reltol: Relative tolerance for convergence (default ngspice: 1e-3)
        abstol: Absolute tolerance for convergence (default ngspice: 1e-12)
        vntol: Voltage tolerance for convergence (default ngspice: 1e-6)
        itl1: DC iteration limit (default: 100)
        itl2: DC transfer curve iteration limit (default: 50)
        itl4: Transient analysis iteration limit (default: 100)
        num_src_steps: Number of source steps for DC (default: 64)
        num_dst_levels: Number of destination steps (default: 8)
        description: Human-readable description of recommendations
    """

    solver_type: SolverType = SolverType.DIRECT
    timestep_strategy: TimestepStrategy = TimestepStrategy.ADAPTIVE
    step_time: float = 1e-6
    max_time_step: Optional[float] = None
    reltol: float = 1e-3
    abstol: float = 1e-12
    vntol: float = 1e-6
    itl1: int = 100
    itl2: int = 50
    itl4: int = 100
    num_src_steps: int = 64
    num_dst_levels: int = 8
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "solver_type": self.solver_type.value,
            "timestep_strategy": self.timestep_strategy.value,
            "step_time": self.step_time,
            "max_time_step": self.max_time_step,
            "reltol": self.reltol,
            "abstol": self.abstol,
            "vntol": self.vntol,
            "itl1": self.itl1,
            "itl2": self.itl2,
            "itl4": self.itl4,
            "num_src_steps": self.num_src_steps,
            "num_dst_levels": self.num_dst_levels,
            "description": self.description,
        }


def recommend_solver_type(metrics: CircuitComplexityMetrics) -> SolverType:
    """
    Recommend solver type based on circuit complexity.

    Direct solvers are generally faster for smaller circuits and those with
    dense matrices. Iterative solvers can be more efficient for larger
    circuits with sparse matrices.

    Args:
        metrics: Circuit complexity metrics

    Returns:
        Recommended solver type
    """
    score = metrics.overall_complexity_score
    num_nodes = metrics.topology.node_count
    num_components = metrics.component_counts.total_components
    has_nonlinear = metrics.has_nonlinear_elements
    has_coupling = metrics.topology.has_coupling
    has_dependent = metrics.source_complexity.num_dependent_sources > 0

    # Decision logic for solver selection
    # Direct solvers are preferred for:
    # - Simple circuits
    # - Circuits without coupling elements
    # - Linear circuits

    # Iterative solvers are preferred for:
    # - Complex circuits with many nodes
    # - Circuits with coupling (transformers, dependent sources)
    # - Very large circuits

    # Base decision on complexity score
    if score < 15:
        # Simple circuits: direct solver
        return SolverType.DIRECT
    elif score < 50:
        # Moderate complexity: check specific factors
        if has_coupling or has_dependent:
            # Coupled/dependent elements can benefit from iterative
            return SolverType.ITERATIVE
        return SolverType.DIRECT
    elif score < 100:
        # Complex circuits: check for challenging elements
        # Coupling or dependent sources push towards iterative
        if has_coupling or has_dependent or num_nodes > 40:
            return SolverType.ITERATIVE
        return SolverType.DIRECT
    else:
        # Very complex: iterative solver
        return SolverType.ITERATIVE


def recommend_timestep_settings(
    metrics: CircuitComplexityMetrics,
    stop_time: Optional[float] = None,
) -> Tuple[float, Optional[float], TimestepStrategy]:
    """
    Recommend timestep settings based on circuit characteristics.

    Args:
        metrics: Circuit complexity metrics
        stop_time: Simulation stop time (optional, for calculating step count)

    Returns:
        Tuple of (step_time, max_time_step, strategy)
    """
    # Determine if adaptive timestep is needed
    has_high_freq = metrics.source_complexity.max_frequency_components > 0
    has_pulse = metrics.source_complexity.num_pulse_sources > 0
    has_switches = metrics.component_counts.switches > 0
    has_transistors = (
        metrics.component_counts.mosfets > 0
        or metrics.component_counts.bjt_transistors > 0
    )
    is_nonlinear = metrics.has_nonlinear_elements

    # Adaptive timestep is recommended for:
    # - Circuits with high frequency components
    # - Circuits with pulse sources (sharp edges)
    # - Circuits with switches (discontinuous behavior)
    # - Circuits with transistors (nonlinear behavior)
    # - Circuits with nonlinear elements

    needs_adaptive = (
        has_high_freq
        or has_pulse
        or has_switches
        or has_transistors
        or is_nonlinear
        or metrics.topology.has_feedback_loops
    )

    if needs_adaptive:
        strategy = TimestepStrategy.ADAPTIVE
    else:
        strategy = TimestepStrategy.FIXED

    # Determine appropriate step time based on circuit characteristics
    # Look at frequency content and component values

    # For simple RC circuits: step based on RC time constant
    has_rc_only = (
        metrics.component_counts.resistors > 0
        and metrics.component_counts.capacitors > 0
        and metrics.component_counts.inductors == 0
        and metrics.component_counts.total_semiconductors == 0
    )

    # For RLC circuits: consider resonant frequency
    has_rlc = (
        metrics.component_counts.resistors > 0
        and metrics.component_counts.capacitors > 0
        and metrics.component_counts.inductors > 0
    )

    # Base step time calculation
    # Default: use 1000 points per simulation (adjustable)
    if stop_time is not None and stop_time > 0:
        step_time = stop_time / 1000
    else:
        # Default to 1 microsecond if no stop time given
        step_time = 1e-6

    # Adjust based on circuit type
    if has_rc_only:
        # For RC circuits, ensure at least 10 points per RC time constant
        # Assume typical R=1k, C=1u -> RC = 1ms
        step_time = min(step_time, 1e-4)  # At least 10 points
    elif has_rlc:
        # For RLC, need to capture resonance
        # Assume resonant freq around 1/(2*pi*sqrt(LC))
        # Use smaller timestep
        step_time = min(step_time, 1e-5)
    elif has_pulse or has_switches:
        # Need fine resolution for sharp edges
        step_time = min(step_time, stop_time / 10000 if stop_time else 1e-9)
    elif has_transistors or is_nonlinear:
        # Nonlinear circuits need finer resolution
        step_time = min(step_time, 1e-7)

    # For adaptive strategy, recommend max_time_step
    if strategy == TimestepStrategy.ADAPTIVE:
        # max_time_step is typically 2-10x the output step_time
        max_time_step = step_time * 5
    else:
        max_time_step = None

    return step_time, max_time_step, strategy


def recommend_convergence_tolerances(
    metrics: CircuitComplexityMetrics,
) -> Tuple[float, float, float]:
    """
    Recommend convergence tolerances based on circuit complexity.

    For more complex or sensitive circuits, tighter tolerances may be needed.
    For simpler circuits, looser tolerances can speed up simulation.

    Args:
        metrics: Circuit complexity metrics

    Returns:
        Tuple of (reltol, abstol, vntol)
    """
    score = metrics.overall_complexity_score
    has_nonlinear = metrics.has_nonlinear_elements
    has_dependent = metrics.source_complexity.num_dependent_sources > 0
    has_switches = metrics.component_counts.switches > 0

    # Base tolerances (ngspice defaults)
    reltol = 1e-3
    abstol = 1e-12
    vntol = 1e-6

    # Adjust based on circuit complexity
    if score < 10:
        # Simple circuits: can use looser tolerances for speed
        reltol = 1e-2
    elif score < 30:
        # Moderate circuits: use defaults
        reltol = 1e-3
    elif score < 60:
        # Complex circuits: tighter tolerances
        reltol = 1e-4
    else:
        # Very complex: even tighter
        reltol = 1e-5

    # Additional adjustments for challenging elements
    if has_nonlinear:
        # Nonlinear elements need tighter tolerances
        # Make it strictly tighter than default
        reltol = min(reltol, 5e-4)
        abstol = min(abstol, 1e-14)  # Tighter current tolerance
        vntol = min(vntol, 1e-8)  # Tighter voltage tolerance

    if has_dependent:
        # Dependent sources can cause convergence issues
        reltol = min(reltol, 5e-4)

    if has_switches:
        # Switches cause discontinuities
        reltol = min(reltol, 5e-4)
        vntol = min(vntol, 1e-7)

    return reltol, abstol, vntol


def recommend_iteration_limits(
    metrics: CircuitComplexityMetrics,
) -> dict:
    """
    Recommend iteration limits for convergence.

    ngspice default values:
    - itl1: 100 (DC iteration limit)
    - itl2: 50 (DC transfer curve iteration limit)
    - itl4: 100 (Transient analysis iteration limit)
    - num_src_steps: 64 (Number of source steps for DC)
    - num_dst_levels: 8 (Number of destination steps)

    Args:
        metrics: Circuit complexity metrics

    Returns:
        Dictionary with iteration limits
    """
    score = metrics.overall_complexity_score
    has_nonlinear = metrics.has_nonlinear_elements
    has_dependent = metrics.source_complexity.num_dependent_sources > 0
    has_switches = metrics.component_counts.switches > 0
    num_nodes = metrics.topology.node_count

    # Base iteration limits (ngspice defaults)
    itl1 = 100
    itl2 = 50
    itl4 = 100
    num_src_steps = 64
    num_dst_levels = 8

    # Adjust based on circuit complexity
    if score < 10:
        # Simple circuits: fewer iterations needed
        itl1 = 50
        itl2 = 25
        itl4 = 50
        num_src_steps = 32
        num_dst_levels = 4
    elif score > 50:
        # Complex circuits: more iterations
        itl1 = 200
        itl2 = 100
        itl4 = 200
        num_src_steps = 128
        num_dst_levels = 16
    elif score > 100:
        # Very complex
        itl1 = 500
        itl2 = 200
        itl4 = 500
        num_src_steps = 256
        num_dst_levels = 32

    # Additional adjustments
    if has_nonlinear:
        # Nonlinear circuits need more iterations
        itl1 = max(itl1, 150)
        itl2 = max(itl2, 75)
        itl4 = max(itl4, 150)

    if has_dependent:
        # Dependent sources add complexity
        itl1 = max(itl1, 150)
        num_src_steps = max(num_src_steps, 128)

    if has_switches:
        # Switches need more transient iterations
        itl4 = max(itl4, 200)

    if num_nodes > 50:
        # Large circuits need more DC iterations
        itl1 = max(itl1, 150)

    return {
        "itl1": itl1,
        "itl2": itl2,
        "itl4": itl4,
        "num_src_steps": num_src_steps,
        "num_dst_levels": num_dst_levels,
    }


def suggest_solver_settings(
    metrics: CircuitComplexityMetrics,
    stop_time: Optional[float] = None,
) -> SolverSettings:
    """
    Suggest complete solver settings based on circuit complexity.

    This function aggregates all recommendation functions to provide
    a complete set of solver settings optimized for the given circuit.

    Args:
        metrics: Circuit complexity metrics
        stop_time: Simulation stop time (optional)

    Returns:
        SolverSettings with recommended values
    """
    # Get individual recommendations
    solver_type = recommend_solver_type(metrics)
    step_time, max_time_step, strategy = recommend_timestep_settings(
        metrics, stop_time
    )
    reltol, abstol, vntol = recommend_convergence_tolerances(metrics)
    iteration_limits = recommend_iteration_limits(metrics)

    # Build description
    difficulty = metrics.difficulty_level
    score = metrics.overall_complexity_score

    description_parts = [
        f"Circuit complexity score: {score:.1f} ({difficulty})",
        f"Recommended solver: {solver_type.value}",
        f"Timestep strategy: {strategy.value}",
        f"Step time: {step_time:.2e}s",
    ]

    if max_time_step:
        description_parts.append(f"Max timestep: {max_time_step:.2e}s")

    if metrics.has_nonlinear_elements:
        description_parts.append("Nonlinear elements detected - tighter tolerances recommended")

    if metrics.topology.has_feedback_loops:
        description_parts.append("Feedback loops present - adaptive timestep recommended")

    description = ". ".join(description_parts) + "."

    return SolverSettings(
        solver_type=solver_type,
        timestep_strategy=strategy,
        step_time=step_time,
        max_time_step=max_time_step,
        reltol=reltol,
        abstol=abstol,
        vntol=vntol,
        itl1=iteration_limits["itl1"],
        itl2=iteration_limits["itl2"],
        itl4=iteration_limits["itl4"],
        num_src_steps=iteration_limits["num_src_steps"],
        num_dst_levels=iteration_limits["num_dst_levels"],
        description=description,
    )
