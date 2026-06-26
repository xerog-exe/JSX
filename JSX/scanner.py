"""Core scanner that loads and runs detector modules."""

import os
import sys
import importlib
from pathlib import Path


class Scanner:
    """Scanner that dynamically loads detectors and scans content."""

    def __init__(self):
        self.detectors = []
        self._load_detectors()

    def _load_detectors(self):
        """Dynamically load all detector modules from detectors/."""
        detectors_dir = Path(__file__).parent / "detectors"

        # Find all .py files in detectors directory (except __init__.py and base.py)
        for file in detectors_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue

            module_name = file.stem
            try:
                # Dynamically import the detector module using relative import
                # Get the package name dynamically
                module = importlib.import_module(f".detectors.{module_name}", package="JSX")

                # Look for a detector class in the module
                if hasattr(module, "Detector"):
                    self.detectors.append(module.Detector())
            except Exception as e:
                # Silently ignore faulty detectors
                pass

    def scan(self, content):
        """
        Scan content with all loaded detectors.

        Args:
            content: JavaScript content as string

        Returns:
            Dictionary with keys as detector names, values as lists of findings.
            Also returns 'all' key with all findings flattened.
        """
        grouped = {}
        all_findings = []

        for detector in self.detectors:
            detector_name = detector.name
            grouped[detector_name] = []

            try:
                findings = detector.run(content)
                if findings and isinstance(findings, list):
                    for finding in findings:
                        finding["detector"] = detector_name
                        finding["severity"] = finding.get("severity", detector.severity)
                        grouped[detector_name].append(finding)
                        all_findings.append(finding)
            except Exception:
                # Ignore detector errors
                pass

        return {
            "grouped": grouped,
            "all": all_findings
        }
