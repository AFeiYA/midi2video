#!/usr/bin/env bash
# Backward-compatible wrapper (8th argument is still DEVICE). Look comes from LOOK= (default v5).
# usage: run_marble.sh song.mid OUT_DIR START END [FPS] [SAMPLES] [RES] [DEVICE] [--intro] [--outro]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MID=${1:?midi}; W=${2:?out_dir}; S=${3:-0}; E=${4:-15}
shift "$(($# < 4 ? $# : 4))"
FPS=30; SPP=12; RES=1080x1920; DEV=${MARBLE_DEVICE:-AUTO}
for option in FPS SPP RES DEV; do
  if [[ $# -eq 0 || "$1" == --* ]]; then break; fi
  if [[ -n "$1" ]]; then printf -v "$option" '%s' "$1"; fi
  shift
done
LOOK=${LOOK:-v5}
exec "$HERE/run_zigzag.sh" "$MID" "$W" "$S" "$E" "$FPS" "$SPP" "$RES" "$LOOK" "$DEV" "$@"
