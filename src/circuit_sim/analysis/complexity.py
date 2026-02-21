"""
Complexity analysis tools for electronic circuits.

This module provides data structures for measuring and scoring circuit complexity
including node count, component types, reactive elements, and topology complexity.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ComponentType(Enum):
    """Classification of electronic component types.
    
    Categories:
        PASSIVE: Resistors, capacitors, inductors
        SOURCE: Voltage and current sources
        ACTIVE: Transistors, diodes, op-amps
        REACTIVE: Energy storage elements (capacitors, inductors)
        NONLINEAR: Components with nonlinear behavior
    """

    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    VOLTAGE_SOURCE = "voltage_source"
    CURRENT_SOURCE = "current_source"
    BJT_TRANSISTOR = "bjt_transistor"
    MOSFET_TRANSISTOR = "mosfet_transistor"
    DIODE = "diode"
    OPAMP = "opamp"
    LED = "led"
    ZENER = "zener"
    TRANSFORMER = "transformer"
    SWITCH = "switch"
    Josephson_JUNCTION = "josephson_junction"
    UNKNOWN = "unknown"


class ReactiveType(Enum):
    """Classification of reactive (energy storage) elements."""

    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    TRANSFORMER = "transformer"


class TopologyType(Enum):
    """Classification of circuit topology structures."""

    SERIES = "series"
    PARALLEL = "parallel"
    BRIDGE = "bridge"
    MESH = "mesh"
    LADDER = "ladder"
    FEEDBACK = "feedback"
    MIXED = "mixed"


@dataclass
class NodeMetrics:
    """Metrics for individual circuit nodes.
    
    Attributes:
        node_id: Unique identifier for the node
        degree: Number of connections to this node
        is_ground: Whether this node is ground (node 0)
        component_count: Number of components connected to this node
        voltage_source_count: Number of voltage sources connected
        reactive_count: Number of reactive elements connected
    """

    node_id: int
    degree: int = 0
    is_ground: bool = False
    component_count: int = 0
    voltage_source_count: int = 0
    reactive_count: int = 0

    def __post_init__(self) -> None:
        """Set derived fields after initialization."""
        if self.node_id == 0:
            self.is_ground = True


@dataclass
class ComponentMetrics:
    """Metrics for individual components.
    
    Attributes:
        name: Component identifier
        component_type: Type of component from ComponentType enum
        is_reactive: Whether component stores energy
        terminal_count: Number of terminals (2 for passive, 3 for transistors, etc.)
        is_nonlinear: Whether component has nonlinear characteristics
        is_controlled: Whether component is controlled (e.g., dependent sources)
    """

    name: str
    component_type: ComponentType
    is_reactive: bool = False
    terminal_count: int = 2
    is_nonlinear: bool = False
    is_controlled: bool = False

    def __post_init__(self) -> None:
        """Set derived fields based on component type."""
        if self.component_type in (ComponentType.CAPACITOR, ComponentType.INDUCTOR, ComponentType.TRANSFORMER):
            self.is_reactive = True
        if self.component_type in (ComponentType.DIODE, ComponentType.LED, ComponentType.ZENER,
                                    ComponentType.BJT_TRANSISTOR, ComponentType.MOSFET_TRANSISTOR):
            self.is_nonlinear = True


@dataclass
class TopologyMetrics:
    """Metrics describing circuit topology complexity.
    
    Attributes:
        node_count: Total number of nodes (excluding ground)
        total_nodes: Total nodes including ground
        component_count: Total number of components
        reactive_element_count: Number of reactive elements
        voltage_source_count: Number of voltage sources
        current_source_count: Number of current sources
        nonlinear_count: Number of nonlinear components
        max_node_degree: Maximum degree of any node
        avg_node_degree: Average degree across all nodes
        has_feedback: Whether circuit has feedback paths
        has_coupling: Whether circuit has coupling elements (transformers)
        has_ground_reference: Whether circuit has ground reference
        mesh_count: Estimated number of independent meshes
        has_feedback_loops: Alias for has_feedback for backward compatibility
    """

    node_count: int = 0
    total_nodes: int = 0
    component_count: int = 0
    reactive_element_count: int = 0
    voltage_source_count: int = 0
    current_source_count: int = 0
    nonlinear_count: int = 0
    max_node_degree: int = 0
    avg_node_degree: float = 0.0
    has_feedback: bool = False
    has_coupling: bool = False
    has_ground_reference: bool = True
    mesh_count: int = 0

    @property
    def has_feedback_loops(self) -> bool:
        """Alias for has_feedback for backward compatibility."""
        return self.has_feedback


@dataclass
class SourceComplexity:
    """Metrics for source complexity in a circuit.
    
    Attributes:
        num_dc_sources: Number of DC voltage/current sources
        num_ac_sources: Number of AC sources
        num_pulse_sources: Number of pulse sources
        num_sine_sources: Number of sine wave sources
        num_dependent_sources: Number of dependent (controlled) sources
        max_frequency_components: Maximum frequency among AC sources
    """

    num_dc_sources: int = 0
    num_ac_sources: int = 0
    num_pulse_sources: int = 0
    num_sine_sources: int = 0
    num_dependent_sources: int = 0
    max_frequency_components: float = 0.0


@dataclass
class ComponentCounts:
    """Counts of different component types in a circuit.
    
    Attributes:
        resistors: Number of resistors
        capacitors: Number of capacitors
        inductors: Number of inductors
        voltage_sources: Number of voltage sources
        current_sources: Number of current sources
        diodes: Number of diodes
        leds: Number of LEDs
        zeners: Number of Zener diodes
        bjt_transistors: Number of BJT transistors
        mosfets: Number of MOSFET transistors
        opamps: Number of operational amplifiers
        transformers: Number of transformers
        switches: Number of switches
        total_components: Total number of all components
        total_semiconductors: Total number of semiconductor components
    """

    resistors: int = 0
    capacitors: int = 0
    inductors: int = 0
    voltage_sources: int = 0
    current_sources: int = 0
    diodes: int = 0
    leds: int = 0
    zeners: int = 0
    bjt_transistors: int = 0
    mosfets: int = 0
    opamps: int = 0
    transformers: int = 0
    switches: int = 0

    @property
    def total_components(self) -> int:
        """Total count of all components."""
        return (
            self.resistors
            + self.capacitors
            + self.inductors
            + self.voltage_sources
            + self.current_sources
            + self.diodes
            + self.leds
            + self.zeners
            + self.bjt_transistors
            + self.mosfets
            + self.opamps
            + self.transformers
            + self.switches
        )

    @property
    def total_semiconductors(self) -> int:
        """Total count of semiconductor components."""
        return (
            self.diodes
            + self.leds
            + self.zeners
            + self.bjt_transistors
            + self.mosfets
        )


@dataclass
class ComplexityScore:
    """Aggregate complexity score for a circuit.
    
    This class combines multiple metrics into a unified complexity score
    that can be used for circuit comparison, synthesis guidance, and
    analysis difficulty estimation.
    
    The final score is on a 1-10 scale:
        - Simple (1-3): Basic circuits with few components
        - Moderate (4-6): Intermediate circuits with moderate complexity
        - Complex (7-9): Advanced circuits with multiple interacting elements
        - Very Complex (10): Sophisticated circuits requiring detailed analysis
    
    Attributes:
        node_count: Number of circuit nodes (excluding ground)
        component_count: Total number of components
        component_type_counts: Breakdown of components by type
        reactive_element_count: Number of reactive elements
        topology: Topology complexity metrics
        source_complexity: Source complexity metrics
        final_score: Final complexity score on 1-10 scale
        score_breakdown: Detailed breakdown of score components
    """

    node_count: int
    component_count: int
    component_type_counts: Dict[ComponentType, int] = field(default_factory=dict)
    reactive_element_count: int = 0
    topology: Optional[TopologyMetrics] = None
    source_complexity: Optional[SourceComplexity] = None
    final_score: float = 1.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    # Weights for combining factor scores (must sum to 1.0)
    NODE_WEIGHT: float = 0.15
    COMPONENT_WEIGHT: float = 0.20
    NONLINEAR_WEIGHT: float = 0.25
    REACTIVE_WEIGHT: float = 0.15
    TOPOLOGY_WEIGHT: float = 0.10
    SOURCE_WEIGHT: float = 0.15

    def _calculate_node_score(self) -> float:
        """Calculate node complexity score (0-10 scale).
        
        Args:
            node_count: Number of circuit nodes excluding ground
            
        Returns:
            Score from 0-10 based on node count
        """
        if self.node_count <= 1:
            return 1.0
        elif self.node_count <= 3:
            return 3.0
        elif self.node_count <= 5:
            return 5.0
        elif self.node_count <= 10:
            return 7.0
        else:
            return 10.0

    def _calculate_component_score(self) -> float:
        """Calculate component complexity score (0-10 scale).
        
        Args:
            component_count: Total number of components
            
        Returns:
            Score from 0-10 based on component count
        """
        if self.component_count <= 3:
            return 1.0
        elif self.component_count <= 6:
            return 3.0
        elif self.component_count <= 10:
            return 5.0
        elif self.component_count <= 20:
            return 7.0
        else:
            return 10.0

    def _calculate_nonlinear_score(self) -> float:
        """Calculate nonlinear element complexity score (0-10 scale).
        
        Returns:
            Score from 0-10 based on nonlinear component count
        """
        nonlinear_count = 0
        nonlinear_count += self.component_type_counts.get(ComponentType.DIODE, 0)
        nonlinear_count += self.component_type_counts.get(ComponentType.BJT_TRANSISTOR, 0)
        nonlinear_count += self.component_type_counts.get(ComponentType.MOSFET_TRANSISTOR, 0)
        nonlinear_count += self.component_type_counts.get(ComponentType.LED, 0)
        nonlinear_count += self.component_type_counts.get(ComponentType.ZENER, 0)
        nonlinear_count += self.component_type_counts.get(ComponentType.OPAMP, 0)
        
        if nonlinear_count == 0:
            return 1.0
        elif nonlinear_count == 1:
            return 3.0
        elif nonlinear_count <= 3:
            return 5.0
        elif nonlinear_count <= 5:
            return 7.0
        else:
            return 10.0

    def _calculate_reactive_score(self) -> float:
        """Calculate reactive element complexity score (0-10 scale).
        
        Returns:
            Score from 0-10 based on reactive element count
        """
        if self.reactive_element_count == 0:
            return 1.0
        elif self.reactive_element_count == 1:
            return 3.0
        elif self.reactive_element_count <= 3:
            return 5.0
        elif self.reactive_element_count <= 5:
            return 7.0
        else:
            return 10.0

    def _calculate_topology_score(self) -> float:
        """Calculate topology complexity score (0-10 scale).
        
        Returns:
            Score from 0-10 based on topology complexity
        """
        score = 1.0
        
        if self.topology:
            # Feedback loops add complexity
            if self.topology.has_feedback:
                score += 2.0
            
            # Coupling elements (transformers) add complexity
            if self.topology.has_coupling:
                score += 2.0
            
            # High node degree adds complexity
            if self.topology.max_node_degree > 3:
                score += 2.0
            
            # Multiple meshes add complexity
            if self.topology.mesh_count > 1:
                score += 2.0
            
            # Many reactive elements in topology
            if self.topology.reactive_element_count > 2:
                score += 2.0
        
        return min(score, 10.0)

    def _calculate_source_score(self) -> float:
        """Calculate source complexity score (0-10 scale).
        
        Returns:
            Score from 0-10 based on source complexity
        """
        score = 1.0
        
        if self.source_complexity:
            sources = self.source_complexity
            
            # Multiple DC sources add complexity
            if sources.num_dc_sources > 2:
                score += 1.5
            
            # AC sources add significant complexity
            if sources.num_ac_sources > 0:
                score += 2.0
            
            # Pulse/sine sources add complexity for time-domain analysis
            if sources.num_pulse_sources > 0 or sources.num_sine_sources > 0:
                score += 1.5
            
            # Dependent sources are more complex
            if sources.num_dependent_sources > 0:
                score += 2.5
            
            # Multiple frequency components
            if sources.max_frequency_components > 1e6:
                score += 1.5
        
        return min(score, 10.0)

    def calculate_score(self) -> float:
        """Calculate the final complexity score (1-10 scale).
        
        Combines all complexity factors (nodes, components, nonlinear, reactive,
        topology, sources) into a weighted final score on a 1-10 scale.
        
        Returns:
            Float representing overall circuit complexity (1-10 scale)
        """
        breakdown: Dict[str, float] = {}

        # Calculate individual factor scores (0-10 scale)
        breakdown["node_score"] = self._calculate_node_score()
        breakdown["component_score"] = self._calculate_component_score()
        breakdown["nonlinear_score"] = self._calculate_nonlinear_score()
        breakdown["reactive_score"] = self._calculate_reactive_score()
        breakdown["topology_score"] = self._calculate_topology_score()
        breakdown["source_score"] = self._calculate_source_score()

        # Calculate weighted final score
        weighted_sum = (
            breakdown["node_score"] * self.NODE_WEIGHT
            + breakdown["component_score"] * self.COMPONENT_WEIGHT
            + breakdown["nonlinear_score"] * self.NONLINEAR_WEIGHT
            + breakdown["reactive_score"] * self.REACTIVE_WEIGHT
            + breakdown["topology_score"] * self.TOPOLOGY_WEIGHT
            + breakdown["source_score"] * self.SOURCE_WEIGHT
        )

        # Scale to 1-10 range (minimum 1, maximum 10)
        self.final_score = max(1.0, min(10.0, weighted_sum))
        
        # Round to one decimal place
        self.final_score = round(self.final_score, 1)
        
        self.score_breakdown = breakdown
        
        return self.final_score

    def get_complexity_level(self) -> str:
        """Get human-readable complexity level.
        
        Returns:
            String describing complexity level: 'Simple', 'Moderate', 'Complex', or 'Very Complex'
        """
        if self.final_score <= 3.0:
            return "Simple"
        elif self.final_score <= 6.0:
            return "Moderate"
        elif self.final_score <= 9.0:
            return "Complex"
        else:
            return "Very Complex"

    def get_complexity_category(self) -> int:
        """Get complexity category as integer (1-10).
        
        Returns:
            Integer from 1-10 representing complexity category
        """
        return int(round(self.final_score))
            return "simple"
        elif self.weighted_score < 25:
            return "moderate"
        elif self.weighted_score < 50:
            return "complex"
        else:
            return "very_complex"

    def __str__(self) -> str:
        """String representation of complexity score."""
        level = self.get_complexity_level()
        return (
            f"Circuit Complexity Analysis:\n"
            f"  Nodes: {self.node_count}\n"
            f"  Components: {self.component_count}\n"
            f"  Reactive Elements: {self.reactive_element_count}\n"
            f"  Weighted Score: {self.weighted_score:.1f}\n"
            f"  Complexity Level: {level}"
        )


@dataclass
class CircuitComplexityMetrics:
    """Complete complexity metrics for a circuit.
    
    This is the main container that combines all complexity-related
    metrics into a single structure for comprehensive circuit analysis.
    
    Attributes:
        topology: Topology-level complexity metrics
        component_counts: Count of each component type
        source_complexity: Source-related complexity metrics
        component_types: Count of each component type (dict form)
        node_metrics: List of per-node metrics
        component_metrics: List of per-component metrics
        overall_score: Aggregate complexity score
        overall_complexity_score: Property for easy access to weighted score
        difficulty_level: Property for easy access to difficulty level
        has_nonlinear_elements: Property to check for nonlinear elements
    """

    topology: TopologyMetrics = field(default_factory=TopologyMetrics)
    component_counts: ComponentCounts = field(default_factory=ComponentCounts)
    source_complexity: SourceComplexity = field(default_factory=SourceComplexity)
    component_types: Dict[ComponentType, int] = field(default_factory=dict)
    node_metrics: List[NodeMetrics] = field(default_factory=list)
    component_metrics: List[ComponentMetrics] = field(default_factory=list)
    overall_score: Optional[ComplexityScore] = None

    @property
    def overall_complexity_score(self) -> float:
        """Get the overall complexity score."""
        if self.overall_score:
            return self.overall_score.weighted_score
        return 0.0

    @property
    def difficulty_level(self) -> str:
        """Get the difficulty level as a string."""
        if self.overall_score:
            return self.overall_score.get_complexity_level()
        return "unknown"

    @property
    def has_nonlinear_elements(self) -> bool:
        """Check if circuit has nonlinear elements."""
        return (
            self.component_counts.diodes
            + self.component_counts.leds
            + self.component_counts.zeners
            + self.component_counts.bjt_transistors
            + self.component_counts.mosfets
        ) > 0

    @classmethod
    def from_circuit(cls, circuit) -> "CircuitComplexityMetrics":
        """Create complexity metrics from a Circuit object.
        
        Args:
            circuit: A Circuit instance to analyze
            
        Returns:
            CircuitComplexityMetrics with computed metrics
        """
        metrics = cls()
        
        # Count nodes (exclude ground)
        node_set = circuit.nodes.copy()
        if 0 in node_set:
            node_set.remove(0)
        metrics.topology.node_count = len(node_set)
        metrics.topology.total_nodes = len(circuit.nodes)
        
        # Count components
        counts = ComponentCounts()
        component_types: Dict[ComponentType, int] = {}
        
        for comp in circuit.components:
            comp_type = comp.get("type", "unknown")
            
            if comp_type == "resistor":
                counts.resistors += 1
                ctype = ComponentType.RESISTOR
            elif comp_type == "capacitor":
                counts.capacitors += 1
                metrics.topology.reactive_element_count += 1
                ctype = ComponentType.CAPACITOR
            elif comp_type == "inductor":
                counts.inductors += 1
                metrics.topology.reactive_element_count += 1
                ctype = ComponentType.INDUCTOR
            elif comp_type == "voltage_source":
                counts.voltage_sources += 1
                metrics.topology.voltage_source_count += 1
                ctype = ComponentType.VOLTAGE_SOURCE
            elif comp_type == "current_source":
                counts.current_sources += 1
                metrics.topology.current_source_count += 1
                ctype = ComponentType.CURRENT_SOURCE
            elif comp_type == "diode":
                counts.diodes += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.DIODE
            elif comp_type == "led":
                counts.leds += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.LED
            elif comp_type == "zener":
                counts.zeners += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.ZENER
            elif comp_type == "bjt_transistor":
                counts.bjt_transistors += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.BJT_TRANSISTOR
            elif comp_type == "mosfet":
                counts.mosfets += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.MOSFET_TRANSISTOR
            elif comp_type == "opamp":
                counts.opamps += 1
                metrics.topology.nonlinear_count += 1
                ctype = ComponentType.OPAMP
            elif comp_type == "transformer":
                counts.transformers += 1
                metrics.topology.has_coupling = True
                metrics.topology.reactive_element_count += 1
                ctype = ComponentType.TRANSFORMER
            elif comp_type == "switch":
                counts.switches += 1
                ctype = ComponentType.SWITCH
            else:
                ctype = ComponentType.UNKNOWN
            
            # Update component type counts
            component_types[ctype] = component_types.get(ctype, 0) + 1
        
        metrics.component_counts = counts
        metrics.component_types = component_types
        metrics.topology.component_count = counts.total_components
        
        # Calculate overall complexity score
        metrics.overall_score = ComplexityScore(
            node_count=metrics.topology.node_count,
            component_count=counts.total_components,
            component_type_counts=component_types,
            reactive_element_count=metrics.topology.reactive_element_count,
            topology=metrics.topology,
        )
        metrics.overall_score.calculate_score()
        
        return metrics

    def get_summary(self) -> Dict[str, any]:
        """Get a dictionary summary of all metrics.
        
        Returns:
            Dictionary containing key metrics for easy access
        """
        return {
            "node_count": self.topology.node_count,
            "component_count": self.component_counts.total_components,
            "reactive_elements": self.topology.reactive_element_count,
            "nonlinear_components": self.topology.nonlinear_count,
            "max_node_degree": self.topology.max_node_degree,
            "has_feedback": self.topology.has_feedback,
            "complexity_score": self.overall_complexity_score,
            "complexity_level": self.difficulty_level,
        }


# Scoring constants module-level access
SCORING_CONSTANTS = {
    "NODE_WEIGHT": 1.0,
    "COMPONENT_WEIGHT": 1.0,
    "REACTIVE_WEIGHT": 2.0,
    "NONLINEAR_WEIGHT": 3.0,
    "FEEDBACK_WEIGHT": 2.5,
}


def CalculateComplexityScore(
    circuit,
    include_topology: bool = True,
) -> CircuitComplexityMetrics:
    """Calculate the complexity score for a circuit.
    
    This is the main entry point for calculating circuit complexity.
    It analyzes the circuit components and topology to produce a
    comprehensive complexity metrics object.
    
    Args:
        circuit: A Circuit instance or dict with 'nodes' and 'components'
        include_topology: Whether to include detailed topology analysis
        
    Returns:
        CircuitComplexityMetrics containing all complexity data and score
        
    Example:
        >>> from circuit_sim import Circuit
        >>> from circuit_sim.analysis.complexity import CalculateComplexityScore
        >>> 
        >>> circuit = Circuit("My Circuit")
        >>> circuit.add_resistor("R1", node1=1, node2=2, resistance="1k")
        >>> circuit.add_capacitor("C1", node1=2, node2=0, capacitance="1u")
        >>> 
        >>> metrics = CalculateComplexityScore(circuit)
        >>> print(f"Complexity: {metrics.overall_complexity_score}")
        >>> print(f"Level: {metrics.difficulty_level}")
    """
    # Create metrics from circuit
    metrics = CircuitComplexityMetrics.from_circuit(circuit)
    
    # Ensure score is calculated
    if metrics.overall_score is None:
        metrics.overall_score = ComplexityScore(
            node_count=metrics.topology.node_count,
            component_count=metrics.component_counts.total_components,
            component_type_counts=metrics.component_types,
            reactive_element_count=metrics.topology.reactive_element_count,
            topology=metrics.topology if include_topology else None,
        )
    
    metrics.overall_score.calculate_score()
    
    return metrics


# Alias for backwards compatibility and simpler API
ComplexityMetrics = CircuitComplexityMetrics
