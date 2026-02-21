"""
Tests for solver settings suggestion module.
"""

import pytest

from circuit_sim.analysis.solver_settings import (
    SolverType,
    TimestepStrategy,
    SolverSettings,
    recommend_solver_type,
    recommend_timestep_settings,
    recommend_convergence_tolerances,
    recommend_iteration_limits,
    suggest_solver_settings,
)
from circuit_sim.analysis.complexity import (
    CircuitComplexityMetrics,
    ComplexityScore,
    ComponentType,
    TopologyMetrics,
    ComponentCounts,
    SourceComplexity,
)


class TestSolverTypeRecommendation:
    """Tests for solver type recommendation based on circuit complexity."""

    def test_simple_circuit_direct_solver(self):
        """Simple circuits should use direct solver."""
        metrics = _create_simple_metrics()
        result = recommend_solver_type(metrics)
        assert result == SolverType.DIRECT

    def test_complex_circuit_iterative_solver(self):
        """Very complex circuits (score >= 100) should use iterative solver."""
        # Create metrics with score >= 100 (simple calculation: 50*1 + 80*1 = 130)
        metrics = CircuitComplexityMetrics()
        metrics.topology = TopologyMetrics(
            node_count=50,
            component_count=80,
        )
        metrics.component_counts = ComponentCounts(
            resistors=30,
            capacitors=5,
            inductors=5,
            voltage_sources=5,
        )
        metrics.overall_score = ComplexityScore(
            node_count=50,
            component_count=80,
            component_type_counts={},
            topology=metrics.topology,
        )
        metrics.overall_score.calculate_score()
        # Score should be >= 100, so iterative solver
        result = recommend_solver_type(metrics)
        assert result == SolverType.ITERATIVE

    def test_moderate_circuit_dependent_sources(self):
        """Moderate circuits (score 15-50) with dependent sources should use iterative."""
        metrics = _create_moderate_metrics()
        # Score should be between 15-50
        assert 15 <= metrics.overall_complexity_score < 50
        # Add dependent sources
        metrics.source_complexity.num_dependent_sources = 2
        result = recommend_solver_type(metrics)
        assert result == SolverType.ITERATIVE

    def test_moderate_circuit_without_dependent(self):
        """Moderate circuits without challenging elements should use direct."""
        metrics = _create_moderate_metrics()
        result = recommend_solver_type(metrics)
        assert result == SolverType.DIRECT

    def test_large_node_count_iterative(self):
        """Moderate circuits with many nodes (>40) should use iterative."""
        metrics = _create_moderate_metrics()
        # Verify score is in 15-50 range
        assert 15 <= metrics.overall_complexity_score < 50
        # Set node count > 40
        metrics.topology.node_count = 45
        # Need to recalculate score to include higher node count impact
        metrics.overall_score = ComplexityScore(
            node_count=45,
            component_count=metrics.component_counts.total_components,
            component_type_counts={},
            topology=metrics.topology,
        )
        metrics.overall_score.calculate_score()
        result = recommend_solver_type(metrics)
        assert result == SolverType.ITERATIVE


