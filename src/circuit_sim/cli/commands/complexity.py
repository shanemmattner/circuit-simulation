"""
Complexity analysis CLI commands.

Commands for analyzing circuit complexity and generating complexity scores.
"""

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from circuit_sim.analysis.complexity import CalculateComplexityScore
from circuit_sim.cli.exceptions import UserError
from circuit_sim.cli.utils.output import print_error, print_info, print_success

console = Console()


def load_circuit_for_analysis(circuit_id: str) -> dict:
    """
    Load circuit data from local project for complexity analysis.

    Args:
        circuit_id: Circuit identifier

    Returns:
        Circuit metadata dictionary

    Raises:
        UserError: If circuit not found
    """
    circuits_dir = Path.cwd() / "circuits"
    metadata_file = circuits_dir / f"{circuit_id}.json"

    if not metadata_file.exists():
        available_circuits = (
            list(circuits_dir.glob("*.json")) if circuits_dir.exists() else []
        )
        circuit_ids = [f.stem for f in available_circuits]

        suggestion = "Use 'circuit-sim list' to see available circuits"
        if circuit_ids:
            suggestion += f"\nAvailable circuit IDs: {', '.join(circuit_ids[:3])}"
            if len(circuit_ids) > 3:
                suggestion += f" (+{len(circuit_ids)-3} more)"

        raise UserError(f"Circuit not found: {circuit_id}", suggestion=suggestion)

    try:
        return json.loads(metadata_file.read_text())
    except json.JSONDecodeError as e:
        raise UserError(
            f"Invalid circuit metadata file: {metadata_file}",
            suggestion="The circuit metadata may be corrupted",
        ) from e


def create_circuit_from_metadata(metadata: dict):
    """
    Create a Circuit object from circuit metadata.

    Args:
        metadata: Circuit metadata dictionary

    Returns:
        Circuit object
    """
    from circuit_sim.circuit import Circuit

    circuit = Circuit(metadata.get("name", "Unknown"))

    # Get components from metadata
    components = metadata.get("components", [])

    for comp in components:
        comp_type = comp.get("type", "")
        name = comp.get("name", "")
        node1 = comp.get("node1", comp.get("positive_node", "1"))
        node2 = comp.get("node2", comp.get("negative_node", "0"))
        value = comp.get("value", "")

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
        elif comp_type == "led":
            circuit.add_led(name, node1, node2)
        elif comp_type == "zener":
            circuit.add_zener(name, node1, node2)
        elif comp_type == "opamp":
            circuit.add_opamp(name, node1, node2, node1)
        elif comp_type == "mosfet":
            circuit.addMosfet(name, node1, node2, node1)
        elif comp_type == "bjt_transistor":
            circuit.add_bjt(name, node1, node2, node1)

    return circuit


def format_complexity_output(metrics) -> None:
    """
    Format and display complexity metrics using Rich.

    Args:
        metrics: CircuitComplexityMetrics instance
    """
    # Display overall complexity
    score = metrics.overall_complexity_score
    level = metrics.difficulty_level

    # Color code the score
    if score <= 3:
        score_color = "green"
        emoji = "🟢"
    elif score <= 6:
        score_color = "yellow"
        emoji = "🟡"
    elif score <= 8:
        score_color = "orange1"
        emoji = "🟠"
    else:
        score_color = "red"
        emoji = "🔴"

    console.print(f"\n{emoji} Circuit Complexity Analysis")
    console.print(f"  Score: [{score_color}]{score:.1f}/10[/{score_color}] ({level})")

    # Component breakdown table
    cc = metrics.component_counts

    table = Table(title="Component Breakdown")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="magenta", justify="right")

    if cc.resistors > 0:
        table.add_row("Resistors", str(cc.resistors))
    if cc.capacitors > 0:
        table.add_row("Capacitors", str(cc.capacitors))
    if cc.inductors > 0:
        table.add_row("Inductors", str(cc.inductors))
    if cc.voltage_sources > 0:
        table.add_row("Voltage Sources", str(cc.voltage_sources))
    if cc.current_sources > 0:
        table.add_row("Current Sources", str(cc.current_sources))
    if cc.diodes > 0:
        table.add_row("Diodes", str(cc.diodes))
    if cc.leds > 0:
        table.add_row("LEDs", str(cc.leds))
    if cc.zeners > 0:
        table.add_row("Zeners", str(cc.zeners))
    if cc.bjt_transistors > 0:
        table.add_row("BJTs", str(cc.bjt_transistors))
    if cc.mosfets > 0:
        table.add_row("MOSFETs", str(cc.mosfets))
    if cc.opamps > 0:
        table.add_row("OpAmps", str(cc.opamps))
    if cc.transformers > 0:
        table.add_row("Transformers", str(cc.transformers))

    table.add_row("Total", f"[bold]{cc.total_components}[/bold]")
    console.print(table)

    # Topology info
    topo = metrics.topology
    console.print(f"\n📊 Topology:")
    console.print(f"  Nodes: {topo.node_count}")
    console.print(f"  Reactive Elements: {topo.reactive_element_count}")
    console.print(f"  Nonlinear Components: {topo.nonlinear_count}")

    if topo.has_feedback:
        console.print("  ⚡ Feedback loops detected")
    if topo.has_coupling:
        console.print("  🔗 Coupling elements detected")


