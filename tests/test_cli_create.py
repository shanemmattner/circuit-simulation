"""
Test CLI create command functionality.

Testing circuit creation from netlist files.
"""

import os
import tempfile
from pathlib import Path

from click.testing import CliRunner

from circuit_sim.cli.main import cli, register_commands

# Register commands for testing
register_commands()


class TestCreateCommand:
    """Test the create command for circuit creation."""

    def create_sample_netlist(self, path: Path, name: str = "RC Filter") -> Path:
        """Helper to create a sample netlist file for testing."""
        netlist_content = f"""* {name}
* Simple RC filter circuit

V1 1 0 DC 5V
R1 1 2 1k
C1 2 0 1u

.end
"""
        netlist_file = path / f"{name.lower().replace(' ', '_')}.cir"
        netlist_file.write_text(netlist_content)
        return netlist_file

    def test_create_command_from_netlist(self):
        """Test that create command works with valid netlist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create sample netlist
                netlist_file = self.create_sample_netlist(Path(temp_dir))

                runner = CliRunner()
                result = runner.invoke(
                    cli, ["create", "--netlist", str(netlist_file), "--name", "Test Circuit"]
                )

                assert result.exit_code == 0
                assert "created successfully" in result.output.lower()

            finally:
                os.chdir(original_cwd)

    def test_create_command_missing_netlist(self):
        """Test create command with missing netlist file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                runner = CliRunner()
                result = runner.invoke(
                    cli, ["create", "--netlist", "nonexistent.cir", "--name", "Test Circuit"]
                )

                assert result.exit_code == 2  # Click's path validation error
                assert "does not exist" in result.output.lower()

            finally:
                os.chdir(original_cwd)

    def test_create_command_invalid_netlist(self):
        """Test create command with invalid netlist syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create invalid netlist
                invalid_netlist = Path(temp_dir) / "invalid.cir"
                invalid_netlist.write_text("This is not a valid netlist\nRandom text\n")

                runner = CliRunner()
                result = runner.invoke(
                    cli, ["create", "--netlist", str(invalid_netlist), "--name", "Test Circuit"]
                )

                # Should handle gracefully, might warn but not crash
                assert result.exit_code in [0, 1]  # Success or user error

            finally:
                os.chdir(original_cwd)
