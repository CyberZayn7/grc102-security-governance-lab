#!/usr/bin/env python3
"""Record simulated change approvals without pretending they patch production."""
from __future__ import annotations

import argparse

from lab_utils import ROOT, load_json, now, save_json

PATCHES = {
    "PATCH-001": "Replace vulnerable Struts training image",
    "PATCH-002": "Remove default database credentials",
    "PATCH-003": "Separate frontend and data networks",
}


def apply(patch_id: str):
    state_file = ROOT / "patch_status.json"
    state = load_json(state_file, {})
    state[patch_id] = {"name": PATCHES[patch_id], "status": "Applied in secure lab configuration", "applied_at": now(), "owner": "Security Engineer"}
    save_json(state_file, state)
    print(f"{patch_id}: {PATCHES[patch_id]} recorded")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true")
    group.add_argument("--apply", choices=PATCHES)
    args = parser.parse_args()
    if args.list:
        for key, value in PATCHES.items():
            print(f"{key}: {value}")
    else:
        apply(args.apply)


if __name__ == "__main__":
    main()

