"""Intermediate analysis: does yesterday's activity affect today's sleep quality?

Baseline approach: for every query (participant, date) scan all rows to find
    yesterday's steps and today's sleep — O(n) per query, O(q*n) total.

Optimized approach: preprocess data into a sorted index per participant,
    then use binary search for O(log n) per query.

Additionally, we compute Pearson correlation between yesterday's steps and
today's sleep duration for each participant to quantify the relationship.
"""

from __future__ import annotations

import csv
import math
from bisect import bisect_left
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping


# Baseline: O(n) per query

def baseline_get_pair(
    rows: list[Mapping[str, Any]],
    participant: str,
    query_date: date,
    participant_key: str = "participant",
    date_key: str = "date",
    steps_key: str = "steps",
    sleep_key: str = "sleep_duration",
) -> tuple[int | None, int | None]:
    """Return (yesterday_steps, today_sleep) by scanning all rows.

    Time: O(n) per call.
    """
    yesterday = query_date - timedelta(days=1)
    yesterday_steps = None
    today_sleep = None

    for row in rows:
        if str(row[participant_key]) != participant:
            continue
        d = row[date_key] if isinstance(
            row[date_key], date) else datetime.strptime(
            row[date_key], "%d.%m.%y").date()
        if d == yesterday:
            yesterday_steps = int(row[steps_key])
        if d == query_date:
            today_sleep = int(row[sleep_key])
        if yesterday_steps is not None and today_sleep is not None:
            break

    return yesterday_steps, today_sleep


# Optimized: preprocess + binary search

def build_recovery_index(
    rows: Iterable[Mapping[str, Any]],
    participant_key: str = "participant",
    date_key: str = "date",
    steps_key: str = "steps",
    sleep_key: str = "sleep_duration",
) -> dict[str, tuple[list[date], list[int], list[int]]]:
    """Preprocess rows into sorted per-participant index.

    For each participant, stores:
        - sorted list of dates
        - corresponding steps values
        - corresponding sleep_duration values

    Time:  O(n log n) for sorting per participant.
    Space: O(n) total.
    """
    buckets: dict[str, list[tuple[date, int, int]]] = {}
    for row in rows:
        pid = str(row[participant_key])
        d = row[date_key] if isinstance(
            row[date_key], date) else datetime.strptime(
            row[date_key], "%d.%m.%y").date()
        steps = int(row[steps_key])
        sleep = int(row[sleep_key])
        buckets.setdefault(pid, []).append((d, steps, sleep))

    index: dict[str, tuple[list[date], list[int], list[int]]] = {}
    for pid, entries in buckets.items():
        entries.sort(key=lambda x: x[0])
        dates = [e[0] for e in entries]
        steps = [e[1] for e in entries]
        sleeps = [e[2] for e in entries]
        index[pid] = (dates, steps, sleeps)

    return index


def fast_get_pair(
    index: dict[str, tuple[list[date], list[int], list[int]]],
    participant: str,
    query_date: date,
) -> tuple[int | None, int | None]:
    """Return (yesterday_steps, today_sleep) using binary search.

    Time: O(log n_p) per call where n_p = days for this participant.
    """
    data = index.get(participant)
    if not data:
        return None, None

    dates, steps, sleeps = data
    yesterday = query_date - timedelta(days=1)

    # Find yesterday's steps
    idx_y = bisect_left(dates, yesterday)
    yesterday_steps = steps[idx_y] if idx_y < len(
        dates) and dates[idx_y] == yesterday else None

    # Find today's sleep
    idx_t = bisect_left(dates, query_date)
    today_sleep = sleeps[idx_t] if idx_t < len(
        dates) and dates[idx_t] == query_date else None

    return yesterday_steps, today_sleep


# Correlation analysis

