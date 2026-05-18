"""Beginner analysis: most active day of the week per participant."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"]


def most_active_weekday(
    rows: Iterable[Mapping[str, Any]],
    participant_key: str = "participant",
    date_key: str = "date",
    steps_key: str = "steps",
) -> dict[str, tuple[str, int]]:
    """Return the most active weekday for each participant.

    Algorithm:
        1. Single pass through all rows.
        2. For each row, extract weekday (0=Mon ... 6=Sun) from the date.
        3. Accumulate steps per (participant, weekday) in a nested dict.
        4. For each participant, scan 7 weekday totals to find the maximum.

    Time:  O(n + p) where n = number of rows, p = number of participants.
           Since p <= n, effectively O(n).
    Space: O(p * 7) = O(p) for the accumulator dict.

    Returns:
        Dict mapping participant_id -> (weekday_name, total_steps).
    """
    # Step 1: accumulate steps per (participant, weekday)
    totals: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        participant = str(row[participant_key])
        date_val = row[date_key]
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%d.%m.%y").date()
        weekday = date_val.weekday()  # 0=Monday ... 6=Sunday
        totals[participant][weekday] += int(row[steps_key])

    # Step 2: find best weekday per participant (scan over 7 entries)
    result: dict[str, tuple[str, int]] = {}
    for participant, weekday_totals in totals.items():
        best_weekday = -1
        best_steps = -1
        for wd, steps in weekday_totals.items():
            if steps > best_steps:
                best_steps = steps
                best_weekday = wd
        result[participant] = (WEEKDAY_NAMES[best_weekday], best_steps)

    return result


# Tests
assert most_active_weekday([]) == {}
assert most_active_weekday(
    [{"participant": "X", "date": "09.07.21", "steps": 4200}]
) == {"X": ("Friday", 4200)}
assert most_active_weekday([
    {"participant": "A", "date": "05.07.21", "steps": 1000},  # Monday
    {"participant": "A", "date": "06.07.21", "steps": 8000},  # Tuesday
]) == {"A": ("Tuesday", 8000)}
print("All tests passed!")


# Data loading
def _load_rows_from_researchdata(max_files: int = 12) -> list[dict[str, Any]]:
    """Load rows from researchdata CSV files."""
    repo_root = Path(__file__).resolve().parents[1]
    csv_paths = sorted(
        (repo_root / "data" / "researchdata").glob("*.csv"))[:max_files]
    rows: list[dict[str, Any]] = []

    for csv_path in csv_paths:
        participant = csv_path.stem
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for raw in reader:
                if not raw.get("DATE") or not raw.get("ACTIVITY_steps"):
                    continue
                rows.append({
                    "participant": participant,
                    "date": datetime.strptime(raw["DATE"], "%d.%m.%y").date(),
                    "steps": int(raw["ACTIVITY_steps"]),
                })
    return rows


if __name__ == "__main__":
    sample_rows = _load_rows_from_researchdata()
    if sample_rows:
        result = most_active_weekday(sample_rows)
        print(
            f"Loaded {
                len(sample_rows)} rows for {
                len(result)} participants\n")
        for pid, (weekday, steps) in sorted(result.items()):
            print(f"  Participant {pid}: {weekday} ({steps:,} total steps)")
    else:
        print("No data loaded from researchdata/")