@click.command()
@click.option(
    "--circuit-id",
    required=True,
    help="Circuit ID to analyze (use 'circuit-sim list' to see available circuits)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file for complexity metrics (JSON)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed score breakdown",
)
def analyze(circuit_id: str, output: Optional[Path], verbose: bool):
    """Analyze circuit complexity and generate complexity score."""

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:

            task = progress.add_task("Loading circuit...", total=None)
            metadata = load_circuit_for_analysis(circuit_id)
            circuit = create_circuit_from_metadata(metadata)

            progress.update(task, description="Calculating complexity...")

            # Calculate complexity
            metrics = CalculateComplexityScore(circuit)

            progress.update(task, description="✅ Analysis complete")

        # Display results
        format_complexity_output(metrics)

        # Show verbose breakdown if requested
        if verbose and metrics.overall_score:
            console.print(f"\n📈 Score Breakdown:")
            breakdown = metrics.overall_score.score_breakdown
            if breakdown:
                console.print(f"  Node Score: {breakdown.get('node_score', 0):.1f}/10")
                console.print(f"  Component Score: {breakdown.get('component_score', 0):.1f}/10")
                console.print(f"  Nonlinear Score: {breakdown.get('nonlinear_score', 0):.1f}/10")
                console.print(f"  Reactive Score: {breakdown.get('reactive_score', 0):.1f}/10")
                console.print(f"  Topology Score: {breakdown.get('topology_score', 0):.1f}/10")
                console.print(f"  Source Score: {breakdown.get('source_score', 0):.1f}/10")

        # Save to file if requested
        if output:
            result = {
                "circuit_id": circuit_id,
                "circuit_name": metadata.get("name"),
                "complexity_score": metrics.overall_complexity_score,
                "complexity_level": metrics.difficulty_level,
                "component_counts": {
                    "resistors": metrics.component_counts.resistors,
                    "capacitors": metrics.component_counts.capacitors,
                    "inductors": metrics.component_counts.inductors,
                    "voltage_sources": metrics.component_counts.voltage_sources,
                    "current_sources": metrics.component_counts.current_sources,
                    "diodes": metrics.component_counts.diodes,
                    "leds": metrics.component_counts.leds,
                    "zeners": metrics.component_counts.zeners,
                    "bjt_transistors": metrics.component_counts.bjt_transistors,
                    "mosfets": metrics.component_counts.mosfets,
                    "opamps": metrics.component_counts.opamps,
                    "transformers": metrics.component_counts.transformers,
                    "total_components": metrics.component_counts.total_components,
                },
                "topology": {
                    "node_count": metrics.topology.node_count,
                    "reactive_element_count": metrics.topology.reactive_element_count,
                    "nonlinear_count": metrics.topology.nonlinear_count,
                    "has_feedback": metrics.topology.has_feedback,
                    "has_coupling": metrics.topology.has_coupling,
                },
            }
            output.write_text(json.dumps(result, indent=2))
            console.print(f"\n💾 Results saved to: {output}")

        print_success(f"Complexity analysis complete for '{metadata.get('name')}'")

    except UserError as e:
        print_error(e)
        raise click.ClickException(str(e))
    except Exception as e:
        print_error(f"Failed to analyze complexity: {str(e)}")
        raise click.ClickException(str(e))


@click.command()
@click.argument("netlist_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file for complexity metrics (JSON)",
)
def from_netlist(netlist_file: Path, output: Optional[Path]):
    """Analyze circuit complexity from a SPICE netlist file."""

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:

            task = progress.add_task("Parsing netlist...", total=None)

            # Import parser
            from circuit_sim.io.parsers.spice_parser import SpiceParser

            parser = SpiceParser()
            circuit = parser.parse_file(netlist_file)

            progress.update(task, description="Calculating complexity...")

            # Calculate complexity
            metrics = CalculateComplexityScore(circuit)

            progress.update(task, description="✅ Analysis complete")

        # Display results
        format_complexity_output(metrics)

        # Save to file if requested
        if output:
            result = {
                "netlist_file": str(netlist_file),
                "circuit_name": circuit.name,
                "complexity_score": metrics.overall_complexity_score,
                "complexity_level": metrics.difficulty_level,
                "component_counts": {
                    "resistors": metrics.component_counts.resistors,
                    "capacitors": metrics.component_counts.capacitors,
                    "inductors": metrics.component_counts.inductors,
                    "voltage_sources": metrics.component_counts.voltage_sources,
                    "current_sources": metrics.component_counts.current_sources,
                    "diodes": metrics.component_counts.diodes,
                    "total_components": metrics.component_counts.total_components,
                },
            }
            output.write_text(json.dumps(result, indent=2))
            console.print(f"\n💾 Results saved to: {output}")

        print_success(f"Complexity analysis complete for '{circuit.name}'")

    except Exception as e:
        print_error(f"Failed to analyze netlist: {str(e)}")
        raise click.ClickException(str(e))
