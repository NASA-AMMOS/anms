"""Shared helpers for stress-test-detailed.sh Python scripts."""

import statistics


def compute_percentiles(latencies, pcts=(0.5, 0.95, 0.99)):
    """Return sorted percentiles for a latency list.

    Returns an empty list for every requested percentile when *latencies* is
    empty — callers must check the list length before using the results.
    """
    s = sorted(latencies)
    if not s:
        return []
    return [
        round(s[min(int(len(s) * pct), len(s) - 1)] * 1000, 1)
        for pct in pcts
    ]


def safe_mean(values):
    """Return the mean of *values* or 0 if the list is empty."""
    return statistics.mean(values) if values else 0


def safe_throughput(success, elapsed):
    """Return requests-per-second or 0 when elapsed is zero."""
    if elapsed <= 0:
        return 0.0
    return round(success / elapsed, 1)
