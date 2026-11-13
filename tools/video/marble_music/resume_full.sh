#!/usr/bin/env bash
# Start/resume a long render in the background. Already-rendered frames are skipped by scene.py.
# usage: resume_full.sh [LOOK=v3] [MIDI] [OUT_DIR] [START] [END] [FPS] [SAMPLES] [RES] [DEVICE]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
LOOK=${1:-v3}
MIDI=${2:-$ROOT/projects/jingle-bells-marble-music/source/jingle.mid}
OUT=${3:-$ROOT/projects/jingle-bells-marble-music/om_zigzag_full}
S=${4:-0}; E=${5:-176.3}; FPS=${6:-30}; SPP=${7:-12}; RES=${8:-1080x1920}
DEV=${9:-${MARBLE_DEVICE:-AUTO}}
LOG="$OUT/render_${LOOK}.log"
mkdir -p "$OUT"
if pgrep -f "scene.py.*$(basename "$OUT")" >/dev/null 2>&1; then
  echo already running
  exit 0
fi
nohup "$HERE/run_zigzag.sh" "$MIDI" "$OUT" "$S" "$E" "$FPS" "$SPP" "$RES" "$LOOK" "$DEV" >> "$LOG" 2>&1 < /dev/null &
echo "started ($LOOK) pid $! -> tail -f $LOG"
