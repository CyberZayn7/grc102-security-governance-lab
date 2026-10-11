#!/usr/bin/env python3
"""Apply control records and verify the running secure Docker configuration."""
from __future__ import annotations

import argparse
import json
import secrets
import subprocess

from governance_tracker import GovernanceTracker
from lab_utils import EVIDENCE, ROOT, docker_networks, load_json, now, run, save_json
from patch_management import PATCHES, apply as apply_patch_record
from vulnerability_scanner import struts_check


def ensure_env():
    path = ROOT / ".env"
    if path.exists():
        return
    path.write_text(
        "BASELINE_DB_ROOT_PASSWORD=password\nBASELINE_DB_PASSWORD=app_password\n"
        f"SECURE_DB_ROOT_PASSWORD={secrets.token_urlsafe(24)}\n"
        f"SECURE_DB_PASSWORD={secrets.token_urlsafe(24)}\n",
        encoding="utf-8",
    )


def apply_controls():
    ensure_env()
    for patch_id in PATCHES:
        apply_patch_record(patch_id)
    tracker = GovernanceTracker()
    tracker.initialize()
    existing = {item["name"] for item in tracker.data["controls"]}
    controls = [
        ("Critical patch verification", "Application Owner", "POL-001"),
        ("Frontend/data network segmentation", "Network Owner", "POL-002"),
        ("Least-privilege database authentication", "Database Owner", "POL-002"),
        ("Critical service monitoring", "Security Operations", "POL-002"),
        ("Executive security oversight", "CEO", "POL-001"),
    ]
    for name, owner, policy in controls:
        if name not in existing:
            tracker.add("control", {"name": name, "owner": owner, "policy_id": policy, "status": "Implemented", "implemented_at": now(), "review_date": "2027-01-31"})
    print("Five governance control categories recorded.")
    print("Next: stop the baseline and start docker-compose.secure.yml, then run --verify.")


def verify() -> dict:
    web_networks = docker_networks("web_server")
    db_networks = docker_networks("database_server")
    struts = struts_check("http://127.0.0.1:8080/")
    old_password = run(["docker", "exec", "database_server", "mysql", "-uroot", "-ppassword", "-Nse", "SELECT 1"], timeout=15)
    monitor = run(["python3", "monitoring/security_monitor.py"])
    tracker = GovernanceTracker()
    expected = {
        "Critical patch verification", "Frontend/data network segmentation",
        "Least-privilege database authentication", "Critical service monitoring",
        "Executive security oversight",
    }
    owned = {c["name"] for c in tracker.data["controls"] if c.get("owner") and c.get("review_date")}
    tests = [
        {"control": "Patch management", "passed": struts["vulnerable"] is False, "evidence": struts["evidence"]},
        {"control": "Database authentication", "passed": old_password.returncode != 0, "evidence": "Former root/password credential rejected" if old_password.returncode else "Former credential still accepted"},
        {"control": "Network segmentation", "passed": bool(web_networks and db_networks and not web_networks & db_networks), "evidence": f"web={sorted(web_networks)}; database={sorted(db_networks)}"},
        {"control": "Monitoring", "passed": monitor.returncode == 0 and (EVIDENCE / "post-control" / "monitoring_snapshot.txt").exists(), "evidence": monitor.stdout.strip() or monitor.stderr.strip()},
        {"control": "Governance oversight", "passed": expected <= owned, "evidence": f"{len(expected & owned)}/{len(expected)} controls have owners and review dates"},
    ]
    report = {"verified_at": now(), "authorised_scope": "Local Docker lab only", "tests": tests, "passed": sum(t["passed"] for t in tests), "total": len(tests)}
    save_json(EVIDENCE / "post-control" / "controls_verification.json", report)
    rows = "\n".join(f"| {t['control']} | {'PASS' if t['passed'] else 'FAIL'} | {t['evidence']} |" for t in tests)
    (ROOT / "controls_report.md").write_text(f"""# Governance Controls Verification Report

Generated: {report['verified_at']}

| Control | Result | Evidence |
|---|---|---|
{rows}

## Conclusion

{report['passed']} of {report['total']} control categories passed direct verification. Failed tests must be remediated and rerun before the report is submitted.
""", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--apply", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply_controls()
    else:
        report = verify()
        print(json.dumps({"passed": report["passed"], "total": report["total"]}, indent=2))
        raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()

