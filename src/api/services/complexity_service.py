"""
Complexity service for business logic operations.

Handles complexity calculation caching and response building.
"""

from typing import Dict, Optional

from src.api.models.complexity import (
    ComplexityResponse,
    ComponentCountsResponse,
    TopologyMetricsResponse,
    SourceComplexityResponse,
    ScoreBreakdownResponse,
)


class ComplexityService:
    """Service for managing circuit complexity analysis."""

    def __init__(self):
        """Initialize complexity service with in-memory cache."""
        self._cache: Dict[str, ComplexityResponse] = {}

    def build_response(self, metrics) -> ComplexityResponse:
        """
        Build API response from complexity metrics.

        Args:
            metrics: CircuitComplexityMetrics instance

        Returns:
            ComplexityResponse with formatted data
        """
        # Extract component counts
        cc = metrics.component_counts
        component_counts = ComponentCountsResponse(
            resistors=cc.resistors,
            capacitors=cc.capacitors,
            inductors=cc.inductors,
            voltage_sources=cc.voltage_sources,
            current_sources=cc.current_sources,
            diodes=cc.diodes,
            leds=cc.leds,
            zeners=cc.zeners,
            bjt_transistors=cc.bjt_transistors,
            mosfets=cc.mosfets,
            opamps=cc.opamps,
            transformers=cc.transformers,
            switches=cc.switches,
            total_components=cc.total_components,
            total_semiconductors=cc.total_semiconductors,
        )

        # Extract topology metrics
        topo = metrics.topology
        topology_metrics = TopologyMetricsResponse(
            node_count=topo.node_count,
            total_nodes=topo.total_nodes,
            component_count=topo.component_count,
            reactive_element_count=topo.reactive_element_count,
            voltage_source_count=topo.voltage_source_count,
            current_source_count=topo.current_source_count,
            nonlinear_count=topo.nonlinear_count,
            max_node_degree=topo.max_node_degree,
            avg_node_degree=topo.avg_node_degree,
            has_feedback=topo.has_feedback,
            has_coupling=topo.has_coupling,
            has_ground_reference=topo.has_ground_reference,
            mesh_count=topo.mesh_count,
        )

        # Extract source complexity
        src = metrics.source_complexity or _default_source_complexity()
        source_complexity = SourceComplexityResponse(
            num_dc_sources=src.num_dc_sources,
            num_ac_sources=src.num_ac_sources,
            num_pulse_sources=src.num_pulse_sources,
            num_sine_sources=src.num_sine_sources,
            num_dependent_sources=src.num_dependent_sources,
            max_frequency_components=src.max_frequency_components,
        )

        # Extract score breakdown
        score = metrics.overall_score
        if score and score.score_breakdown:
            score_breakdown = ScoreBreakdownResponse(
                node_score=score.score_breakdown.get("node_score", 0),
                component_score=score.score_breakdown.get("component_score", 0),
                nonlinear_score=score.score_breakdown.get("nonlinear_score", 0),
                reactive_score=score.score_breakdown.get("reactive_score", 0),
                topology_score=score.score_breakdown.get("topology_score", 0),
                source_score=score.score_breakdown.get("source_score", 0),
            )
        else:
            score_breakdown = ScoreBreakdownResponse()

        return ComplexityResponse(
            circuit_name=metrics.circuit_name if hasattr(metrics, 'circuit_name') else "Unknown",
            complexity_score=metrics.overall_complexity_score,
            complexity_level=metrics.difficulty_level,
            component_counts=component_counts,
            topology_metrics=topology_metrics,
            source_complexity=source_complexity,
            score_breakdown=score_breakdown,
        )

    def cache_result(self, circuit_id: str, response: ComplexityResponse) -> None:
        """
        Cache complexity result for a circuit.

        Args:
            circuit_id: Circuit identifier
            response: Complexity response to cache
        """
        response_data = response.model_copy()
        response_data.circuit_id = circuit_id
        self._cache[circuit_id] = response_data

    def get_cached(self, circuit_id: str) -> Optional[ComplexityResponse]:
        """
        Get cached complexity result.

        Args:
            circuit_id: Circuit identifier

        Returns:
            Cached ComplexityResponse if found, None otherwise
        """
        return self._cache.get(circuit_id)

    def clear_cache(self, circuit_id: Optional[str] = None) -> None:
        """
        Clear complexity cache.

        Args:
            circuit_id: Specific circuit to clear, or None to clear all
        """
        if circuit_id:
            self._cache.pop(circuit_id, None)
        else:
            self._cache.clear()


def _default_source_complexity():
    """Create default source complexity object."""
    from src.circuit_sim.analysis.complexity import SourceComplexity
    return SourceComplexity()