def compute_recovery_pairs(
    index: dict[str, tuple[list[date], list[int], list[int]]],
    participant: str,
) -> list[tuple[int, int]]:
    """Extract all (yesterday_steps, today_sleep) consecutive-day pairs.

    Scans the sorted date list for the participant; when two entries are
    exactly 1 day apart, records (steps[i], sleep[i+1]).

    Time:  O(n_p) single pass.
    Space: O(n_p) for the result list.
    """
    data = index.get(participant)
    if not data:
        return []

    dates, steps, sleeps = data
    pairs: list[tuple[int, int]] = []

    for i in range(len(dates) - 1):
        if (dates[i + 1] - dates[i]).days == 1:
            pairs.append((steps[i], sleeps[i + 1]))

    return pairs


def pearson_correlation(pairs: list[tuple[int, int]]) -> float | None:
    """Compute Pearson correlation coefficient for a list of (x, y) pairs.

    Returns None if fewer than 2 pairs or zero variance.

    Time:  O(k) where k = len(pairs).
    Space: O(1) extra (running sums only).
    """
    n = len(pairs)
    if n < 2:
        return None

    sum_x = sum_y = sum_xx = sum_yy = sum_xy = 0.0
    for x, y in pairs:
        sum_x += x
        sum_y += y
        sum_xx += x * x
        sum_yy += y * y
        sum_xy += x * y

    denom_x = n * sum_xx - sum_x * sum_x
    denom_y = n * sum_yy - sum_y * sum_y

    if denom_x <= 0 or denom_y <= 0:
        return None

    return (n * sum_xy - sum_x * sum_y) / math.sqrt(denom_x * denom_y)


# Tests
assert fast_get_pair(
    build_recovery_index(
        []),
    "A",
    date(
        2023,
        1,
        2)) == (
    None,
    None)
assert fast_get_pair(
    build_recovery_index([
        {"participant": "A", "date": date(
            2023, 1, 1), "steps": 10000, "sleep_duration": 25000},
        {"participant": "A", "date": date(
            2023, 1, 2), "steps": 5000, "sleep_duration": 28000},
    ]),
    "A", date(2023, 1, 2),
) == (10000, 28000)
assert pearson_correlation([(1000, 100), (2000, 200), (3000, 300)]) == 1.0
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
                if not raw.get("DATE") or not raw.get(
                        "ACTIVITY_steps") or not raw.get("SLEEP_totalsleeptime"):
                    continue
                rows.append({
                    "participant": participant,
                    "date": datetime.strptime(raw["DATE"], "%d.%m.%y").date(),
                    "steps": int(raw["ACTIVITY_steps"]),
                    "sleep_duration": int(raw["SLEEP_totalsleeptime"]),
                })
    return rows


if __name__ == "__main__":
    sample_rows = _load_rows_from_researchdata()
    if not sample_rows:
        raise SystemExit("No data loaded from researchdata/")

    index = build_recovery_index(sample_rows)
    print(f"Loaded {len(sample_rows)} rows for {len(index)} participants\n")
    print("Recovery correlation (yesterday steps vs today sleep duration):")
    print(f"{'Participant':>12}  {'Pairs':>6}  {'Pearson r':>10}  Interpretation")
    print("-" * 58)

    for pid in sorted(index.keys()):
        pairs = compute_recovery_pairs(index, pid)
        r = pearson_correlation(pairs)
        if r is None:
            interp = "insufficient data"
        elif r > 0.3:
            interp = "positive (more steps -> more sleep)"
        elif r < -0.3:
            interp = "negative (more steps -> less sleep)"
        else:
            interp = "weak / no correlation"
        r_str = f"{r:.4f}" if r is not None else "N/A"
        print(f"{pid:>12}  {len(pairs):>6}  {r_str:>10}  {interp}")

    # Demo: baseline vs optimized query comparison
    first_pid = sorted(index.keys())[0]
    dates_list = index[first_pid][0]
    if len(dates_list) > 1:
        query = dates_list[1]
        b = baseline_get_pair(sample_rows, first_pid, query)
        f = fast_get_pair(index, first_pid, query)
        print(f"\nDemo query: participant={first_pid}, date={query}")
        print(
            f"  Baseline result:  yesterday_steps={
                b[0]}, today_sleep={
                b[1]}")
        print(
            f"  Optimized result: yesterday_steps={
                f[0]}, today_sleep={
                f[1]}")
        print(f"  Results match: {b == f}")
