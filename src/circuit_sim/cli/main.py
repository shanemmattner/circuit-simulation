"""
Main CLI application entry point.

Defines the primary CLI interface using Click framework.
"""

import sys

import click
from rich.console import Console

from circuit_sim import __version__
from circuit_sim.cli.exceptions import CLIError
from circuit_sim.cli.utils.output import print_error

console = Console()


# Register commands after CLI definition
def register_commands():
    """Register all CLI commands."""
    from circuit_sim.cli.commands.create import create
    from circuit_sim.cli.commands.list_circuits import circuit_info, list_circuits
    from circuit_sim.cli.commands.project import info, init
    from circuit_sim.cli.commands.simulate import simulate

    cli.add_command(init)
    cli.add_command(info)
    cli.add_command(create)
    cli.add_command(simulate)
    cli.add_command(list_circuits, name="list")
    cli.add_command(circuit_info, name="show")


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """Circuit Simulation CLI - Professional circuit analysis tool."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def main():
    """Entry point for the CLI application."""
    # Register commands
    register_commands()

    try:
        cli()
    except CLIError as error:
        print_error(error)
        sys.exit(error.exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as error:
        console.print(f"[red]❌ Unexpected error:[/red] {error}")
        sys.exit(2)
