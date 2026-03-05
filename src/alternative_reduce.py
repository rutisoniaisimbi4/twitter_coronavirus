#!/usr/bin/env python3

import argparse
import os
import re
import json
import glob
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--hashtags', nargs='+', required=True,
                    help='List of hashtags to plot, e.g. --hashtags "#coronavirus" "#flu"')
parser.add_argument('--input_folder', default='outputs',
                    help='Folder containing .lang output files from map.py')
args = parser.parse_args()

hashtags = [h.lower() for h in args.hashtags]
series = defaultdict(lambda: defaultdict(int))

pattern = os.path.join(args.input_folder, 'geoTwitter20-*.zip.lang')
files = sorted(glob.glob(pattern))

if not files:
    raise SystemExit(f"No .lang files found in {args.input_folder}. Check --input_folder.")

for path in files:
    basename = os.path.basename(path)
    m = re.search(r'geoTwitter(\d{2})-(\d{2})-(\d{2})\.zip', basename)
    if not m:
        continue
    yy, mm, dd = m.group(1), m.group(2), m.group(3)
    date = datetime.date(2000 + int(yy), int(mm), int(dd))

    with open(path, encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            continue

    for hashtag in hashtags:
        if hashtag in data:
            daily_total = sum(data[hashtag].values())
            series[hashtag][date] += daily_total

fig, ax = plt.subplots(figsize=(14, 6))

for hashtag in hashtags:
    if not series[hashtag]:
        print(f"Warning: no data found for {hashtag!r}, skipping.")
        continue
    sorted_days = sorted(series[hashtag].keys())
    counts = [series[hashtag][d] for d in sorted_days]
    ax.plot(sorted_days, counts, label=hashtag, linewidth=1.5)

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_xlabel('Month (2020)')
ax.set_ylabel('Number of Tweets')
ax.set_title('Hashtag Usage Over Time (2020)')
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout()

def safe_name(s):
    s = s.strip().replace('#', 'hash_')
    return re.sub(r'[^A-Za-z0-9_\-]+', '_', s)

out_name = 'alternative_reduce_' + '_'.join(safe_name(h) for h in hashtags) + '.png'
plt.savefig(out_name, dpi=200)
print("saved", out_name)
