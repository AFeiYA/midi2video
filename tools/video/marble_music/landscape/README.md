# 16:9 marble trajectory planner

This prototype generates a single-marble route for the first 10 seconds of the six-instrument Jingle Bells MIDI. The three layouts use the same 23 note onsets. Layout C follows a terraced descent, with lateral reversals and drops between levels.

Run from the repository root with Python, NumPy and mido installed.

```bash
python3 tools/video/marble_music/extract_hits.py \
  projects/jingle-bells-marble-music/source/jingle_remix_6inst_16beat.mid \
  --start 0 --end 10 -o /tmp/marble-landscape-hits.json

python3 tools/video/marble_music/landscape/plan.py \
  /tmp/marble-landscape-hits.json --layout C -o /tmp/marble-landscape-plan.json
```

Use `--layout all` to generate A (long sweep), B (folded return), and C (terraced descent). The JSON records hit times, positions, plate centers and normals, arc velocities, and clearance diagnostics. The viewport is a 16×9 rectangle in world XZ coordinates. The fixed layout anchors are authored for this excerpt.

For each hit, a beam search tests reflected velocities and plate positions under gravity. The score rewards proximity to the layout anchors and penalizes repeated, similar runs. A continuous check evaluates the selected ballistic arcs against capsule proxies for the plates, including minima between frames.

The planner is invoked separately from the portrait pipeline. It does not invoke Blender. The capsule check covers the planned contact geometry. Each final instrument mesh needs a separate check after placement because its decorative body can extend past the proxy.
