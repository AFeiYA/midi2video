#!/usr/bin/env bash
# Zig-zag marble-music pipeline (macOS / OpenMontage). Resumable: already-rendered frames are skipped.
# usage: tools/video/marble_music/run_marble.sh song.mid OUT_DIR START END [FPS] [SAMPLES] [RES] [DEVICE]
# e.g.   tools/video/marble_music/run_marble.sh projects/jingle-bells-marble-music/source/jingle.mid projects/jingle-bells-marble-music/om_zigzag_0_15 0 15
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MID=${1:?midi}; W=${2:?out_dir}; S=${3:-0}; E=${4:-15}; FPS=${5:-30}; SPP=${6:-12}; RES=${7:-1080x1920}; DEV=${8:-AUTO}
BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
SF2=${SF2:-$HERE/GeneralUser.sf2}
PY=${PY:-python3}
mkdir -p "$W/frames"
$PY "$HERE/extract_hits.py" "$MID" --start "$S" --end "$E" -o "$W/hits.json" >/dev/null
$PY "$HERE/plan_zigzag.py" "$W/hits.json" --fps "$FPS" -o "$W/plan.json"
[ -f "$W/audio.wav" ] || "$HERE/render_audio.sh" "$MID" "$SF2" "$W/audio.wav" "$S" "$E"
NF=$($PY -c "print(int(round(($E-$S)*$FPS))-1)")
"$BLENDER" -b -P "$HERE/scene_zigzag.py" -- --plan "$W/plan.json" --out "$W/frames" --start 0 --end "$NF" --samples "$SPP" --res "$RES" --device "$DEV" | grep --line-buffered -E "FRAME|Cycles device|GPU setup"
"$HERE/mux.sh" "$W/frames" "$W/audio.wav" "$FPS" "$W/marble_zigzag_${S}_${E}.mp4"
$PY "$HERE/contact_sheet.py" "$W/plan.json" "$W/frames" "$W/contact.png" || true
echo "done -> $W/marble_zigzag_${S}_${E}.mp4"
