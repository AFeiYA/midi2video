#!/usr/bin/env bash
# render_audio.sh song.mid soundfont.sf2 out.wav START END  -- FluidSynth render, then trim to [START,END]
set -euo pipefail
TMP=$(mktemp -t marble).wav
fluidsynth -ni -g 0.8 -r 48000 -F "$TMP" "$2" "$1" >/dev/null
ffmpeg -v error -y -ss "$4" -to "$5" -i "$TMP" -ar 48000 -ac 2 "$3"; rm -f "$TMP"
