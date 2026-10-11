#!/usr/bin/env python3
"""Small shared helpers for the isolated GRC102 lab."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def human_now() -> str:
    return dt.datetime.now().astimezone().strftime("%d %B %Y at %I:%M %p %Z")


def human_time(value: str) -> str:
    return dt.datetime.fromisoformat(value).strftime("%d %B %Y at %I:%M %p %Z")


def stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def latest(pattern: str) -> Path | None:
    files = sorted(ROOT.glob(pattern))
    return files[-1] if files else None


def run(args: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def docker_networks(container: str) -> set[str]:
    result = run(["docker", "inspect", container, "--format", "{{json .NetworkSettings.Networks}}"])
    if result.returncode:
        return set()
    try:
        return set(json.loads(result.stdout))
    except json.JSONDecodeError:
        return set()