class TestTimestepSettings:
    """Tests for timestep settings recommendation."""

    def test_fixed_timestep_simple_circuit(self):
        """Simple circuits without reactive elements should use fixed timestep."""
        metrics = _create_simple_metrics()
        step_time, max_time_step, strategy = recommend_timestep_settings(metrics)
        assert strategy == TimestepStrategy.FIXED

    def test_adaptive_timestep_nonlinear(self):
        """Circuits with nonlinear elements should use adaptive timestep."""
        # has_nonlinear_elements checks component_counts, not topology.nonlinear_count
        metrics = CircuitComplexityMetrics()
        metrics.component_counts = ComponentCounts(diodes=1)
        step_time, max_time_step, strategy = recommend_timestep_settings(metrics)
        assert strategy == TimestepStrategy.ADAPTIVE

    def test_adaptive_timestep_with_switches(self):
        """Circuits with switches should use adaptive timestep."""
        metrics = _create_simple_metrics()
        metrics.component_counts.switches = 1
        step_time, max_time_step, strategy = recommend_timestep_settings(metrics)
        assert strategy == TimestepStrategy.ADAPTIVE

    def test_adaptive_timestep_with_pulse_sources(self):
        """Circuits with pulse sources should use adaptive timestep."""
        metrics = _create_simple_metrics()
        metrics.source_complexity.num_pulse_sources = 1
        step_time, max_time_step, strategy = recommend_timestep_settings(metrics)
        assert strategy == TimestepStrategy.ADAPTIVE

    def test_adaptive_timestep_with_feedback(self):
        """Circuits with feedback loops should use adaptive timestep."""
        metrics = _create_simple_metrics()
        metrics.topology.has_feedback = True
        step_time, max_time_step, strategy = recommend_timestep_settings(metrics)
        assert strategy == TimestepStrategy.ADAPTIVE


class TestConvergenceTolerances:
    """Tests for convergence tolerance recommendations."""

    def test_simple_circuit_looser_tolerance(self):
        """Simple circuits can use looser tolerances for speed."""
        metrics = _create_simple_metrics()
        reltol, abstol, vntol = recommend_convergence_tolerances(metrics)
        assert reltol == 1e-2  # Looser for simple circuits

    def test_complex_circuit_tighter_tolerance(self):
        """Complex circuits need tighter tolerances."""
        metrics = _create_complex_metrics()
        reltol, abstol, vntol = recommend_convergence_tolerances(metrics)
        assert reltol < 1e-3  # Tighter than default

    def test_nonlinear_circuit_tighter(self):
        """Nonlinear circuits need tighter tolerances."""
        # has_nonlinear_elements checks component_counts, not topology.nonlinear_count
        metrics = CircuitComplexityMetrics()
        metrics.component_counts = ComponentCounts(diodes=1)
        metrics.topology = TopologyMetrics(node_count=1, component_count=1)
        reltol, abstol, vntol = recommend_convergence_tolerances(metrics)
        assert reltol <= 5e-4
        assert vntol <= 1e-8


class TestIterationLimits:
    """Tests for iteration limit recommendations."""

    def test_simple_circuit_lower_limits(self):
        """Simple circuits need fewer iterations."""
        metrics = _create_simple_metrics()
        limits = recommend_iteration_limits(metrics)
        assert limits["itl1"] == 50
        assert limits["itl2"] == 25
        assert limits["itl4"] == 50

    def test_complex_circuit_higher_limits(self):
        """Complex circuits need more iterations."""
        metrics = _create_complex_metrics()
        limits = recommend_iteration_limits(metrics)
        assert limits["itl1"] > 100
        assert limits["itl4"] > 100

    def test_nonlinear_circuit_increased_itl4(self):
        """Nonlinear circuits need more transient iterations."""
        # has_nonlinear_elements checks component_counts
        metrics = CircuitComplexityMetrics()
        metrics.component_counts = ComponentCounts(diodes=1)
        metrics.topology = TopologyMetrics(node_count=1, component_count=1)
        limits = recommend_iteration_limits(metrics)
        assert limits["itl4"] >= 150


