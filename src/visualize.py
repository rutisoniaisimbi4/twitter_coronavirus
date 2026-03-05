#!/usr/bin/env python3

import argparse
import json
import os
import re
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--input_path', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--percent', action='store_true',
                    help='If set, normalize by counts["_all"][subkey] when available (lang plots).')
parser.add_argument('--topk', type=int, default=10)
args = parser.parse_args()

with open(args.input_path, encoding="utf-8") as f:
    counts = json.load(f)

if args.key not in counts:
    available = sorted(counts.keys())
    raise SystemExit(f'Key {args.key!r} not found. Available keys include: {available[:30]}')

series = counts[args.key]  # dict: {subkey: value}

# Optional normalization (only if _all exists and has matching subkeys)
if args.percent:
    if "_all" not in counts:
        raise SystemExit("Cannot use --percent because this file has no '_all' key.")
    all_counts = counts["_all"]
    normalized = {}
    for subk, v in series.items():
        denom = all_counts.get(subk, 0)
        if denom:
            normalized[subk] = v / denom
        else:
            # if denom missing/zero, skip to avoid division-by-zero nonsense
            continue
    series = normalized

items = sorted(series.items(), key=lambda kv: kv[1])  # low -> high
items = items[-args.topk:]                             # keep topK

labels = [k for k, _ in items]
values = [v for _, v in items]

plt.figure(figsize=(12, 6))
plt.bar(labels, values)
plt.xticks(rotation=45, ha="right")
plt.ylabel("Percent" if args.percent else "Count")
plt.title(f"Top {len(items)} for {args.key}")
plt.tight_layout()

def safe_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", "_", s)
    s = s.replace("#", "hash_")
    s = re.sub(r"[^A-Za-z0-9_\-]+", "_", s)
    return s

base = os.path.basename(args.input_path)
suffix = "percent" if args.percent else "count"
out_name = f"{safe_name(args.key)}_{suffix}_{base}.png"
plt.savefig(out_name, dpi=200)
print("saved", out_name)
