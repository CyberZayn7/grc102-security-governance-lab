#!/usr/bin/env python3
"""Perform a non-destructive Struts detection request in the local lab."""
from __future__ import annotations

import argparse
import json

from lab_utils import ROOT, now, save_json
from vulnerability_scanner import struts_check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8080/")
    args = parser.parse_args()
    check = struts_check(args.url)
    event = {
        "timestamp": now(),
        "authorised_scope": "Local Docker lab only",
        "attack_type": "Safe S2-045 detection simulation",
        "target": args.url,
        "success": check["vulnerable"] is True,
        "data_accessed": False,
        "records_affected": 0,
        "evidence": check["evidence"],
        "note": "No command execution, database query, or data exfiltration was attempted.",
    }
    save_json(ROOT / "attack_log.json", event)
    print(json.dumps(event, indent=2))


if __name__ == "__main__":
    main()

