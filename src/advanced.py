"""Advanced analysis: Longest Increasing Subsequence (LIS) of daily steps.

Find the longest subsequence of days (not necessarily consecutive) where
step counts are strictly increasing. This reveals the longest "progress
trend" in a participant's activity history.

Baseline:  O(n^2) DP — for each day, scan all previous days.
Optimized: O(n log n) — patience sorting with binary search.
"""

from __future__ import annotations

import csv
from bisect import bisect_left
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


# Baseline: O(n^2) DP

def lis_baseline(steps: Sequence[int]) -> tuple[int, list[int]]:
    """Return (length, subsequence) of the LIS using classic DP.

    dp[i] = length of LIS ending at index i.
    prev[i] = index of previous element in that LIS (for reconstruction).

    Time:  O(n^2)
    Space: O(n)
    """
    n = len(steps)
    if n == 0:
        return 0, []

    dp = [1] * n
    prev = [-1] * n

    for i in range(1, n):
        for j in range(i):
            if steps[j] < steps[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j

    # Find the index with the maximum LIS length
    best_idx = 0
    for i in range(1, n):
        if dp[i] > dp[best_idx]:
            best_idx = i

    # Reconstruct the subsequence
    subseq: list[int] = []
    idx = best_idx
    while idx != -1:
        subseq.append(steps[idx])
        idx = prev[idx]
    subseq.reverse()

    return dp[best_idx], subseq


# Optimized: O(n log n) patience sorting

def lis_optimized(steps: Sequence[int]) -> tuple[int, list[int]]:
    """Return (length, subsequence) of the LIS using patience sorting.

    Maintains a list `tails` where tails[i] is the smallest tail value
    of all increasing subsequences of length i+1 found so far.
    Uses binary search to find the insertion point.

    For reconstruction, we store for each element the length of the LIS
    ending at that element, and the predecessor index.

    Time:  O(n log n)
    Space: O(n)
    """
    n = len(steps)
    if n == 0:
        return 0, []

    # tails[i] = smallest tail of all increasing subsequences of length i+1
    tails: list[int] = []
    # For reconstruction: lis_len[i] = length of LIS ending at index i
    lis_len: list[int] = [0] * n
    # prev[i] = index of previous element in the LIS ending at i
    prev: list[int] = [-1] * n
    # tail_indices[i] = index in `steps` of the element stored in tails[i]
    tail_indices: list[int] = []

    for i in range(n):
        pos = bisect_left(tails, steps[i])

        if pos == len(tails):
            tails.append(steps[i])
            tail_indices.append(i)
        else:
            tails[pos] = steps[i]
            tail_indices[pos] = i

        lis_len[i] = pos + 1

        if pos > 0:
            prev[i] = tail_indices[pos - 1]
        else:
            prev[i] = -1

    # Reconstruct: find the last element with maximum LIS length
    best_len = len(tails)
    best_idx = -1
    for i in range(n - 1, -1, -1):
        if lis_len[i] == best_len:
            best_idx = i
            break

    subseq: list[int] = []
    idx = best_idx
    while idx != -1:
        subseq.append(steps[idx])
        idx = prev[idx]
    subseq.reverse()

    return best_len, subseq


# Full analysis with dates

def lis_with_dates(
    dates: Sequence[Any],
    steps: Sequence[int],
) -> tuple[int, list[tuple[Any, int]]]:
    """Return LIS length and list of (date, steps) pairs in the subsequence.

    Uses the optimized O(n log n) algorithm internally.
    """
    n = len(steps)
    if n == 0:
        return 0, []

    tails: list[int] = []
    lis_len: list[int] = [0] * n
    prev: list[int] = [-1] * n
    tail_indices: list[int] = []

    for i in range(n):
        pos = bisect_left(tails, steps[i])
        if pos == len(tails):
            tails.append(steps[i])
            tail_indices.append(i)
        else:
            tails[pos] = steps[i]
            tail_indices[pos] = i
        lis_len[i] = pos + 1
        prev[i] = tail_indices[pos - 1] if pos > 0 else -1

    best_len = len(tails)
    best_idx = -1
    for i in range(n - 1, -1, -1):
        if lis_len[i] == best_len:
            best_idx = i
            break

    result: list[tuple[Any, int]] = []
    idx = best_idx
    while idx != -1:
        result.append((dates[idx], steps[idx]))
        idx = prev[idx]
    result.reverse()

    return best_len, result


# Tests
assert lis_baseline([]) == (0, [])
assert lis_optimized([]) == (0, [])
assert lis_baseline([3, 10, 2, 1, 20])[0] == 3
assert lis_optimized([3, 10, 2, 1, 20])[0] == 3
assert lis_baseline([50, 40, 30, 20, 10])[0] == 1
assert lis_optimized([1, 2, 3, 4, 5]) == (5, [1, 2, 3, 4, 5])
assert lis_baseline([5, 5, 5, 5])[0] == 1
print("All tests passed!")


# Data loading

def _load_participant_data(
    max_files: int = 12,
) -> dict[str, tuple[list[Any], list[int]]]:
    """Load per-participant sorted (dates, steps) from researchdata."""
    repo_root = Path(__file__).resolve().parents[1]
    csv_paths = sorted(
        (repo_root / "data" / "researchdata").glob("*.csv"))[:max_files]
    participants: dict[str, list[tuple[Any, int]]] = {}

    for csv_path in csv_paths:
        pid = csv_path.stem
        entries: list[tuple[Any, int]] = []
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for raw in reader:
                if not raw.get("DATE") or not raw.get("ACTIVITY_steps"):
                    continue
                d = datetime.strptime(raw["DATE"], "%d.%m.%y").date()
                entries.append((d, int(raw["ACTIVITY_steps"])))
        entries.sort(key=lambda x: x[0])
        dates = [e[0] for e in entries]
        steps = [e[1] for e in entries]
        participants[pid] = (dates, steps)

    return participants


if __name__ == "__main__":
    participants = _load_participant_data()
    if not participants:
        raise SystemExit("No data loaded from researchdata/")

    print(f"Loaded data for {len(participants)} participants\n")
    print(
        f"{
            'Participant':>12}  {
            'Days':>5}  {
                'LIS len':>8}  {
                    'LIS %':>6}  First -> Last in LIS")
    print("-" * 75)

    for pid in sorted(participants.keys()):
        dates, steps = participants[pid]
        n = len(steps)
        lis_len, lis_pairs = lis_with_dates(dates, steps)
        pct = (lis_len / n * 100) if n > 0 else 0

        if lis_pairs:
            first = f"{lis_pairs[0][0]} ({lis_pairs[0][1]:,})"
            last = f"{lis_pairs[-1][0]} ({lis_pairs[-1][1]:,})"
        else:
            first = last = "N/A"

        print(f"{pid:>12}  {n:>5}  {lis_len:>8}  {pct:>5.1f}%  {first} -> {last}")

    # Detailed example for first participant
    first_pid = sorted(participants.keys())[0]
    dates, steps = participants[first_pid]
    lis_len, lis_pairs = lis_with_dates(dates, steps)

    # Verify baseline matches optimized
    bl, _ = lis_baseline(steps)
    ol, _ = lis_optimized(steps)
    print(f"\nVerification for participant {first_pid}:")
    print(f"  Baseline LIS length:  {bl}")
    print(f"  Optimized LIS length: {ol}")
    print(f"  Match: {bl == ol}")

    print(f"\nFirst 10 entries of LIS for participant {first_pid}:")
    for d, s in lis_pairs[:10]:
        print(f"  {d}: {s:,} steps")