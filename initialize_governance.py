#!/usr/bin/env python3
from governance_tracker import GovernanceTracker

tracker = GovernanceTracker()
tracker.initialize()
print(f"Governance tracker initialized: {tracker.path.name}")
print(f"Governance dashboard generated: {tracker.dashboard().name}")

