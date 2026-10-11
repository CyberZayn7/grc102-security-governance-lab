#!/usr/bin/env python3
"""Convert saved technical evidence into a governance failure register."""
from __future__ import annotations

import argparse
import json

from lab_utils import EVIDENCE, ROOT, latest, load_json, now, save_json, stamp

MAPPING = {
    "CVE-2017-5638": ("Patch and Vulnerability Management", "Known critical weakness remained exposed", "Application Owner", "Replace the component and enforce a seven-day critical patch SLA"),
    "DB-AUTH-001": ("Authentication and Access Control", "Default database credentials permit unauthorised access", "Database Owner", "Use unique secrets and least-privilege accounts"),
    "NET-SEG-001": ("Security Architecture", "A shared network enables lateral movement", "Network Owner", "Separate frontend and data networks"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    scan_path = latest("evidence/baseline/vulnerability_report_*.json")
    if not scan_path:
        raise SystemExit("Run vulnerability_scanner.py --mode baseline first")
    scan = load_json(scan_path, {})
    failures = []
    for finding in scan.get("findings", []):
        if finding.get("vulnerable") and finding["id"] in MAPPING:
            category, impact, owner, recommendation = MAPPING[finding["id"]]
            failures.append({"category": category, "finding_id": finding["id"], "failure": finding["title"], "impact": impact, "accountable_owner": owner, "recommendation": recommendation})
    failures.extend([
        {"category": "Monitoring and Detection", "finding_id": "GOV-MON-001", "failure": "No effective baseline alerting", "impact": "Malicious activity may remain undetected", "accountable_owner": "Security Operations", "recommendation": "Monitor critical services and escalate alerts"},
        {"category": "Policy Enforcement", "finding_id": "GOV-POL-001", "failure": "Policies exist without verified implementation", "impact": "Documented intent does not reduce technical risk", "accountable_owner": "CISO", "recommendation": "Require evidence-backed control attestations"},
        {"category": "Metrics and Accountability", "finding_id": "GOV-MET-001", "failure": "Metrics are not tied to remediation decisions", "impact": "Overdue high-risk work may not be escalated", "accountable_owner": "Executive Risk Committee", "recommendation": "Assign thresholds, owners, deadlines, and escalation rules"},
    ])
    report = {"generated_at": now(), "source": str(scan_path.relative_to(ROOT)), "total_failures": len(failures), "failures": failures}
    path = save_json(EVIDENCE / "baseline" / f"governance_failure_report_{stamp()}.json", report)
    print(json.dumps({"total_failures": len(failures), "report": str(path.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()

