"""
Schematic generation for circuit reports.

This module provides the SchematicGenerator class that generates
SVG circuit schematics from circuit definitions using schemdraw.
"""

from io import StringIO
from typing import Any, Dict, List, Optional

from circuit_sim.circuit import Circuit


class SchematicGenerator:
    """Generate SVG circuit schematics from Circuit objects."""

    def __init__(self, style: str = "modern"):
        """
        Initialize the schematic generator.

        Args:
            style: Style for schematic rendering ('modern', 'classic')
        """
        self.style = style
        self._schemdraw_available = True

        try:
            import schemdraw
            import schemdraw.elements as elm
            self.schemdraw = schemdraw
            self.elm = elm
        except ImportError:
            self._schemdraw_available = False

    def generate_schematic(
        self, circuit: Circuit, include_values: bool = True
    ) -> Optional[str]:
        """
        Generate an SVG schematic from a Circuit object.

        Args:
            circuit: Circuit object to render
            include_values: Whether to include component values in schematic

        Returns:
            SVG string of the schematic, or None if generation fails
        """
        if not self._schemdraw_available:
            return self._generate_fallback_schematic(circuit)

        try:
            return self._generate_schemdraw_schematic(circuit, include_values)
        except Exception:
            return self._generate_fallback_schematic(circuit)

    def _generate_schemdraw_schematic(
        self, circuit: Circuit, include_values: bool
    ) -> str:
        """Generate schematic using schemdraw."""
        import schemdraw
        import schemdraw.elements as elm

        # Create a new drawing
        d = schemdraw.Drawing(
            unit=1,
            inches_per_unit=1,
            lw=1.5,
            font_size=10,
        )

        # Build the schematic based on circuit components
        elements = self._build_schematic_elements(circuit, include_values)

        # Add elements to drawing
        for elem in elements:
            d.add(elem)

        # Save to SVG string
        output = StringIO()
        d.save(output, fmt="svg")
        return output.getvalue()

    def _build_schematic_elements(
        self, circuit: Circuit, include_values: bool
    ) -> List[Any]:
        """Build schematic elements from circuit components."""
        elements = []

        # Simple approach: iterate components and create elements
        # This creates a basic schematic - more complex layouts would require
        # graph algorithms for optimal component placement

        # Group components by type for easier processing
        voltage_sources = []
        resistors = []
        capacitors = []
        inductors = []
        current_sources = []
        diodes = []
        transistors = []
        other = []

        for comp in circuit.components:
            comp_type = comp.get("type", "")
            if comp_type == "voltage_source":
                voltage_sources.append(comp)
            elif comp_type == "resistor":
                resistors.append(comp)
            elif comp_type == "capacitor":
                capacitors.append(comp)
            elif comp_type == "inductor":
                inductors.append(comp)
            elif comp_type == "current_source":
                current_sources.append(comp)
            elif comp_type == "diode":
                diodes.append(comp)
            elif comp_type == "bjt_transistor":
                transistors.append(comp)
            else:
                other.append(comp)

        # Build the circuit representation
        # Use a simple left-to-right layout approach
        y_pos = 0

        # Add voltage sources
        for vs in voltage_sources:
            label = vs.get("name", "V")
            if include_values:
                label += f" {vs.get('dc_value', '')}"
            elements.append(
                self.elm.SourceV(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add resistors
        for r in resistors:
            label = r.get("name", "R")
            if include_values:
                label += f" {r.get('resistance', '')}"
            elements.append(
                self.elm.Resistor(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add capacitors
        for c in capacitors:
            label = c.get("name", "C")
            if include_values:
                label += f" {c.get('capacitance', '')}"
            elements.append(
                self.elm.Capacitor(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add inductors
        for l in inductors:
            label = l.get("name", "L")
            if include_values:
                label += f" {l.get('inductance', '')}"
            elements.append(
                self.elm.Inductor(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add current sources
        for cs in current_sources:
            label = cs.get("name", "I")
            if include_values:
                label += f" {cs.get('dc_value', '')}"
            elements.append(
                self.elm.SourceI(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add diodes
        for d in diodes:
            label = d.get("name", "D")
            elements.append(
                self.elm.Diode(label=label).at((0, y_pos))
            )
            y_pos += 2

        # Add transistors
        for t in transistors:
            label = t.get("name", "Q")
            elements.append(
                self.elm.NPN(transistor=True, label=label).at((0, y_pos))
            )
            y_pos += 2

        return elements

    def _generate_fallback_schematic(self, circuit: Circuit) -> str:
        """
        Generate a simple text-based schematic as fallback.

        Args:
            circuit: Circuit object

        Returns:
            SVG string with text representation
        """
        lines = [f"Circuit: {circuit.name}", ""]

        # Group components by type
        components_by_type: Dict[str, List[Dict]] = {}
        for comp in circuit.components:
            comp_type = comp.get("type", "unknown")
            if comp_type not in components_by_type:
                components_by_type[comp_type] = []
            components_by_type[comp_type].append(comp)

        # Generate text representation
        for comp_type, components in components_by_type.items():
            type_name = comp_type.replace("_", " ").title()
            lines.append(f"--- {type_name}s ---")
            for comp in components:
                name = comp.get("name", "?")
                if comp_type == "voltage_source":
                    value = comp.get("dc_value", "")
                    pos = comp.get("positive", "?")
                    neg = comp.get("negative", "?")
                    lines.append(f"  {name}: {value}V ({pos} to {neg})")
                elif comp_type == "resistor":
                    value = comp.get("resistance", "")
                    n1 = comp.get("node1", "?")
                    n2 = comp.get("node2", "?")
                    lines.append(f"  {name}: {value}Ω ({n1} to {n2})")
                elif comp_type == "capacitor":
                    value = comp.get("capacitance", "")
                    n1 = comp.get("node1", "?")
                    n2 = comp.get("node2", "?")
                    lines.append(f"  {name}: {value}F ({n1} to {n2})")
                elif comp_type == "inductor":
                    value = comp.get("inductance", "")
                    n1 = comp.get("node1", "?")
                    n2 = comp.get("node2", "?")
                    lines.append(f"  {name}: {value}H ({n1} to {n2})")
                elif comp_type == "current_source":
                    value = comp.get("dc_value", "")
                    lines.append(f"  {name}: {value}A")
                elif comp_type == "diode":
                    anode = comp.get("anode", "?")
                    cathode = comp.get("cathode", "?")
                    lines.append(f"  {name}: {anode} to {cathode}")
                elif comp_type == "bjt_transistor":
                    c = comp.get("collector", "?")
                    b = comp.get("base", "?")
                    e = comp.get("emitter", "?")
                    lines.append(f"  {name}: C={c}, B={b}, E={e}")
                else:
                    lines.append(f"  {name}")

        schematic_text = "\n".join(lines)

        # Wrap in SVG
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{len(lines) * 20 + 40}">
  <rect width="100%" height="100%" fill="#f5f5f5"/>
  <text x="10" y="25" font-family="monospace" font-size="12" fill="#333">
    {self._escape_svg_text(schematic_text)}
  </text>
</svg>'''

        return svg

    def _escape_svg_text(self, text: str) -> str:
        """Escape special characters for SVG text element."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
            .replace("\n", "&#10;")
        )

    def generate_thumbnail(
        self, circuit: Circuit, max_width: int = 300
    ) -> Optional[str]:
        """
        Generate a smaller thumbnail schematic.

        Args:
            circuit: Circuit object
            max_width: Maximum width in pixels

        Returns:
            SVG string of the thumbnail
        """
        return self.generate_schematic(circuit, include_values=False)
