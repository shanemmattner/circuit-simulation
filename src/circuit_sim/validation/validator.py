"""
Main circuit validator that orchestrates multiple validation rules.
"""

from typing import Dict, List, Optional

from ..circuit import Circuit
from .base import ValidationResult, ValidationRule


class CircuitValidator:
    """Main validator that runs multiple validation rules."""

    def __init__(self):
        """Initialize validator with no rules."""
        self.rules: List[ValidationRule] = []

    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a validation rule.

        Args:
            rule: ValidationRule instance to add
        """
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a validation rule by name.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if rule was removed, False if not found
        """
        initial_count = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        return len(self.rules) < initial_count

    def validate(
        self, circuit: Circuit, rule_names: Optional[List[str]] = None
    ) -> Dict[str, ValidationResult]:
        """
        Validate circuit against all or specified rules.

        Args:
            circuit: Circuit to validate
            rule_names: Optional list of specific rule names to run

        Returns:
            Dictionary mapping rule names to their results
        """
        results = {}

        rules_to_run = self.rules
        if rule_names:
            rules_to_run = [rule for rule in self.rules if rule.name in rule_names]

        for rule in rules_to_run:
            try:
                result = rule.validate(circuit)
                results[rule.name] = result
            except Exception as e:
                # Create error result for failed validation
                from .base import Severity, ValidationIssue

                error_issue = ValidationIssue(
                    type="validation_error",
                    severity=Severity.ERROR,
                    message=f"Validation rule '{rule.name}' failed: {str(e)}",
                    components=[],
                )
                results[rule.name] = ValidationResult(
                    rule_name=rule.name,
                    is_valid=False,
                    issues=[error_issue],
                    warnings=[],
                    info=[],
                    suggestions=[],
                )

        return results

    def is_valid(
        self, circuit: Circuit, rule_names: Optional[List[str]] = None
    ) -> bool:
        """
        Check if circuit passes all validation rules.

        Args:
            circuit: Circuit to validate
            rule_names: Optional list of specific rule names to check

        Returns:
            True if all rules pass, False otherwise
        """
        results = self.validate(circuit, rule_names)
        return all(result.is_valid for result in results.values())

    def get_summary(self, results: Dict[str, ValidationResult]) -> Dict[str, int]:
        """
        Get summary statistics from validation results.

        Args:
            results: Results from validate() method

        Returns:
            Dictionary with summary statistics
        """
        total_errors = sum(len(result.issues) for result in results.values())
        total_warnings = sum(len(result.warnings) for result in results.values())
        total_info = sum(len(result.info) for result in results.values())
        rules_passed = sum(1 for result in results.values() if result.is_valid)

        return {
            "rules_run": len(results),
            "rules_passed": rules_passed,
            "rules_failed": len(results) - rules_passed,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "total_info": total_info,
            "overall_valid": total_errors == 0,
        }
