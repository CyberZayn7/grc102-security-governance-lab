#!/usr/bin/env python3
"""Build the professional four-part HTML/PDF evidence report."""
from __future__ import annotations

import argparse
import html
import subprocess
from pathlib import Path

from lab_utils import ROOT, human_now

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SHOTS = ROOT / "evidence" / "screenshots"
OUTPUT_HTML = ROOT / "GRC102_Lab8_Evidence_Report.html"
OUTPUT_PDF = ROOT / "GRC102_Lab8_Evidence_Report.pdf"

FIGURES = [
    (1, "Baseline Docker environment", "The container listing demonstrates that the web, database, and monitoring services ran inside the authorised local Docker lab."),
    (2, "Customer-facing baseline application", "The intentionally vulnerable training application was reachable only through the loopback interface."),
    (3, "Baseline vulnerability scan", "The scanner records the critical Struts exposure, default database authentication, and shared-network condition."),
    (4, "Governance tracker dashboard", "The baseline register connects policies, controls, risks, incidents, metrics, audits, and accountable owners."),
    (5, "Safe attack simulation", "The simulation performs detection only and explicitly records that no data was accessed or exfiltrated."),
    (6, "Governance failure analysis", "Technical observations are translated into ownership, impact, and remediation decisions."),
    (7, "Implemented control records", "Dated records document the controlled replacement, database hardening, and segmentation changes."),
    (8, "Post-control verification", "Independent checks test patch behaviour, credentials, networks, monitoring, and oversight."),
    (9, "Post-control scan", "The baseline scanner is repeated to make the before-and-after comparison consistent."),
    (10, "Executive dashboard", "Evidence-derived metrics present targets, current state, residual risk, and management action."),
]


def find_shot(number: int) -> Path:
    matches = sorted(SHOTS.glob(f"figure_{number:02d}_*.png"))
    if not matches:
        raise SystemExit(f"Missing genuine screenshot for Figure {number}; run capture_evidence.py")
    return matches[0]


def figure(number: int, title: str, explanation: str) -> str:
    image = find_shot(number).relative_to(ROOT)
    return f"<figure><img src='{image}' alt='{html.escape(title)}'><figcaption><b>Figure {number}: {html.escape(title)}.</b> {html.escape(explanation)}</figcaption></figure>"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-name", default="Zainab Umar Shuaibu")
    parser.add_argument("--student-id", default="C11/26/CGRCE/17194")
    args = parser.parse_args()
    rendered = {number: figure(number, title, text) for number, title, text in FIGURES}
    OUTPUT_HTML.write_text(f"""<!doctype html><html lang=en><meta charset=utf-8><title>GRC102 Lab 8 Evidence Report</title><style>@page{{size:A4;margin:18mm}}body{{font:11pt Arial;color:#172b3a;line-height:1.45}}h1{{font-size:24pt}}h2{{color:#134e6f;border-bottom:2px solid #36a2a8;padding-bottom:5px;page-break-before:always}}h2.first{{page-break-before:auto}}figure{{margin:18px 0;page-break-inside:avoid}}img{{width:100%;border:1px solid #b8c4cc}}figcaption{{font-size:9pt;color:#415466;margin-top:5px}}.cover{{height:80vh;display:flex;flex-direction:column;justify-content:center}}.notice{{background:#fff7df;border-left:5px solid #d68b00;padding:12px}}li{{margin-bottom:6px}}</style>
<section class=cover><h1>GRC102 Security Governance Simulation</h1><h3>Practical Lab 8: Monitoring, Auditing Controls and Executive Reporting</h3><p><b>Student:</b> {html.escape(args.student_name)}</p><p><b>Student ID:</b> {html.escape(args.student_id)}</p><p><b>Generated:</b> {html.escape(human_now())}</p><p><b>Environment:</b> Isolated local Docker environment</p></section>
<h2 class=first>Part 1 — Setting Up a Simulated Environment</h2><p>The baseline combines an intentionally vulnerable Struts training service, a database containing three explicitly synthetic rows, and a monitoring container on one shared network. Loopback-only port binding prevents external exposure. This models delayed patching, weak authentication, and insufficient segmentation while limiting the activity to the authorised host.</p>{rendered[1]}{rendered[2]}{rendered[3]}{rendered[4]}
<h2>Part 2 — Analysing Security Governance Failures</h2><p>The safe request confirmed whether the S2-045 response behaviour was present; it did not execute operating-system commands or access the database. The analysis identified failures in remediation, access control, architecture, monitoring, policy enforcement, and executive accountability. These mirror governance lessons from Equifax while avoiding a claim that the small simulation reproduces the scale or impact of that incident.</p>{rendered[5]}{rendered[6]}
<h2>Part 3 — Implementing Security Governance Controls</h2><p>The secure configuration replaces the vulnerable training service, removes default credentials, keeps the database off host ports, and separates frontend and internal data networks. Monitoring captures dated service evidence, while the oversight register assigns owners, review dates, thresholds, and escalation routes. Verification uses direct container and HTTP checks rather than relying solely on implementation status.</p>{rendered[7]}{rendered[8]}{rendered[9]}
<h2>Part 4 — Developing Security Governance Metrics and Reporting</h2><p>The dashboard derives its current state from the saved scan and control-verification evidence. Its metrics cover patching, remediation time, unresolved high-risk findings, monitoring, test results, and ownership. Targets make exceptions visible and connect operational evidence to decisions required from management and the board.</p>{rendered[10]}
<h3>Governance value</h3><p>Evidence-backed reporting helps leadership distinguish implemented controls from stated intent. Named owners and escalation thresholds make overdue risk actionable, while repeatable before-and-after tests support auditability and continuous oversight.</p>
<h3>References</h3><ul><li>U.S. GAO, <i>Data Protection: Actions Taken by Equifax and Federal Agencies in Response to the 2017 Breach</i>, GAO-18-559 (2018).</li><li>U.S. House Committee on Oversight and Government Reform, <i>The Equifax Data Breach</i> (2018).</li><li>NIST National Vulnerability Database, CVE-2017-5638.</li><li>ICDFA, GRC102 Week 8 Lab Instructions.</li></ul></html>""", encoding="utf-8")
    result = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={OUTPUT_PDF}", OUTPUT_HTML.as_uri()], cwd=ROOT, text=True, capture_output=True)
    if result.returncode or not OUTPUT_PDF.exists():
        raise SystemExit(result.stderr or "PDF generation failed")
    print(OUTPUT_PDF.name)


if __name__ == "__main__":
    main()

