#!/usr/bin/env bash
# Zig-zag marble-music pipeline (macOS / Linux). Resumable: already-rendered frames are skipped.
# usage: run_zigzag.sh song.mid OUT_DIR START END [FPS] [SAMPLES] [RES] [LOOK=v5] [DEVICE]
# v3+: instrument keep-out check (--strict); v5+: striker clearance check, then titles.py overlay + composite.sh -> *_titled.mp4
# DEVICE also via MARBLE_DEVICE (AUTO|CPU|GPU|METAL|CUDA|OPTIX|HIP). GPU/AUTO: Metal, then OptiX/CUDA/HIP, else CPU.
# BLENDER: default /Applications/Blender.app/Contents/MacOS/Blender if present, otherwise `blender` on PATH.
# SF2: path to GeneralUser GS soundfont (default: alongside this script). PY: python interpreter (default python3).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MID=${1:?midi}; W=${2:?out_dir}; S=${3:-0}; E=${4:-15}; FPS=${5:-30}; SPP=${6:-12}; RES=${7:-1080x1920}; LOOK=${8:-v5}
DEV=${9:-${MARBLE_DEVICE:-AUTO}}
if [[ -z "${BLENDER:-}" ]]; then
  if [[ -x /Applications/Blender.app/Contents/MacOS/Blender ]]; then
    BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
  else
    BLENDER=blender
  fi
fi
SF2=${SF2:-$HERE/GeneralUser.sf2}
PY=${PY:-python3}
F="$W/frames_zz_$LOOK"; PLAN="$W/plan_zz_v2.json"
mkdir -p "$F"
"$PY" "$HERE/extract_hits.py" "$MID" --start "$S" --end "$E" -o "$W/hits.json" >/dev/null
"$PY" "$HERE/plan_zigzag.py" "$W/hits.json" --fps "$FPS" --frame-margin 0.8 -o "$PLAN"
LN=${LOOK#v}
if [ "$LN" -ge 3 ]; then
  "$PY" "$HERE/check_keepout.py" "$PLAN" --look "$LOOK" --out "$W/keepout_report_$LOOK.json" --strict
fi
if [ "$LN" -ge 5 ]; then
  "$PY" "$HERE/check_pairs.py" "$PLAN" --look "$LOOK" --out "$W/pairs_report_$LOOK.json"
fi
[ -f "$W/audio.wav" ] || "$HERE/render_audio.sh" "$MID" "$SF2" "$W/audio.wav" "$S" "$E"
NF=$("$PY" -c "print(int(round(($E-$S)*$FPS))-1)")
"$BLENDER" -b -P "$HERE/scene.py" -- --look "$LOOK" --plan "$PLAN" --out "$F" --start 0 --end "$NF" --samples "$SPP" --res "$RES" --device "$DEV" | grep --line-buffered -E "FRAME|Cycles device|GPU setup"
"$HERE/mux.sh" "$F" "$W/audio.wav" "$FPS" "$W/marble_zigzag_${LOOK}_${S}_${E}.mp4"
"$PY" "$HERE/contact_sheet.py" "$PLAN" "$F" "$W/contact_zigzag_${LOOK}.png" || true
if [ "$LN" -ge 5 ]; then
  "$PY" "$HERE/titles.py" "$PLAN" "$W/overlay_$LOOK" --start 0 --end "$NF"
  PY="$PY" "$HERE/composite.sh" "$F" "$W/overlay_$LOOK" "$W/audio.wav" "$FPS" 0 "$W/marble_zigzag_${LOOK}_${S}_${E}_titled.mp4"
  echo "titled -> $W/marble_zigzag_${LOOK}_${S}_${E}_titled.mp4"
fi
echo "done -> $W/marble_zigzag_${LOOK}_${S}_${E}.mp4"
