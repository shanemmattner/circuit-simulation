"""
Test CLI functionality.

Testing the command-line interface components following TDD approach.
"""

from click.testing import CliRunner

from circuit_sim.cli.main import cli


class TestCLIFoundation:
    """Test basic CLI setup and functionality."""

    def test_cli_help_command(self):
        """Test that --help shows available commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "circuit simulation cli" in result.output.lower()
        assert "professional circuit analysis" in result.output.lower()

    def test_cli_version_command(self):
        """Test that --version shows version info."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_app_context(self):
        """Test that CLI app can be created without errors."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # Should show help when no command given
        assert result.exit_code == 0
