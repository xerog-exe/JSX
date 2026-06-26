"""Hardcoded credentials detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects hardcoded credentials in JavaScript."""

    def __init__(self):
        super().__init__("Hardcoded Credentials", severity="high")
        self.pattern = re.compile(
            r'(?:password|passwd|pwd|secret|client_secret|api_secret|token)\s*[:=]\s*["\']([^"\']{4,200})["\']',
            re.IGNORECASE
        )

    def run(self, content):
        """Find all hardcoded credentials."""
        findings = []
        seen = set()

        for match in self.pattern.finditer(content):
            value = match.group(1)
            if value in seen:
                continue
            seen.add(value)

            context = self._get_context(content, match.start())
            findings.append({
                "value": value,
                "context": context,
                "severity": "high"
            })

        return findings
