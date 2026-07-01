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

        # Temporary map to deduplicate findings by (detector, value)
        dedupe_map = {}

        for detector in self.detectors:
            detector_name = detector.name
            grouped.setdefault(detector_name, [])

            try:
                findings = detector.run(content)
                if not findings or not isinstance(findings, list):
                    continue

                for finding in findings:
                    # Determine index/position if provided by detector
                    index = finding.get("index")
                    if index is None:
                        index = finding.get("pos") if finding.get("pos") is not None else 0

                    # Compute line number from content and index
                    line = None
                    try:
                        if isinstance(index, int) and index >= 0:
                            line = content[:index].count("\n") + 1
                    except Exception:
                        line = None

                    value = finding.get("value")
                    if value is None:
                        # Skip findings without a value to key on
                        continue

                    key = (detector_name, value)
                    entry = dedupe_map.get(key)
                    if entry:
                        # Increment occurrences and record unique line numbers
                        entry["occurrences"] += 1
                        if line and line not in entry["lines"]:
                            entry["lines"].append(line)
                        continue

                    # Build normalized finding record
                    record = {
                        "value": value,
                        "context": finding.get("context"),
                        "severity": finding.get("severity", detector.severity),
                        "detector": detector_name,
                        "occurrences": 1,
                        "lines": [line] if line else [],
                    }

                    # Simple confidence heuristic based on value length
                    conf = 50
                    try:
                        if isinstance(value, str):
                            length = len(value)
                            if length > 30:
                                conf = 95
                            elif length > 20:
                                conf = 85
                            elif length > 10:
                                conf = 70
                    except Exception:
                        conf = 50

                    record["confidence"] = conf

                    dedupe_map[key] = record
                    grouped[detector_name].append(record)
                    all_findings.append(record)
            except Exception:
                # Ignore detector errors
                pass

        return {"grouped": grouped, "all": all_findings}
