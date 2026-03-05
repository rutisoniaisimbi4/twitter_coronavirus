#!/usr/bin/env python3

import argparse
import os
import zipfile
import datetime
import json
from collections import Counter, defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--input_path', required=True)
parser.add_argument('--output_folder', default='outputs')
args = parser.parse_args()

# Load hashtags from file (per assignment spec)
with open("hashtags", "r", encoding="utf-8") as f:
    hashtags = [line.strip().lower() for line in f if line.strip()]

counter_lang = defaultdict(Counter)
counter_country = defaultdict(Counter)

with zipfile.ZipFile(args.input_path) as archive:
    for filename in archive.namelist():
        print(datetime.datetime.now(), args.input_path, filename)

        with archive.open(filename) as f:
            for line in f:
                try:
                    tweet = json.loads(line)
                except Exception:
                    continue

                text = (tweet.get("text") or "").lower()
                lang = tweet.get("lang", "und")

                country = "unknown"
                place = tweet.get("place")
                if isinstance(place, dict):
                    country = place.get("country_code", "unknown") or "unknown"

                # Count ALL tweets once per tweet (not once per hashtag)
                counter_lang["_all"][lang] += 1

                # Count tracked hashtags
                for hashtag in hashtags:
                    if hashtag in text:
                        counter_lang[hashtag][lang] += 1
                        counter_country[hashtag][country] += 1

os.makedirs(args.output_folder, exist_ok=True)
output_path_base = os.path.join(args.output_folder, os.path.basename(args.input_path))

output_path_lang = output_path_base + ".lang"
print("saving", output_path_lang)
with open(output_path_lang, "w", encoding="utf-8") as f:
    json.dump(counter_lang, f, ensure_ascii=False)

output_path_country = output_path_base + ".country"
print("saving", output_path_country)
with open(output_path_country, "w", encoding="utf-8") as f:
    json.dump(counter_country, f, ensure_ascii=False)