class TestSuggestSolverSettings:
    """Tests for complete solver settings suggestion."""

    def test_suggest_simple_circuit_settings(self):
        """Test solver settings suggestion for simple circuit."""
        metrics = _create_simple_metrics()
        settings = suggest_solver_settings(metrics)
        
        assert isinstance(settings, SolverSettings)
        assert settings.solver_type == SolverType.DIRECT
        assert settings.step_time > 0

    def test_suggest_complex_circuit_settings(self):
        """Test solver settings suggestion for complex circuit."""
        metrics = _create_complex_metrics()
        settings = suggest_solver_settings(metrics)
        
        assert isinstance(settings, SolverSettings)
        assert settings.reltol < 1e-3  # Tighter tolerance

    def test_settings_include_description(self):
        """Settings should include human-readable description."""
        metrics = _create_simple_metrics()
        settings = suggest_solver_settings(metrics)
        
        assert settings.description != ""
        assert "complexity" in settings.description.lower()

    def test_settings_to_dict(self):
        """Test conversion of SolverSettings to dictionary."""
        metrics = _create_simple_metrics()
        settings = suggest_solver_settings(metrics)
        
        settings_dict = settings.to_dict()
        assert isinstance(settings_dict, dict)
        assert "solver_type" in settings_dict
        assert "reltol" in settings_dict
        assert settings_dict["solver_type"] == settings.solver_type.value


def _create_simple_metrics() -> CircuitComplexityMetrics:
    """Create a simple circuit metrics (low complexity)."""
    metrics = CircuitComplexityMetrics()
    metrics.topology = TopologyMetrics(
        node_count=2,
        component_count=3,
        reactive_element_count=0,
        nonlinear_count=0,
    )
    metrics.component_counts = ComponentCounts(
        resistors=2,
        voltage_sources=1,
    )
    metrics.source_complexity = SourceComplexity()
    metrics.overall_score = ComplexityScore(
        node_count=2,
        component_count=3,
        component_type_counts={
            ComponentType.RESISTOR: 2,
            ComponentType.VOLTAGE_SOURCE: 1,
        },
        reactive_element_count=0,
        topology=metrics.topology,
    )
    metrics.overall_score.calculate_score()
    return metrics


def _create_moderate_metrics() -> CircuitComplexityMetrics:
    """Create a moderate complexity circuit metrics (score ~25-30)."""
    metrics = CircuitComplexityMetrics()
    metrics.topology = TopologyMetrics(
        node_count=10,
        component_count=15,
        reactive_element_count=2,
        nonlinear_count=0,
    )
    metrics.component_counts = ComponentCounts(
        resistors=8,
        capacitors=2,
        voltage_sources=2,
        current_sources=1,
    )
    metrics.source_complexity = SourceComplexity()
    metrics.overall_score = ComplexityScore(
        node_count=10,
        component_count=15,
        component_type_counts={
            ComponentType.RESISTOR: 8,
            ComponentType.CAPACITOR: 2,
            ComponentType.VOLTAGE_SOURCE: 2,
            ComponentType.CURRENT_SOURCE: 1,
        },
        reactive_element_count=2,
        topology=metrics.topology,
    )
    metrics.overall_score.calculate_score()
    return metrics


def _create_complex_metrics() -> CircuitComplexityMetrics:
    """Create a complex circuit metrics (score >= 100 for iterative solver)."""
    metrics = CircuitComplexityMetrics()
    metrics.topology = TopologyMetrics(
        node_count=50,
        component_count=80,
        reactive_element_count=10,
        nonlinear_count=5,
        has_feedback=True,
    )
    metrics.component_counts = ComponentCounts(
        resistors=30,
        capacitors=5,
        inductors=5,
        voltage_sources=5,
        current_sources=2,
        diodes=3,
        bjt_transistors=2,
    )
    metrics.source_complexity = SourceComplexity(
        num_ac_sources=2,
        num_pulse_sources=1,
    )
    metrics.overall_score = ComplexityScore(
        node_count=50,
        component_count=80,
        component_type_counts={
            ComponentType.RESISTOR: 30,
            ComponentType.CAPACITOR: 5,
            ComponentType.INDUCTOR: 5,
            ComponentType.VOLTAGE_SOURCE: 5,
            ComponentType.CURRENT_SOURCE: 2,
            ComponentType.DIODE: 3,
            ComponentType.BJT_TRANSISTOR: 2,
        },
        reactive_element_count=10,
        topology=metrics.topology,
    )
    metrics.overall_score.calculate_score()
    return metrics
