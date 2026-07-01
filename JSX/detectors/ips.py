"""IP address detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects IP addresses in JavaScript."""

    def __init__(self):
        super().__init__("IP Addresses", severity="low")
        self.pattern = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3})\b'
        )

    def run(self, content):
        """Find all IP addresses."""
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
