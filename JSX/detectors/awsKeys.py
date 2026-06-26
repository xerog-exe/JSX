"""AWS access key detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects AWS access keys in JavaScript."""

    def __init__(self):
        super().__init__("AWS Access Keys", severity="high")
        self.pattern = re.compile(r'AKIA[0-9A-Z]{16}')

    def run(self, content):
        """Find all AWS access keys."""
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
                "severity": "high"
            })

        return findings
