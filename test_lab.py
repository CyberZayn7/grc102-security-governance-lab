#!/usr/bin/env python3
"""Small standard-library checks for the report plumbing."""
import tempfile
import unittest
from pathlib import Path

from governance_metrics import bar_chart
from governance_tracker import GovernanceTracker


class LabTest(unittest.TestCase):
    def test_register_and_png(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = GovernanceTracker(root / "governance.json")
            tracker.add("policy", {"name": "Test", "owner": "Owner"})
            self.assertEqual(tracker.data["policies"][0]["id"], "POL-001")
            image = root / "chart.png"
            bar_chart(image, 20, 90, 100)
            self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()

