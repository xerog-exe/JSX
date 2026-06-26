"""Base detector class for all detectors to inherit from."""

from abc import ABC, abstractmethod


class BaseDetector(ABC):
    """Abstract base class for all detectors."""

    def __init__(self, name, severity="info"):
        """
        Initialize detector.

        Args:
            name: Human-readable name of detector category (e.g., "Email Addresses")
            severity: Default severity level (low, medium, high)
        """
        self.name = name
        self.severity = severity

    @abstractmethod
    def run(self, content):
        """
        Scan content and return findings.

        Args:
            content: JavaScript content as string

        Returns:
            List of findings, each a dict with 'value', 'context', and optionally 'severity'
        """
        pass

    def _get_context(self, content, index, length=120):
        """Helper to extract context around a finding."""
        start = max(0, index - 40)
        end = min(len(content), index + length)
        context = content[start:end].replace("\n", " ")
        return context
