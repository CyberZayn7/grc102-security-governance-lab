#!/usr/bin/env python3
"""Minimal JSON-backed governance register and dashboard."""
from __future__ import annotations

import argparse
import html
from pathlib import Path

from lab_utils import ROOT, human_now, load_json, now, save_json

DATA = ROOT / "governance_data.json"


class GovernanceTracker:
    def __init__(self, path: Path = DATA):
        self.path = path
        self.data = load_json(path, {"policies": [], "controls": [], "risks": [], "incidents": [], "metrics": [], "audits": []})

    def save(self):
        save_json(self.path, self.data)

    def add(self, kind: str, item: dict) -> str:
        key = {"policy": "policies", "control": "controls", "risk": "risks", "incident": "incidents", "metric": "metrics", "audit": "audits"}[kind]
        prefix = {"policy": "POL", "control": "CTL", "risk": "RISK", "incident": "INC", "metric": "MET", "audit": "AUD"}[kind]
        item = {"id": f"{prefix}-{len(self.data[key]) + 1:03d}", **item}
        self.data[key].append(item)
        self.save()
        return item["id"]

    def initialize(self):
        if any(self.data.values()):
            return
        self.add("policy", {"name": "Critical Patch Management", "owner": "CISO", "status": "Active", "review_date": "2026-12-31"})
        self.add("policy", {"name": "Vulnerability Management", "owner": "Security Manager", "status": "Active", "review_date": "2026-12-31"})
        self.add("control", {"name": "Monthly vulnerability scan", "owner": "Security Engineer", "status": "Partially Implemented", "policy_id": "POL-002"})
        self.add("risk", {"name": "Unpatched internet-facing component", "owner": "Application Owner", "likelihood": "High", "impact": "High", "risk_level": "Critical", "status": "Open"})
        self.add("incident", {"name": "Simulated web compromise", "owner": "Incident Manager", "severity": "High", "status": "Open", "date": now()})
        self.add("metric", {"name": "Critical Patch Compliance", "owner": "CISO", "target": 95, "actual": 67, "status": "Below Target"})
        self.add("audit", {"name": "Security Governance Review", "owner": "Internal Audit", "status": "Completed", "finding": "Patch and segmentation controls require improvement"})

    def dashboard(self, output: Path = ROOT / "governance_dashboard.html") -> Path:
        cards = "".join(f"<article><b>{len(items)}</b><span>{html.escape(key.title())}</span></article>" for key, items in self.data.items())
        rows = "".join(
            f"<tr><td>{html.escape(r['id'])}</td><td>{html.escape(r['name'])}</td><td>{html.escape(r['risk_level'])}</td><td>{html.escape(r['owner'])}</td><td>{html.escape(r['status'])}</td></tr>"
            for r in self.data["risks"]
        )
        output.write_text(f"""<!doctype html><html lang=en><meta charset=utf-8><title>Governance Dashboard</title>
<style>body{{font:16px system-ui;margin:40px;background:#f4f7fb;color:#17324d}}section{{display:flex;gap:12px;flex-wrap:wrap}}article{{background:white;padding:20px;border-radius:10px;min-width:120px;box-shadow:0 2px 8px #ccd}}article b{{font-size:30px;display:block}}article span{{color:#52677c}}table{{margin-top:24px;background:white;border-collapse:collapse;width:100%}}th,td{{padding:12px;border-bottom:1px solid #dde4ea;text-align:left}}</style>
<h1>Security Governance Baseline</h1><p>Generated {html.escape(human_now())}</p><section>{cards}</section><h2>Open Risks</h2><table><tr><th>ID</th><th>Risk</th><th>Level</th><th>Owner</th><th>Status</th></tr>{rows}</table></html>""", encoding="utf-8")
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()
    tracker = GovernanceTracker()
    if args.initialize:
        tracker.initialize()
        print(f"Governance register initialized: {tracker.path.name}")
    if args.dashboard:
        print(f"Dashboard generated: {tracker.dashboard().name}")
    if not (args.initialize or args.dashboard):
        parser.print_help()


if __name__ == "__main__":
    main()

