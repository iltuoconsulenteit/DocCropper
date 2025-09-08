import re
from datetime import datetime, date
import pathlib

def test_updates_dates_not_in_future():
    path = pathlib.Path(__file__).resolve().parent.parent / "UPDATES.md"
    today = date.today()
    pattern = re.compile(r"## (\d{4}-\d{2}-\d{2})")
    with path.open(encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                entry_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                assert entry_date <= today, f"UPDATES.md has future date {entry_date}"
