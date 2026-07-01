"""Google API key detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects Google API keys in JavaScript."""

    def __init__(self):
        super().__init__("Google API Keys", severity="high")
        self.pattern = re.compile(r'AIza[0-9A-Za-z\-_]{35}')

    def run(self, content):
        """Find all Google API keys."""
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
