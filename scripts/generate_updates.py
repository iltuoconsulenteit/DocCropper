#!/usr/bin/env python3
"""Generate UPDATES.md from git commit history.

This helper extracts commit dates and messages so update entries always
reflect the repository log without manually maintaining timestamps.
"""

import subprocess
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

# Limit the number of commits to keep the log readable
MAX_COMMITS = 200

# Get commit history: date and subject
result = subprocess.run(
    [
        "git",
        "log",
        f"-n{MAX_COMMITS}",
        "--pretty=format:%cd|%s",
        "--date=short",
    ],
    capture_output=True,
    text=True,
    check=True,
)

lines = result.stdout.strip().splitlines()
by_date = defaultdict(list)
today = date.today()
for line in lines:
    if "|" not in line:
        continue
    date_str, msg = line.split("|", 1)
    commit_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    # Avoid logging dates in the future relative to today
    if commit_date > today:
        commit_date = today
    by_date[commit_date].append(f"- {msg.strip()}")

path = Path(__file__).resolve().parent.parent / "UPDATES.md"
with path.open("w", encoding="utf-8") as fh:
    fh.write("# Updates\n\n")
    for d in sorted(by_date.keys(), reverse=True):
        fh.write(f"## {d.isoformat()}\n")
        fh.write("\n".join(by_date[d]))
        fh.write("\n\n")
