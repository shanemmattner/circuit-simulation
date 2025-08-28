"""
Base classes for circuit validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..circuit import Circuit


class Severity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a circuit."""

    type: str
    severity: Severity
    message: str
    components: List[str]
    nodes: Optional[List[int]] = None
    suggestion: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class ValidationResult:
    """Result of circuit validation."""

    rule_name: str
    is_valid: bool
    issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    suggestions: List[str]
    metadata: Optional[dict] = None

    def __post_init__(self):
        """Organize issues by severity."""
        # Separate issues by severity if not already done
        if not self.warnings and not self.info:
            self.warnings = [
                issue for issue in self.issues if issue.severity == Severity.WARNING
            ]
            self.info = [
                issue for issue in self.issues if issue.severity == Severity.INFO
            ]
            # Keep only errors in issues
            self.issues = [
                issue for issue in self.issues if issue.severity == Severity.ERROR
            ]

    @property
    def has_errors(self) -> bool:
        """Check if result has any errors."""
        return len(self.issues) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if result has any warnings."""
        return len(self.warnings) > 0

    @property
    def total_issues(self) -> int:
        """Get total count of all issues."""
        return len(self.issues) + len(self.warnings) + len(self.info)


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, name: Optional[str] = None):
        """
        Initialize validation rule.

        Args:
            name: Optional custom name for the rule
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def validate(self, circuit: Circuit) -> ValidationResult:
        """
        Validate a circuit against this rule.

        Args:
            circuit: Circuit to validate

        Returns:
            ValidationResult with any issues found
        """
        pass

    def _create_result(
        self,
        is_valid: bool = True,
        issues: Optional[List[ValidationIssue]] = None,
        metadata: Optional[dict] = None,
    ) -> ValidationResult:
        """
        Helper to create validation result.

        Args:
            is_valid: Whether validation passed
            issues: List of issues found
            metadata: Optional metadata

        Returns:
            ValidationResult instance
        """
        issues = issues or []
        suggestions = []

        # Extract suggestions from issues
        for issue in issues:
            if issue.suggestion:
                suggestions.append(issue.suggestion)

        return ValidationResult(
            rule_name=self.name,
            is_valid=is_valid,
            issues=issues,
            warnings=[],
            info=[],
            suggestions=suggestions,
            metadata=metadata,
        )

    def _create_issue(
        self,
        issue_type: str,
        severity: Severity,
        message: str,
        components: List[str],
        nodes: Optional[List[int]] = None,
        suggestion: Optional[str] = None,
        **metadata
    ) -> ValidationIssue:
        """
        Helper to create validation issue.

        Args:
            issue_type: Type of issue (e.g., "short_circuit")
            severity: Severity level
            message: Human-readable message
            components: List of component names involved
            nodes: Optional list of node numbers involved
            suggestion: Optional suggestion to fix the issue
            **metadata: Additional metadata

        Returns:
            ValidationIssue instance
        """
        return ValidationIssue(
            type=issue_type,
            severity=severity,
            message=message,
            components=components,
            nodes=nodes,
            suggestion=suggestion,
            metadata=metadata if metadata else None,
        )
