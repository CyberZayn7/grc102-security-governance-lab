#!/usr/bin/env python3
"""Render genuine saved lab evidence to labelled PNG screenshots with Chrome."""
from __future__ import annotations

import argparse
import html
import subprocess
from pathlib import Path

from lab_utils import EVIDENCE, ROOT, latest

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SCREENSHOTS = EVIDENCE / "screenshots"
PAGES = EVIDENCE / "pages"


def page(title: str, source: Path, caption: str) -> Path:
    text = source.read_text(encoding="utf-8") if source.exists() else "Required evidence file is missing."
    path = PAGES / (source.stem + ".html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""<!doctype html><html lang=en><meta charset=utf-8><style>body{{font:18px system-ui;margin:36px;color:#17324d}}pre{{white-space:pre-wrap;background:#101923;color:#d7e4ef;padding:24px;border-radius:8px;font:15px ui-monospace;min-height:420px}}footer{{color:#52677c}}</style><h1>{html.escape(title)}</h1><pre>{html.escape(text)}</pre><footer>{html.escape(caption)}</footer></html>""", encoding="utf-8")
    return path


def shot(number: int, url: str, name: str):
    output = SCREENSHOTS / f"figure_{number:02d}_{name}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1440,1000", f"--screenshot={output}", url]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode or not output.exists():
        raise SystemExit(result.stderr or f"Failed to capture {output}")
    print(output.relative_to(ROOT))


def baseline():
    scan = latest("evidence/baseline/vulnerability_report_*.json")
    failures = latest("evidence/baseline/governance_failure_report_*.json")
    required = [scan, failures, ROOT / "attack_log.json", ROOT / "governance_dashboard.html", EVIDENCE / "runtime" / "docker_ps_baseline.txt"]
    if any(item is None or not item.exists() for item in required):
        raise SystemExit("Baseline evidence is incomplete; run the baseline workflow first")
    p1 = page("Baseline Docker environment", required[4], "Actual docker compose ps output from the isolated lab.")
    p3 = page("Baseline vulnerability scan", scan, "Timestamped scanner output generated from live container checks.")
    p5 = page("Safe attack simulation", ROOT / "attack_log.json", "No command execution or data access was attempted.")
    p6 = page("Governance failure analysis", failures, "Failures derived from the saved baseline scan.")
    shot(1, p1.as_uri(), "docker_environment")
    shot(2, "http://127.0.0.1:8080/", "baseline_application")
    shot(3, p3.as_uri(), "baseline_scan")
    shot(4, (ROOT / "governance_dashboard.html").as_uri(), "governance_dashboard")
    shot(5, p5.as_uri(), "attack_simulation")
    shot(6, p6.as_uri(), "failure_analysis")


def post_control():
    post_scan = latest("evidence/post-control/vulnerability_report_*.json")
    required = [ROOT / "patch_status.json", ROOT / "controls_report.md", post_scan, ROOT / "executive_dashboard.html"]
    if any(item is None or not item.exists() for item in required):
        raise SystemExit("Post-control evidence is incomplete; run secure verification and metrics first")
    p7 = page("Implemented control records", required[0], "Dated patch, authentication, and segmentation change records.")
    p8 = page("Control verification", required[1], "Direct verification results from the secure Docker configuration.")
    p9 = page("Post-control vulnerability scan", post_scan, "The same scanner rerun against the controlled environment.")
    shot(7, p7.as_uri(), "implemented_controls")
    shot(8, p8.as_uri(), "control_verification")
    shot(9, p9.as_uri(), "post_control_scan")
    shot(10, required[3].as_uri(), "executive_dashboard")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["baseline", "post-control", "all"])
    args = parser.parse_args()
    if not CHROME.exists():
        raise SystemExit(f"Chrome not found at {CHROME}")
    if args.phase in {"baseline", "all"}:
        baseline()
    if args.phase in {"post-control", "all"}:
        post_control()


if __name__ == "__main__":
    main()

