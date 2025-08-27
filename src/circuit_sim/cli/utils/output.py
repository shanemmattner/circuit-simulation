"""
Output formatting utilities using Rich.

This module provides functions for consistent CLI output formatting.
"""

from typing import Optional

from rich.console import Console

from circuit_sim.cli.exceptions import CLIError

console = Console()


def format_error(message: str, suggestion: Optional[str] = None) -> str:
    """
    Format an error message with Rich styling.

    Args:
        message: The error message to format
        suggestion: Optional suggestion for fixing the error

    Returns:
        Formatted error string with Rich markup
    """
    formatted = f"[red]❌ Error:[/red] {message}"

    if suggestion:
        formatted += f"\n[yellow]💡 Suggestion:[/yellow] {suggestion}"

    return formatted


def print_error(error: CLIError) -> None:
    """
    Print a CLI error with Rich formatting.

    Args:
        error: The CLI error to print
    """
    formatted = format_error(error.message, error.suggestion)
    console.print(formatted)


def print_success(message: str) -> None:
    """
    Print a success message with Rich formatting.

    Args:
        message: The success message to print
    """
    console.print(f"[green]✅[/green] {message}")


def print_warning(message: str) -> None:
    """
    Print a warning message with Rich formatting.

    Args:
        message: The warning message to print
    """
    console.print(f"[yellow]⚠️[/yellow] {message}")


def print_info(message: str) -> None:
    """
    Print an informational message with Rich formatting.

    Args:
        message: The info message to print
    """
    console.print(f"[blue]ℹ️[/blue] {message}")
