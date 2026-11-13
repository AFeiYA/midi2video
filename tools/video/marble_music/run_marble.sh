#!/usr/bin/env bash
# Backward-compatible wrapper (8th argument is still DEVICE). Look comes from LOOK= (default v5).
# usage: run_marble.sh song.mid OUT_DIR START END [FPS] [SAMPLES] [RES] [DEVICE]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MID=${1:?midi}; W=${2:?out_dir}; S=${3:-0}; E=${4:-15}; FPS=${5:-30}; SPP=${6:-12}; RES=${7:-1080x1920}
DEV=${8:-${MARBLE_DEVICE:-AUTO}}
LOOK=${LOOK:-v5}
exec "$HERE/run_zigzag.sh" "$MID" "$W" "$S" "$E" "$FPS" "$SPP" "$RES" "$LOOK" "$DEV"
