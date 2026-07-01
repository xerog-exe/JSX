"""Authorization token detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects authorization tokens in JavaScript."""

    def __init__(self):
        super().__init__("Authorization Tokens", severity="high")
        self.bearer_pattern = re.compile(r'Bearer\s+([A-Za-z0-9\-_.=/]+)')
        self.auth_pattern = re.compile(r'authorization\s*["\']?\s*[:=]\s*["\']([^"\']{8,200})["\']', re.IGNORECASE)

    def run(self, content):
        """Find all authorization tokens."""
        findings = []
        seen = set()

        # Look for Bearer tokens
        for match in self.bearer_pattern.finditer(content):
            # capture the token part (group 1)
            value = match.group(1)
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

        # Look for authorization header assignments
        for match in self.auth_pattern.finditer(content):
            value = match.group(1)
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
