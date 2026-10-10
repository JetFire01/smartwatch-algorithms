# smartwatch-algorithms

Algorithmic analysis of daily activity and sleep data from Withings smartwatches
(12 participants, ~290 days each): steps, distance, heart rate and sleep metrics.

Course project for **Algorithmics** (Algorithmique), University of Geneva, Spring 2026.

The project contains three analyses of increasing complexity, each comparing a
baseline solution with an optimized one:

| Level        | File                                             | Question                                         | Algorithms                                   |
| ------------ | ------------------------------------------------ | ------------------------------------------------ | -------------------------------------------- |
| Beginner     | [`src/beginner.py`](src/beginner.py)             | Which weekday is the most active per participant? | O(n) group-by aggregation                    |
| Intermediate | [`src/intermediate.py`](src/intermediate.py)     | Does yesterday's activity affect today's sleep?  | O(n) scan vs. O(log n) binary search, Pearson correlation |
| Advanced     | [`src/advanced.py`](src/advanced.py)             | Longest strictly increasing trend in daily steps | O(n²) DP vs. O(n log n) patience sorting (LIS) |

Detailed specifications for each analysis (problem, algorithm, complexity, tests)
are at the [end of this file](#analysis-specifications).

## Dataset

> **The dataset is not included in this repository.** It contains health data
> (heart rate, sleep) of real study participants and was provided for the course
> only.

The scripts expect one CSV file per participant in `data/researchdata/`,
named `<participant_id>.csv`, with a header such as:

```
DATE,DAY_OF_THE_WEEK,MONTH,SEASON,ACTIVITY_steps,ACTIVITY_distance,...,SLEEP_totalsleeptime,...
06.07.21,1,6,0,2584,1841,...,24960,...
```

`DATE` is in `DD.MM.YY` format. If you have access to the data, place the files
there; the folder is listed in `.gitignore`.

## Requirements

- **Python 3.9 or newer** (the code uses PEP 585 generic types like `list[int]`).
- No third-party packages: every script uses the Python standard library only.

## Getting started

```bash
git clone git@github.com:JetFire01/smartwatch-algorithms.git
cd smartwatch-algorithms

python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows
```

## Running the analyses

Each script runs its inline tests first and then prints results from the dataset:

```bash
python src/beginner.py
python src/intermediate.py
python src/advanced.py
```

Expected output begins with `All tests passed!` followed by per-participant
results. Without the dataset the tests still run, and the script then reports
that no data was loaded.

## Project structure

```
smartwatch-algorithms/
├── data/
│   └── researchdata/         # participant CSV files (not tracked)
├── src/
│   ├── beginner.py           # Analysis 1
│   ├── intermediate.py       # Analysis 2
│   └── advanced.py           # Analysis 3
├── requirements.txt
└── README.md
```

## Analysis specifications

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
