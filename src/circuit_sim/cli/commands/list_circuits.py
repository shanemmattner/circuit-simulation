"""
Circuit listing and information commands.

Commands for viewing available circuits and their details.
"""

import json
from pathlib import Path
from typing import Dict, List

import click
from rich.console import Console
from rich.table import Table

from circuit_sim.cli.commands.simulate import load_circuit_metadata
from circuit_sim.cli.exceptions import UserError
from circuit_sim.cli.utils.output import print_error, print_info

console = Console()


def get_all_circuits() -> List[Dict]:
    """
    Get all available circuits in the current project.

    Returns:
        List of circuit metadata dictionaries
    """
    circuits_dir = Path.cwd() / "circuits"

    if not circuits_dir.exists():
        return []

    circuits = []
    for metadata_file in circuits_dir.glob("*.json"):
        try:
            metadata = json.loads(metadata_file.read_text())
            circuits.append(metadata)
        except json.JSONDecodeError:
            continue  # Skip invalid files

    return sorted(circuits, key=lambda c: c.get("created_at", ""))


@click.command()
def list_circuits():
    """List all circuits in the current project."""

    circuits = get_all_circuits()

    if not circuits:
        print_info("No circuits found in current project")
        console.print(
            "💡 Create a circuit with: [bold]circuit-sim create --netlist <file> --name <name>[/bold]"
        )
        return

    # Create a beautiful table
    table = Table(title=f"Available Circuits ({len(circuits)} found)")
    table.add_column("ID", style="cyan", width=10)
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Simulations", style="blue", width=15)
    table.add_column("Netlist", style="dim")

    for circuit in circuits:
        circuit_id = circuit.get("id", "unknown")[:8]  # Truncate for display
        name = circuit.get("name", "Unknown")
        status = circuit.get("status", "unknown")

        # Count simulations
        simulations = circuit.get("simulations", [])
        sim_count = f"{len(simulations)} runs" if simulations else "None"

        # Get netlist path (show relative to current dir if possible)
        netlist_path = circuit.get("netlist_path", "")
        try:
            relative_path = Path(netlist_path).relative_to(Path.cwd())
            netlist_display = str(relative_path)
        except ValueError:
            netlist_display = Path(netlist_path).name

        # Add status emoji
        status_display = {
            "created": "📝 Created",
            "simulated": "✅ Simulated",
            "error": "❌ Error",
        }.get(status, f"🔄 {status}")

        table.add_row(circuit_id, name, status_display, sim_count, netlist_display)

    console.print(table)
    console.print(
        "\n💡 To simulate: [bold]circuit-sim simulate dc --circuit-id <ID>[/bold]"
    )


@click.command()
@click.argument("circuit_id")
def circuit_info(circuit_id: str):
    """Show detailed information about a specific circuit."""

    try:
        metadata = load_circuit_metadata(circuit_id)

        # Display detailed circuit information
        console.print("\n[bold cyan]Circuit Information[/bold cyan]")
        console.print(f"ID: [yellow]{metadata.get('id', 'Unknown')}[/yellow]")
        console.print(f"Name: [green]{metadata.get('name', 'Unknown')}[/green]")
        console.print(f"Status: [blue]{metadata.get('status', 'unknown')}[/blue]")
        console.print(f"Created: {metadata.get('created_at', 'Unknown')}")

        # Netlist information
        netlist_path = Path(metadata.get("netlist_path", ""))
        console.print("\n[bold]Netlist Information[/bold]")
        console.print(f"Path: {netlist_path}")

        if netlist_path.exists():
            console.print(f"Size: {netlist_path.stat().st_size} bytes")
            console.print("✅ File exists")
        else:
            console.print("❌ File not found")

        # Simulation history
        simulations = metadata.get("simulations", [])
        console.print(f"\n[bold]Simulation History[/bold] ({len(simulations)} runs)")

        if simulations:
            sim_table = Table()
            sim_table.add_column("Type", style="cyan")
            sim_table.add_column("Status", style="green")
            sim_table.add_column("Date", style="dim")

            for sim in simulations[-5:]:  # Show last 5
                sim_table.add_row(
                    sim.get("type", "unknown"),
                    sim.get("status", "unknown"),
                    sim.get("date", "unknown"),
                )

            console.print(sim_table)
        else:
            console.print("No simulations run yet")
            console.print(
                f"💡 Run simulation: [bold]circuit-sim simulate dc --circuit-id {circuit_id}[/bold]"
            )

    except UserError as e:
        print_error(e)
        raise click.ClickException(str(e))
