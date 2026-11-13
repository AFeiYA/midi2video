#!/usr/bin/env bash
# composite.sh FRAMES_DIR OVERLAY_DIR AUDIO.wav FPS START_FRAME OUT.mp4
# v5 compositing pass: Blender frames (any resolution, upscaled to the overlay size with lanczos) + titles.py RGBA overlays
# (same %05d numbering; PY = python with Pillow, default python3) + the matching audio segment (audio.wav covers the whole song from t=0, so it is trimmed at START/FPS).
# Label tweaks only need titles.py + this script - no re-render.
set -euo pipefail
FR="$1"; OV="$2"; AU="$3"; FPS="$4"; S="$5"; OUT="$6"
read OW OH < <("${PY:-python3}" -c "import glob;from PIL import Image;f=sorted(glob.glob('$OV/*.png'))[0];print(*Image.open(f).size)" 2>/dev/null || echo "1080 1920")
N=$(ls "$FR" | grep -c '\.png$')
SS=$("${PY:-python3}" -c "print($S/$FPS)"); DUR=$("${PY:-python3}" -c "print($N/$FPS)")
ffmpeg -v error -y -framerate "$FPS" -start_number "$S" -i "$FR/%05d.png" -framerate "$FPS" -start_number "$S" -i "$OV/%05d.png" \
  -ss "$SS" -t "$DUR" -i "$AU" \
  -filter_complex "[0:v]scale=${OW}:${OH}:flags=lanczos[b];[b][1:v]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 256k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT"
