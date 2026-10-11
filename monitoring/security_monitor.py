#!/usr/bin/env python3
"""Capture a small, repeatable local-container monitoring snapshot."""
from pathlib import Path
import subprocess
import datetime

root = Path(__file__).resolve().parents[1]
out = root / "evidence" / "post-control" / "monitoring_snapshot.txt"
out.parent.mkdir(parents=True, exist_ok=True)
commands = [
    ["docker", "ps", "--filter", "name=web_server", "--filter", "name=database_server", "--filter", "name=monitoring_server", "--format", "{{.Names}}\t{{.Status}}"],
    ["docker", "logs", "--tail", "20", "web_server"],
]
blocks = [f"Monitoring snapshot: {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}"]
for command in commands:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    blocks.extend(["$ " + " ".join(command), result.stdout.strip(), result.stderr.strip()])
out.write_text("\n".join(filter(None, blocks)) + "\n", encoding="utf-8")
print(out.relative_to(root))

