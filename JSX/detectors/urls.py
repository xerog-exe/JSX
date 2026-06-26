"""URL detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects URLs in JavaScript."""

    def __init__(self):
        super().__init__("URLs", severity="low")
        self.pattern = re.compile(r'https?://[\w\-\.\/:?=&%#\+~,]+')

    def run(self, content):
        """Find all URLs."""
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
                "severity": "low"
            })

        return findings
