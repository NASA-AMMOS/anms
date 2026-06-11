#!/usr/bin/env python3
"""Phase D (part 2): Container Stats Processor.

Reads raw ``docker stats --no-stream`` output and computes per-container
peak CPU, memory, and network I/O.

Usage:
    python3 stress_container_stats.py <raw_stats_file> <metrics_dir>

Input file format (pipe-delimited, from docker stats --no-stream --format):
    <Name>|<CPUPerc>|<MemUsage>|<MemPerc>|<NetIO>|<BlockIO>

Example line:
    anms-core-1|2.35%|45.23MiB / 1.953GiB|2.28|1.2MB / 4.09MB|0B / 0B
"""

import json
import os
import sys


def parse_io(s):
    """Convert a docker stats IO string (e.g. '1.2MB') to megabytes."""
    s = s.strip()
    if not s:
        return 0.0
    try:
        if "GB" in s:
            return float(s.replace("GB", "").strip()) * 1024
        if "MB" in s:
            return float(s.replace("MB", "").strip())
        if "kB" in s:
            return float(s.replace("kB", "").strip()) / 1024
        if "B" in s:
            return float(s.replace("B", "").strip()) / (1024 * 1024)
    except ValueError:
        pass
    return 0.0


def main():
    raw_file = sys.argv[1]
    metrics_dir = sys.argv[2]

    peak = {}
    net_peak = {}
    counts = {}

    with open(raw_file) as f:
        for line in f:
            p = line.strip().split("|")
            if len(p) != 6:
                continue
            name = p[0]
            try:
                cpu_v = float(p[1].replace("%", ""))
                mem_pct = float(p[3].replace("%", ""))
                net = p[4]  # "1.2MB / 4.09MB"
                # block = p[5]  # unused

                counts[name] = counts.get(name, 0) + 1
                if name not in peak or cpu_v > peak[name][0]:
                    peak[name] = (cpu_v, p[2], mem_pct)

                # Parse net I/O
                net_parts = net.split("/")
                net_in = parse_io(net_parts[0]) if len(net_parts) > 0 else 0
                net_out = parse_io(net_parts[1]) if len(net_parts) > 1 else 0

                if name not in net_peak or net_in > net_peak[name][0]:
                    net_peak[name] = (net_in, net_out)
            except (ValueError, IndexError):
                continue

    # Write peak stats (one JSON object per line)
    with open(os.path.join(metrics_dir, "container_stats.json"), "w") as f:
        for n in sorted(peak, key=lambda k: peak[k][0], reverse=True):
            json.dump(
                {
                    "container": n,
                    "peak_cpu": round(peak[n][0], 1),
                    "samples": counts.get(n, 0),
                    "peak_mem_raw": peak[n][1],
                    "peak_mem_pct": round(peak[n][2], 1),
                    "peak_net_in_mb": round(
                        net_peak.get(n, (0, 0))[0], 2
                    ),
                    "peak_net_out_mb": round(
                        net_peak.get(n, (0, 0))[1], 2
                    ),
                },
                f,
            )
            f.write("\n")

    # Print summary
    print("  Peak container resources during sustained load:")
    print(
        f"  {'Container':<35} {'CPU%':>6} {'Samples':>8}"
        f" {'Mem%':>6} {'NetIn MB':>10} {'NetOut MB':>10}"
    )
    for n in sorted(peak, key=lambda k: peak[k][0], reverse=True):
        np = net_peak.get(n, (0, 0))
        print(
            f"  {n:<35} {peak[n][0]:>5.1f}%"
            f" {counts.get(n, 0):>8}"
            f" {peak[n][2]:>5.1f}%"
            f" {np[0]:>10.2f}"
            f" {np[1]:>10.2f}"
        )


if __name__ == "__main__":
    main()
