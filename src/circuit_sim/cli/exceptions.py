"""
CLI-specific exceptions with proper exit codes.

This module defines the error hierarchy for CLI operations.
"""

from typing import Optional


class CLIError(Exception):
    """
    Base exception for CLI errors.

    All CLI errors should inherit from this class to ensure
    proper error handling and exit codes.
    """

    exit_code = 1

    def __init__(self, message: str, suggestion: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion


class UserError(CLIError):
    """
    User input errors (exit code 1).

    These are errors caused by invalid user input or usage.
    """

    exit_code = 1


class SystemError(CLIError):
    """
    System-level errors (exit code 2).

    These are errors caused by system issues like missing dependencies
    or insufficient permissions.
    """

    exit_code = 2


class SimulationError(CLIError):
    """
    Simulation-specific errors (exit code 3).

    These are errors that occur during circuit simulation.
    """

    exit_code = 3


class FileNotFoundError(UserError):
    """Specific error for missing files."""

    def __init__(self, filepath: str) -> None:
        super().__init__(
            f"File not found: {filepath}",
            suggestion="Check that the file path is correct and the file exists",
        )


class InvalidNetlistError(UserError):
    """Specific error for invalid netlist files."""

    def __init__(self, filepath: str, line_number: Optional[int] = None) -> None:
        message = f"Invalid netlist file: {filepath}"
        if line_number:
            message += f" (line {line_number})"
        super().__init__(message, suggestion="Check the netlist syntax and component definitions")


class ConvergenceError(SimulationError):
    """Specific error for simulation convergence issues."""

    def __init__(self, circuit_name: str) -> None:
        super().__init__(
            f"Simulation failed to converge for circuit: {circuit_name}",
            suggestion="Check for floating nodes or unrealistic component values",
        )
