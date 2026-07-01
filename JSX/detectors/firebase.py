"""Firebase configuration detector."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects Firebase configuration in JavaScript."""

    def __init__(self):
        super().__init__("Firebase Config", severity="high")
        self.api_key_pattern = re.compile(r'apiKey\s*[:=]\s*["\']?(AIza[0-9A-Za-z\-_]{35})["\']?', re.IGNORECASE)
        self.config_pattern = re.compile(r'firebase(?:Config)?\s*[:=]\s*\{([\s\S]{0,800}?)};', re.IGNORECASE)

    def run(self, content):
        """Find Firebase configuration."""
        findings = []

        for match in self.api_key_pattern.finditer(content):
            value = match.group(1)
            context = self._get_context(content, match.start())
            findings.append({
                "value": value,
                "context": context,
                "pos": match.start(),
                "severity": "high"
            })

        for match in self.config_pattern.finditer(content):
            snippet = match.group(0).replace("\n", " ")
            findings.append({
                "value": "firebaseConfig",
                "context": snippet[:200],
                "pos": match.start(),
                "severity": "high"
            })

        return findings
