# Matsvei Hemza — Algorithms Project

Analysis of the Withings smartwatch dataset (12 participants, ~290 days each):
daily activity (steps, distance, heart rate) and sleep metrics.

The project contains three analyses of increasing complexity:

- `src/beginner.py` — most active weekday per participant (O(n) aggregation).
- `src/intermediate.py` — does yesterday's activity affect today's sleep?
  Baseline O(n) scan vs. O(log n) binary search on a sorted per-participant index,
  plus Pearson correlation.
- `src/advanced.py` — Longest Increasing Subsequence of daily steps.
  Baseline O(n²) DP vs. optimized O(n log n) patience sorting.

See [`src/README.md`](src/README.md) for the per-analysis breakdown (problem,
algorithm, complexity, tests).

## Prerequisites

- **Python 3.9 or newer** (the code uses PEP 585 generic types like `list[int]`).
- **git** for cloning the repository.

No third-party dependencies — every script uses the Python standard library only.

## Installation

1. **Clone the repository**

   ```bash
   git clone git@gitlab.unige.ch:alg-26/spring-2026/matsvei-hemza.git
   cd matsvei-hemza
   ```

   If you don't have SSH access set up, use HTTPS instead:

   ```bash
   git clone https://gitlab.unige.ch/alg-26/spring-2026/matsvei-hemza.git
   ```

2. **Create and activate a virtual environment** (recommended)

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate          # macOS / Linux
   .venv\Scripts\activate             # Windows (PowerShell / cmd)
   ```

3. **Install dependencies**

   `requirements.txt` is currently empty (stdlib only), but running this is safe
   and future-proof:

   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the dataset is present**

   The CSV files should already be in `data/researchdata/` (12 files named
   `<participant_id>.csv`). Check with:

   ```bash
   ls data/researchdata/
   ```

## Running the analyses

Each script runs its inline tests on import and then prints results from the
real dataset:

```bash
python src/beginner.py
python src/intermediate.py
python src/advanced.py
```

Expected output begins with `All tests passed!` followed by per-participant
results.

## Project structure

```
matsvei-hemza/
├── data/
│   └── researchdata/         # 12 participant CSV files
├── src/
│   ├── beginner.py           # Analysis 1
│   ├── intermediate.py       # Analysis 2
│   ├── advanced.py           # Analysis 3
│   └── README.md             # Per-analysis specifications
├── requirements.txt
└── README.md
```


**Analysis 1 (Beginner)**


| Field                             | Your answer                                                                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem I want to solve           | Which day of the week is the most active for each participant over the entire observation period?                                                |
| Algorithm I will use              | Single linear pass through all rows: extract weekday from each date, accumulate steps per (participant, weekday) in a nested dict, then scan the 7 weekday totals per participant to find the maximum. |
| Why this algorithm is appropriate | This is a group-by-key aggregation. One pass with dict updates is simple and avoids sorting. The inner scan is always over exactly 7 entries, so it adds negligible cost. |
| Expected time complexity          | O(n) where n is the total number of rows (the per-participant max-scan is O(7) = O(1)).                                                          |
| Expected space complexity         | O(p) where p is the number of participants (each stores 7 integers).                                                                             |
| Minimum tests                     | Normal multi-participant dataset, empty dataset, single-participant single-day dataset, tie between two weekdays.                                |
| Python file                       | [`src/beginner.py`](src/beginner.py)                                                                                                                            |


---

**Analysis 2 (Intermediate)**


| Field                             | Your answer                                                                                                                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem I want to solve           | Does yesterday's physical activity (steps) affect today's sleep duration? For each participant, retrieve (yesterday_steps, today_sleep) pairs and compute their Pearson correlation.                   |
| Algorithm I will use              | Baseline: for each query, scan all rows to find yesterday's steps and today's sleep — O(n) per query. Improved: sort each participant's data by date once, then use binary search to answer each query in O(log n). Correlation is computed in a single O(k) pass. |
| Why this algorithm is appropriate | Repeated lookups by (participant, date) are expensive with full scans. Preprocessing into sorted arrays enables binary search. Pearson correlation needs only running sums, so O(k) with O(1) extra space. |
| Expected time complexity          | Baseline: O(q * n). Improved: preprocessing O(n log n), then O(log n_p) per query. Correlation: O(k) where k = number of consecutive-day pairs.                                                        |
| Expected space complexity         | O(n) for the sorted index (dates + steps + sleep arrays per participant).                                                                                                                              |
| Minimum tests                     | Baseline vs optimized result comparison, empty dataset, gap in dates (no consecutive days should form a pair), known correlation values.                                                               |
| Python file                       | [`src/intermediate.py`](src/intermediate.py)                                                                                                                                                                              |


---

**Analysis 3 (Advanced)**


| Field                             | Your answer                                                                                                                                                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Problem I want to solve           | What is the longest subsequence of days (not necessarily consecutive) where step counts are strictly increasing? This reveals the longest "progress trend" in a participant's activity.                                                    |
| Algorithm I will use              | Baseline: classic O(n^2) DP where `dp[i]` = length of LIS ending at day i, scanning all previous days. Improved: O(n log n) patience sorting — maintain a `tails` array of smallest tail values and use binary search (`bisect_left`) to update it. Backpointers reconstruct the subsequence. |
| Why this algorithm is appropriate | LIS is a classic DP problem with optimal substructure. The O(n^2) baseline is correct but slow for ~290 days per participant; the patience sorting optimization reduces each step to O(log n) via binary search, making it practical and demonstrating a clear algorithmic improvement. |
| Expected time complexity          | Baseline: O(n^2). Improved: O(n log n) where n = number of days for a participant.                                                                                                                                                         |
| Expected space complexity         | O(n) for DP table, predecessor array, and tails array.                                                                                                                                                                                     |
| Minimum tests                     | Standard LIS example, empty input, all-decreasing sequence (LIS = 1), all-increasing sequence (LIS = n), all-equal values (LIS = 1), baseline vs optimized length comparison on mixed data.                                                |
| Python file                       | [`src/advanced.py`](src/advanced.py)                                                                                                                                                                                                                      |
