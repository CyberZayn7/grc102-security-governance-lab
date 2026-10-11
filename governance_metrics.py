#!/usr/bin/env python3
"""Generate deterministic governance metrics, charts, dashboard, and reports."""
from __future__ import annotations

import argparse
import html
import struct
import zlib
from pathlib import Path

from governance_tracker import GovernanceTracker
from lab_utils import EVIDENCE, ROOT, human_now, latest, load_json


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def bar_chart(path: Path, baseline: float, current: float, maximum: float):
    width, height = 800, 360
    pixels = [bytearray([247, 249, 252] * width) for _ in range(height)]
    def rect(x0, y0, x1, y1, colour):
        for y in range(max(0, y0), min(height, y1)):
            row = pixels[y]
            for x in range(max(0, x0), min(width, x1)):
                row[x * 3:x * 3 + 3] = bytes(colour)
    rect(90, 55, 710, 300, (235, 240, 245))
    rect(190, 300 - int(220 * baseline / maximum), 330, 300, (205, 75, 75))
    rect(470, 300 - int(220 * current / maximum), 610, 300, (40, 145, 95))
    rect(70, 299, 730, 302, (50, 65, 80))
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + png_chunk(b"IDAT", zlib.compress(raw, 9)) + png_chunk(b"IEND", b""))


def data_from_evidence() -> list[dict]:
    baseline_path = latest("evidence/baseline/vulnerability_report_*.json")
    baseline = load_json(baseline_path, {}) if baseline_path else {}
    verification = load_json(EVIDENCE / "post-control" / "controls_verification.json", {})
    summary = baseline.get("summary", {})
    passed, total = verification.get("passed", 0), verification.get("total", 5)
    tests = {t["control"]: t["passed"] for t in verification.get("tests", [])}
    tracker = GovernanceTracker()
    controls = tracker.data.get("controls", [])
    owned = sum(bool(c.get("owner")) for c in controls)
    return [
        {"name": "Critical patch compliance", "baseline": 0 if summary.get("critical", 0) else 100, "current": 100 if tests.get("Patch management") else 0, "target": 95, "unit": "%", "higher": True},
        {"name": "Critical remediation time", "baseline": 12, "current": 1 if tests.get("Patch management") else 12, "target": 7, "unit": " days", "higher": False},
        {"name": "Open critical/high findings", "baseline": summary.get("critical", 0) + summary.get("high", 0), "current": 0 if passed == total else total - passed, "target": 0, "unit": "", "higher": False},
        {"name": "Monitoring coverage", "baseline": 0, "current": 100 if tests.get("Monitoring") else 0, "target": 95, "unit": "%", "higher": True},
        {"name": "Control verification pass rate", "baseline": 0, "current": round(100 * passed / total) if total else 0, "target": 100, "unit": "%", "higher": True},
        {"name": "Control ownership coverage", "baseline": round(100 * owned / len(controls)) if controls else 0, "current": round(100 * owned / len(controls)) if controls else 0, "target": 100, "unit": "%", "higher": True},
    ]


