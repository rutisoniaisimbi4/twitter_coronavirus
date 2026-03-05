#!/usr/bin/env bash
set -euo pipefail

# Always run from the directory where this script lives (the repo root)
cd "$(dirname "$0")"

DATA_DIR="/data/Twitter dataset"
OUT_DIR="outputs"
LOG_DIR="logs"

mkdir -p "$OUT_DIR" "$LOG_DIR"

MAX_JOBS=2

for zip in "$DATA_DIR"/geoTwitter20-*.zip; do
  base="$(basename "$zip")"

  # skip if outputs already exist
  if [[ -f "$OUT_DIR/$base.lang" && -f "$OUT_DIR/$base.country" ]]; then
    echo "SKIP $base (already done)"
    continue
  fi

  # throttle number of concurrent mappers
  while [[ $(pgrep -u "$USER" -f "python3 src/map.py" | wc -l) -ge $MAX_JOBS ]]; do
    sleep 2
  done

  echo "START $base"
  nohup python3 src/map.py --input_path "$zip" --output_folder "$OUT_DIR" \
    > "$LOG_DIR/$base.log" 2>&1 &
done

echo "Launched all jobs; mapping continues in background."
