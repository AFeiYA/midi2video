#!/usr/bin/env bash
# render_audio.sh song.mid soundfont.sf2 out.wav START END  -- FluidSynth render, then trim to [START,END]
set -euo pipefail
if [ ! -f "$2" ]; then
  echo "找不到音色库: $2" >&2
  echo "请下载 GeneralUser GS（https://schristiancollins.com/generaluser.php），保存为该路径，或设置 SF2=/path/to/GeneralUser.sf2" >&2
  exit 1
fi
TMP=$(mktemp "${TMPDIR:-/tmp}/marble.XXXXXX").wav
fluidsynth -ni -g 0.8 -r 48000 -F "$TMP" "$2" "$1" >/dev/null
ffmpeg -v error -y -ss "$4" -to "$5" -i "$TMP" -ar 48000 -ac 2 "$3"
rm -f "$TMP"
