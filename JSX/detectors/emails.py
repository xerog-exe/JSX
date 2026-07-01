"""Email address detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects email addresses in JavaScript."""

    def __init__(self):
        super().__init__("Email Addresses", severity="low")
        self.pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

    def run(self, content):
        """Find all email addresses."""
        findings = []
        seen = set()

        for match in self.pattern.finditer(content):
            value = match.group(0)
            if value in seen:
                continue
            seen.add(value)

            context = self._get_context(content, match.start())
            findings.append({
                "value": value,
                "context": context,
                "pos": match.start(),
                "severity": "low"
            })

        return findings
