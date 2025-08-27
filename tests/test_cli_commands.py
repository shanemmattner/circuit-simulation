"""
Test CLI command implementations.

Testing individual commands like init, version, etc.
"""

import os
import tempfile
from pathlib import Path

from click.testing import CliRunner

from circuit_sim.cli.main import cli, register_commands

# Register commands for testing
register_commands()


class TestInitCommand:
    """Test the init command for project initialization."""

    def test_init_command_creates_project_structure(self):
        """Test that init command creates proper project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory for the test
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()
                result = runner.invoke(cli, ["init"])

                assert result.exit_code == 0

                # Check that project files are created
                project_path = Path(temp_dir)
                assert (project_path / ".circuit-sim.yml").exists()
                assert (project_path / "circuits").exists()
                assert (project_path / "reports").exists()
            finally:
                os.chdir(original_cwd)

    def test_init_command_with_existing_project(self):
        """Test that init command handles existing project gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing config file
            config_path = Path(temp_dir) / ".circuit-sim.yml"
            config_path.write_text("existing: true")

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                runner = CliRunner()
                result = runner.invoke(cli, ["init"])

                # Should ask for confirmation or skip
                assert result.exit_code == 0
                assert "already exists" in result.output.lower()
            finally:
                os.chdir(original_cwd)


class TestVersionCommand:
    """Test the version command functionality."""

    def test_version_command_shows_version(self):
        """Test that version command shows proper version info."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_info_command_shows_system_info(self):
        """Test that info command shows system information."""
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        # Should show Python version, platform, dependencies
        assert "python" in result.output.lower()
        assert "circuit-sim" in result.output.lower()
