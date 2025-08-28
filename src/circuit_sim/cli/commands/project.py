"""
Project management commands.

Commands for initializing and managing circuit simulation projects.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from circuit_sim import __version__
from circuit_sim.cli.utils.output import print_info, print_success, print_warning

console = Console()


@click.command()
@click.option(
    "--name", default=None, help="Project name (defaults to current directory name)"
)
@click.option("--force", is_flag=True, help="Overwrite existing project files")
def init(name: Optional[str], force: bool):
    """Initialize a new circuit simulation project."""
    current_dir = Path.cwd()
    project_name = name or current_dir.name

    config_file = current_dir / ".circuit-sim.yml"

    if config_file.exists() and not force:
        print_warning(f"Project already exists in {current_dir}")
        print_info("Use --force to overwrite existing configuration")
        return

    # Create project structure
    directories = ["circuits", "reports", "netlists", "results"]
    for dir_name in directories:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)

    # Create configuration file
    config_content = f"""# Circuit Simulation Project Configuration
project:
  name: {project_name}
  version: "1.0.0"
  description: "Circuit simulation project created with circuit-sim"

# Default simulation settings
simulation:
  default_analysis: "dc"
  timeout: 60  # seconds
  
# Output settings
output:
  format: "json"
  directory: "./results"
  
# Plotting settings
plots:
  theme: "plotly_white"
  width: 800
  height: 600
"""

    config_file.write_text(config_content)

    # Create example README
    readme_file = current_dir / "README.md"
    if not readme_file.exists():
        readme_content = f"""# {project_name}

Circuit simulation project created with [circuit-sim](https://github.com/circuit-synth/circuit-simulation).

## Project Structure

- `circuits/` - Circuit netlist files
- `netlists/` - SPICE netlist files  
- `results/` - Simulation results
- `reports/` - Generated reports and plots

## Quick Start

```bash
# Create a circuit from netlist
circuit-sim create --netlist netlists/example.cir

# Run DC analysis
circuit-sim simulate dc --circuit-id <id>

# Generate report
circuit-sim report --results results/simulation.json
```

## Configuration

Project settings are stored in `.circuit-sim.yml`. Modify as needed for your workflows.
"""
        readme_file.write_text(readme_content)

    print_success(f"Initialized circuit simulation project: {project_name}")
    console.print(f"  📁 Created directories: {', '.join(directories)}")
    console.print("  ⚙️  Created configuration: .circuit-sim.yml")
    if not readme_file.exists():
        console.print("  📄 Created README.md")


@click.command()
def info():
    """Show system and project information."""
    table = Table(title="Circuit Simulation Environment")
    table.add_column("Component", style="cyan")
    table.add_column("Version/Info", style="green")

    # Basic info
    table.add_row("circuit-sim", __version__)
    table.add_row(
        "Python",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    table.add_row("Platform", sys.platform)

    # Dependencies info
    try:
        import PySpice

        table.add_row("PySpice", getattr(PySpice, "__version__", "unknown"))
    except ImportError:
        table.add_row("PySpice", "[red]Not installed[/red]")

    try:
        import rich

        table.add_row("Rich", getattr(rich, "__version__", "unknown"))
    except ImportError:
        table.add_row("Rich", "[red]Not installed[/red]")

    try:
        import click

        table.add_row("Click", getattr(click, "__version__", "unknown"))
    except ImportError:
        table.add_row("Click", "[red]Not installed[/red]")

    # Project info if available
    config_file = Path.cwd() / ".circuit-sim.yml"
    if config_file.exists():
        table.add_row("Project", f"Found in {Path.cwd()}")
        try:
            import yaml

            with open(config_file) as f:
                config = yaml.safe_load(f)
                if "project" in config:
                    project_info = config["project"]
                    table.add_row("  Name", project_info.get("name", "Unknown"))
                    table.add_row("  Version", project_info.get("version", "Unknown"))
        except Exception:
            table.add_row(
                "  Status", "[yellow]Config file exists but cannot be read[/yellow]"
            )
    else:
        table.add_row("Project", "[yellow]No project detected[/yellow]")

    console.print(table)


# Commands will be registered by importing this module
