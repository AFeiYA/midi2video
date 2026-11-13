#!/usr/bin/env bash
# mux.sh FRAMES_DIR AUDIO.wav FPS OUT.mp4
set -euo pipefail
ffmpeg -v error -y -framerate "$3" -i "$1/%05d.png" -i "$2" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart "$4"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$4"