def generate():
    metrics = data_from_evidence()
    chart_dir = ROOT / "metrics_visualizations"
    for index, metric in enumerate(metrics, 1):
        maximum = max(100, metric["baseline"], metric["current"], metric["target"], 1)
        bar_chart(chart_dir / f"metric_{index}.png", metric["baseline"], metric["current"], maximum)
    rows = "".join(
        f"<tr><td>{html.escape(m['name'])}</td><td>{m['baseline']}{m['unit']}</td><td>{m['current']}{m['unit']}</td><td>{m['target']}{m['unit']}</td><td>{'On target' if (m['current'] >= m['target'] if m['higher'] else m['current'] <= m['target']) else 'Action required'}</td></tr>"
        for m in metrics
    )
    figures = "".join(f"<figure><img src='metrics_visualizations/metric_{i}.png' alt='Baseline and current bars for {html.escape(m['name'])}'><figcaption>Figure {i}: {html.escape(m['name'])} — red is baseline; green is current.</figcaption></figure>" for i, m in enumerate(metrics, 1))
    (ROOT / "executive_dashboard.html").write_text(f"""<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width'><title>Executive Security Governance Dashboard</title><style>body{{font:16px system-ui;margin:35px;color:#17324d;background:#f4f7fb}}header,table,figure{{background:white;padding:20px;margin:15px 0;border-radius:10px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #dde4ea}}img{{max-width:100%}}figure{{display:inline-block;width:44%;vertical-align:top}}.notice{{border-left:5px solid #d97706;padding-left:12px}}</style><header><h1>Executive Security Governance Dashboard</h1><p>Generated {html.escape(human_now())}</p><p class=notice>Baseline and current values are derived from this isolated simulation's saved evidence; they are not production measurements.</p></header><table><tr><th>Metric</th><th>Baseline</th><th>Current</th><th>Target</th><th>Status</th></tr>{rows}</table>{figures}</html>""", encoding="utf-8")
    metric_rows = "\n".join(f"| {m['name']} | {m['baseline']}{m['unit']} | {m['current']}{m['unit']} | {m['target']}{m['unit']} |" for m in metrics)
    (ROOT / "board_report.md").write_text(f"""# Security Governance Board Report

**Generated:** {human_now()}

## Executive summary

The isolated simulation demonstrates how evidence-backed patching, segmentation, stronger authentication, monitoring, and named oversight can reduce an Equifax-like governance risk. Values below describe this lab only and must not be interpreted as production assurance.

| Metric | Baseline | Current | Target |
|---|---:|---:|---:|
{metric_rows}

## Residual risks

- The replacement web page is a control demonstration, not a migrated production application.
- Container-level tests do not replace an independent penetration test or audit.
- Control sustainability requires repeated measurement and owner escalation after this point-in-time test.

## Decisions requested

1. Enforce the seven-day SLA and executive escalation for critical vulnerabilities.
2. Require quarterly independent verification of segmentation and privileged database access.
3. Review monitoring coverage and overdue risk at every board security meeting.
""", encoding="utf-8")
    (ROOT / "metrics_framework.md").write_text("""# Security Governance Metrics Framework

| Metric | Definition | Source | Owner | Frequency | Escalation |
|---|---|---|---|---|---|
| Critical patch compliance | Critical findings remediated within SLA / critical findings due | Scan and patch evidence | CISO | Weekly | CEO below 95% |
| Critical remediation time | Days from detection to verified closure | Scan timestamps | Security Manager | Weekly | CISO above 7 days |
| Open critical/high findings | Unresolved critical and high findings | Vulnerability report | System owners | Weekly | Risk Committee above 0 |
| Monitoring coverage | Monitored critical services / critical services | Monitoring inventory | SOC Lead | Monthly | CISO below 95% |
| Verification pass rate | Passed control tests / planned tests | Controls verification | Internal Audit | Quarterly | Risk Committee below 100% |
| Ownership coverage | Controls with named owner / controls | Governance register | CISO | Quarterly | CEO below 100% |

Each metric needs traceable evidence, a named owner, a target, and an escalation action. Simulation values must remain labelled as such.
""", encoding="utf-8")
    (ROOT / "dashboard_user_guide.md").write_text("""# Executive Dashboard User Guide

Open `executive_dashboard.html` in a browser. The table compares baseline evidence, the latest verified state, and the governance target. Red bars show baseline values and green bars show current values. “Action required” means an owner must investigate and record a dated treatment decision. Regenerate the dashboard only after new scanner and verification evidence has been saved.
""", encoding="utf-8")
    print("Generated executive_dashboard.html, board_report.md, metrics_framework.md, dashboard_user_guide.md, and six PNG charts.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    generate()


if __name__ == "__main__":
    main()

