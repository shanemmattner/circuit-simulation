"""
Test CLI error handling functionality.

Testing the error handling framework and Rich output formatting.
"""

from click.testing import CliRunner

from circuit_sim.cli.exceptions import CLIError, SimulationError, SystemError, UserError
from circuit_sim.cli.main import cli


class TestCLIErrorHandling:
    """Test CLI error handling and colored output."""

    def test_user_error_exit_code(self):
        """Test that user errors return exit code 1."""
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent-command"])

        assert result.exit_code == 2  # Click default for unknown command

    def test_cli_error_hierarchy(self):
        """Test that error hierarchy is properly defined."""
        # Test base error
        error = CLIError("base error")
        assert str(error) == "base error"

        # Test user error
        user_error = UserError("user error")
        assert isinstance(user_error, CLIError)

        # Test system error
        system_error = SystemError("system error")
        assert isinstance(system_error, CLIError)

        # Test simulation error
        sim_error = SimulationError("simulation error")
        assert isinstance(sim_error, CLIError)

    def test_error_formatting(self):
        """Test that errors are formatted with Rich styling."""
        from circuit_sim.cli.utils.output import format_error

        error_msg = format_error("Test error message")
        assert "Test error message" in error_msg
        # Should contain Rich markup for red color
        assert "[red]" in error_msg or "❌" in error_msg
