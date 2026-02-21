"""
Pydantic models for complexity-related API operations.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ComponentInput(BaseModel):
    """Input model for components in complexity analysis."""

    type: str = Field(..., description="Component type (resistor, capacitor, etc.)")
    name: str = Field(..., description="Component identifier")
    positive_node: Optional[str] = Field(None, description="Positive terminal node")
    negative_node: Optional[str] = Field(None, description="Negative terminal node")
    node1: Optional[str] = Field(None, description="First node (alias for positive_node)")
    node2: Optional[str] = Field(None, description="Second node (alias for negative_node)")
    value: str = Field(..., description="Component value")


class ComplexityRequest(BaseModel):
    """Request model for complexity analysis."""

    name: str = Field(..., description="Circuit name")
    components: List[ComponentInput] = Field(..., description="Circuit components")

    def to_circuit(self):
        """Convert request to Circuit object."""
        from src.circuit_sim.circuit import Circuit
        
        circuit = Circuit(self.name)
        
        for comp in self.components:
            node1 = comp.positive_node or comp.node1 or "1"
            node2 = comp.negative_node or comp.node2 or "0"
            value = comp.value
            name = comp.name
            
            comp_type = comp.type.lower()
            if comp_type == "resistor":
                circuit.add_resistor(name, node1, node2, value)
            elif comp_type == "capacitor":
                circuit.add_capacitor(name, node1, node2, value)
            elif comp_type == "inductor":
                circuit.add_inductor(name, node1, node2, value)
            elif comp_type == "voltage_source":
                circuit.add_voltage_source(name, node1, node2, value)
            elif comp_type == "current_source":
                circuit.add_current_source(name, node1, node2, value)
            elif comp_type == "diode":
                circuit.add_diode(name, node1, node2)
            elif comp_type == "mosfet":
                circuit.add_mosfet(name, node1, node2, node1)  # Simplified
            elif comp_type == "opamp":
                circuit.add_opamp(name, node1, node2, node1, node1, node1)  # Simplified
            elif comp_type == "led":
                circuit.add_led(name, node1, node2)
            elif comp_type == "zener":
                circuit.add_zener(name, node1, node2)
            elif comp_type == "bjt_transistor":
                circuit.add_bjt_transistor(name, node1, node2, node1)  # Simplified
            elif comp_type == "transformer":
                circuit.add_transformer(name, node1, node2, node1, node2)  # Simplified
            elif comp_type == "switch":
                circuit.add_switch(name, node1, node2)
        
        return circuit


class ComponentCountsResponse(BaseModel):
    """Response model for component counts."""

    resistors: int = Field(0, description="Number of resistors")
    capacitors: int = Field(0, description="Number of capacitors")
    inductors: int = Field(0, description="Number of inductors")
    voltage_sources: int = Field(0, description="Number of voltage sources")
    current_sources: int = Field(0, description="Number of current sources")
    diodes: int = Field(0, description="Number of diodes")
    leds: int = Field(0, description="Number of LEDs")
    zeners: int = Field(0, description="Number of Zener diodes")
    bjt_transistors: int = Field(0, description="Number of BJT transistors")
    mosfets: int = Field(0, description="Number of MOSFET transistors")
    opamps: int = Field(0, description="Number of operational amplifiers")
    transformers: int = Field(0, description="Number of transformers")
    switches: int = Field(0, description="Number of switches")
    total_components: int = Field(0, description="Total component count")
    total_semiconductors: int = Field(0, description="Total semiconductor count")


class TopologyMetricsResponse(BaseModel):
    """Response model for topology metrics."""

    node_count: int = Field(0, description="Number of circuit nodes")
    total_nodes: int = Field(0, description="Total nodes including ground")
    component_count: int = Field(0, description="Total component count")
    reactive_element_count: int = Field(0, description="Number of reactive elements")
    voltage_source_count: int = Field(0, description="Number of voltage sources")
    current_source_count: int = Field(0, description="Number of current sources")
    nonlinear_count: int = Field(0, description="Number of nonlinear components")
    max_node_degree: int = Field(0, description="Maximum node degree")
    avg_node_degree: float = Field(0.0, description="Average node degree")
    has_feedback: bool = Field(False, description="Whether circuit has feedback")
    has_coupling: bool = Field(False, description="Whether circuit has coupling")
    has_ground_reference: bool = Field(True, description="Whether circuit has ground")
    mesh_count: int = Field(0, description="Estimated mesh count")


class SourceComplexityResponse(BaseModel):
    """Response model for source complexity."""

    num_dc_sources: int = Field(0, description="Number of DC sources")
    num_ac_sources: int = Field(0, description="Number of AC sources")
    num_pulse_sources: int = Field(0, description="Number of pulse sources")
    num_sine_sources: int = Field(0, description="Number of sine sources")
    num_dependent_sources: int = Field(0, description="Number of dependent sources")
    max_frequency_components: float = Field(0.0, description="Max frequency in Hz")


class ScoreBreakdownResponse(BaseModel):
    """Response model for score breakdown."""

    node_score: float = Field(0.0, description="Node complexity score")
    component_score: float = Field(0.0, description="Component complexity score")
    nonlinear_score: float = Field(0.0, description="Nonlinear element score")
    reactive_score: float = Field(0.0, description="Reactive element score")
    topology_score: float = Field(0.0, description="Topology complexity score")
    source_score: float = Field(0.0, description="Source complexity score")


class ComplexityResponse(BaseModel):
    """Response model for complexity analysis."""

    circuit_id: Optional[str] = Field(None, description="Circuit identifier")
    circuit_name: str = Field(..., description="Circuit name")
    complexity_score: float = Field(..., description="Overall complexity score (1-10)")
    complexity_level: str = Field(..., description="Difficulty level")
    component_counts: ComponentCountsResponse = Field(
        ..., description="Component type counts"
    )
    topology_metrics: TopologyMetricsResponse = Field(
        ..., description="Topology metrics"
    )
    source_complexity: SourceComplexityResponse = Field(
        ..., description="Source complexity details"
    )
    score_breakdown: ScoreBreakdownResponse = Field(
        ..., description="Detailed score breakdown"
    )
