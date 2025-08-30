"""
Circuit-synth parser for JSON format integration.

Integrates circuit-synth JSON format into the established parser architecture,
following the same patterns as KiCad and SPICE parsers.
"""

import json
import logging
from typing import Any, Dict

from .import_result import ImportResult
from ..models.circuit_synth_importer import CircuitSynthImporter

logger = logging.getLogger(__name__)


class CircuitSynthParser:
    """Parse circuit-synth JSON format following established parser patterns."""

    def __init__(self):
        self.importer = CircuitSynthImporter()

    def parse_file(self, file_path: str) -> ImportResult:
        """Parse circuit-synth JSON file.

        Args:
            file_path: Path to circuit-synth JSON file

        Returns:
            ImportResult with circuit and any warnings/errors
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.parse_content(content)
        except FileNotFoundError:
            logger.error(f"Circuit-synth file not found: {file_path}")
            result = ImportResult()
            result.parsing_errors.append(f"File not found: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Failed to read circuit-synth file {file_path}: {e}")
            result = ImportResult()
            result.parsing_errors.append(f"Failed to read file: {e}")
            return result

    def parse_content(self, content: str) -> ImportResult:
        """Parse circuit-synth JSON content.

        Args:
            content: Circuit-synth JSON content as string

        Returns:
            ImportResult with parsed circuit
        """
        try:
            # Parse JSON content
            data = json.loads(content)

            # Validate basic structure
            if not isinstance(data, dict):
                result = ImportResult()
                result.parsing_errors.append(
                    "Invalid circuit-synth format: expected JSON object"
                )
                return result

            # Use enhanced importer
            result = self.importer.import_from_dict(data)

            if result.is_successful:
                logger.info(f"Successfully parsed circuit-synth: {result.circuit.name}")
            else:
                logger.error(
                    f"Circuit-synth parsing had critical errors: {result.parsing_errors}"
                )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in circuit-synth content: {e}")
            result = ImportResult()
            result.parsing_errors.append(f"Invalid JSON format: {e}")
            return result
        except Exception as e:
            logger.error(f"Unexpected error parsing circuit-synth: {e}")
            result = ImportResult()
            result.parsing_errors.append(f"Parser error: {e}")
            return result

    def parse_dict(self, data: Dict[str, Any]) -> ImportResult:
        """Parse circuit-synth data from dictionary.

        Args:
            data: Circuit-synth data as dictionary

        Returns:
            ImportResult with parsed circuit
        """
        return self.importer.import_from_dict(data)

    @classmethod
    def can_parse(cls, content: str) -> bool:
        """Check if content appears to be circuit-synth JSON format.

        Args:
            content: Content to check

        Returns:
            True if content appears to be circuit-synth format
        """
        try:
            data = json.loads(content.strip())
            if not isinstance(data, dict):
                return False

            # Look for circuit-synth indicators
            indicators = [
                "components" in data,
                "nets" in data,
                any(key in data for key in ["name", "description"]),
                # Check for circuit-synth component format
                any(
                    isinstance(comp, dict) and "symbol" in comp
                    for comp in data.get("components", {}).values()
                ),
            ]

            # Must have at least 2 indicators
            return sum(indicators) >= 2

        except (json.JSONDecodeError, AttributeError):
            return False

    @classmethod
    def get_format_name(cls) -> str:
        """Get parser format name."""
        return "circuit-synth-json"

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".json", ".circuit-synth"]
