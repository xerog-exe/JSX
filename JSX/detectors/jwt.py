"""JWT token detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects JWT tokens in JavaScript."""

    def __init__(self):
        super().__init__("JWT Tokens", severity="high")
        self.pattern = re.compile(r'\beyJ[0-9A-Za-z\-_]+\.[0-9A-Za-z\-_]+\.[0-9A-Za-z\-_]+\b')

    def run(self, content):
        """Find all JWT tokens."""
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
                "severity": "high"
            })

        return findings
