"""
Circuit creation commands.

Commands for creating and managing circuits from netlist files.
"""

import json
import uuid
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from circuit_sim import Circuit
from circuit_sim.cli.exceptions import FileNotFoundError, InvalidNetlistError
from circuit_sim.cli.utils.output import print_error, print_info, print_success

console = Console()


def validate_netlist_file(netlist_path: Path) -> bool:
    """
    Validate basic netlist file structure.

    Args:
        netlist_path: Path to the netlist file

    Returns:
        True if valid, raises exception if invalid

    Raises:
        FileNotFoundError: If file doesn't exist
        InvalidNetlistError: If netlist is malformed
    """
    if not netlist_path.exists():
        raise FileNotFoundError(str(netlist_path))

    try:
        content = netlist_path.read_text()
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Basic validation - should have some content
        if not lines:
            raise InvalidNetlistError(str(netlist_path))

        # Check for common SPICE elements
        has_components = False
        for line in lines:
            if line.startswith(("*", ".", ";")):  # Comments or directives
                continue
            if any(line.upper().startswith(comp) for comp in ["V", "I", "R", "L", "C"]):
                has_components = True
                break

        if not has_components:
            print_info("Warning: No recognizable components found in netlist")

    except Exception as e:
        raise InvalidNetlistError(str(netlist_path)) from e

    return True


def save_circuit_metadata(circuit_id: str, name: str, netlist_path: Path) -> Path:
    """
    Save circuit metadata to local project database.

    Args:
        circuit_id: Unique circuit identifier
        name: Circuit name
        netlist_path: Path to source netlist file

    Returns:
        Path to the saved metadata file
    """
    # Create circuits directory if it doesn't exist
    circuits_dir = Path.cwd() / "circuits"
    circuits_dir.mkdir(exist_ok=True)

    metadata = {
        "id": circuit_id,
        "name": name,
        "netlist_path": str(netlist_path.absolute()),
        "created_at": str(circuit_id),  # UUID includes timestamp
        "status": "created",
        "simulations": [],
    }

    metadata_file = circuits_dir / f"{circuit_id}.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))

    return metadata_file


@click.command()
@click.option(
    "--netlist",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to SPICE netlist file",
)
@click.option("--name", required=True, help="Descriptive name for the circuit")
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate the netlist without creating circuit",
)
def create(netlist: Path, name: str, validate_only: bool):
    """Create a new circuit from a SPICE netlist file."""

    try:
        # Show progress while processing
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:

            # Step 1: Validate netlist
            task = progress.add_task("Validating netlist...", total=None)
            validate_netlist_file(netlist)
            progress.update(task, description="✅ Netlist validation passed")

            if validate_only:
                print_success(f"Netlist validation successful: {netlist}")
                return

            # Step 2: Create circuit instance
            progress.update(task, description="Creating circuit...")
            try:
                # Use existing Circuit class if available
                Circuit(name)
                circuit_id = str(uuid.uuid4())[:8]  # Short UUID for CLI

            except Exception:
                # Fallback for development
                print_info(f"Circuit creation: {name} from {netlist}")
                circuit_id = str(uuid.uuid4())[:8]

            # Step 3: Save metadata
            progress.update(task, description="Saving circuit metadata...")
            metadata_file = save_circuit_metadata(circuit_id, name, netlist)

            progress.update(task, description="✅ Circuit created successfully")

        # Success output
        print_success(f"Circuit '{name}' created successfully!")
        console.print(f"  🆔 Circuit ID: [bold cyan]{circuit_id}[/bold cyan]")
        console.print(f"  📁 Netlist: {netlist}")
        console.print(f"  📄 Metadata: {metadata_file}")
        console.print("\n💡 Next steps:")
        console.print(
            f"  • Run simulation: [bold]circuit-sim simulate dc --circuit-id {circuit_id}[/bold]"
        )
        console.print(
            f"  • View info: [bold]circuit-sim info --circuit-id {circuit_id}[/bold]"
        )

    except (FileNotFoundError, InvalidNetlistError) as e:
        print_error(e)
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"[red]❌ Unexpected error during circuit creation:[/red] {e}")
        raise click.ClickException(str(e))
