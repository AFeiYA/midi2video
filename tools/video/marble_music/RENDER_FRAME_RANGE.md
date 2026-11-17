# 渲染指定帧区间

适用于 `adjust/v5` 上的 Marble Music。命令从仓库根目录运行。

## 渲染第 400 到 428 帧

用原来渲染时的 `plan_zz_v2.json`，这样弹珠轨迹、镜头和帧编号都能与原序列对齐。把下面的 `PLAN` 改成实际的规划文件路径。

```bash
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
PLAN="work/plan_zz_v2.json"
OUT="work/frames_00400_00428_v5"

"$BLENDER" -b --python-exit-code 1 -P tools/video/marble_music/scene.py -- \
  --plan "$PLAN" --out "$OUT" --look v5 \
  --start 400 --end 428 \
  --samples 12 --res 1080x1920 --device "${MARBLE_DEVICE:-GPU}"
```

- `--start` 和 `--end` 都包含在内。这段共 29 帧，输出从 `00400.png` 到 `00428.png`。
- 帧号从 `0` 开始，沿用该计划的时间轴。省略 `--end` 会渲到计划最后一帧。
- 抽查几张时，改用 `--frames 400,414,428`。如果同时提供区间参数，脚本优先使用帧列表。只渲一张用 `--frames 428`。
- 这条命令输出 PNG 序列。字幕、音频和 MP4 由后续合成步骤生成。
- 如果 Blender 在 `PATH` 中，可先运行 `export BLENDER=blender`。横版可指定 `--res 1920x1080`；补全原序列时请沿用原来的分辨率、外观、采样数和 Blender 版本。

## 补帧与重渲

- **继续渲染或补缺帧**：将 `OUT` 设为原序列目录，再运行同一命令。已有且大于 1000 字节的同名 PNG 会被跳过，日志显示 `FRAME 428 skip`。跳过条件只检查文件大小。
- **改了材质、灯光或渲染设置**：使用新的输出目录，保证整段都按新设置渲染。也可先移走原目录中要重做的那几帧，再写回原目录。

## 确认秒数对应的帧号

在计划时间轴上，第 `f` 帧对应 `f / FPS` 秒。例如，30 fps 时，时间段 `[10, 12)` 包含第 300 到 359 帧，共 60 帧。若规划时从 MIDI 的第 10 秒开始截取，计划的第 0 帧就对应原曲第 10 秒。

用下面的命令查看计划的实际 FPS 和有效帧号：

```bash
python3 - "$PLAN" <<'PY'
import json
import sys

with open(sys.argv[1]) as plan_file:
    plan = json.load(plan_file)
print(f"FPS = {plan['fps']}")
print(f"Frames = 0–{len(plan['marble']) - 1}")
PY
```

## 手里只有 MIDI 时

例如，为仓库里的 Jingle Bells 生成从歌曲开头算起的 30 fps 计划，再渲染其中一段：

```bash
mkdir -p work
python3 tools/video/marble_music/extract_hits.py \
  projects/jingle-bells-marble-music/source/jingle.mid \
  --start 0 --end 176.3 -o work/hits.json

python3 tools/video/marble_music/fix_clearance.py \
  work/hits.json --fps 30 --frame-margin 0.8 --look v5 \
  -o work/plan_zz_v2.json
```

规划依赖和合成命令见 [Marble Music README](README.md)。`extract_hits.py` 和 `run_zigzag.sh` 接收的是 MIDI 时间（秒），上面的 `scene.py --start/--end` 接收的是计划中的帧号。

## 片尾鼓提前固定在场景里

`scene.py` 搭建场景时，只有计划包含 `ending` 数据才会创建片尾鼓。制作带片尾鼓的版本时，先用 `ending.py` 生成带片尾的完整计划，再用同一份计划渲染整条序列。这样鼓从第 0 帧就固定在世界坐标里，等镜头下移时自然入画，碰撞帧再触发下沉和闪光。

补渲已完成的片尾时，沿用该版本已有的 `plan_zz_v2_end.json`。例如 Jingle Bells 这版，用它渲染整个第 5216–5304 帧区间。第 5253 帧是最后一次乐器击打，第 5269 帧是弹珠落鼓。第 5254 帧是片尾轨迹开始的时间，场景在这之前也需要有鼓。如果现有第 5254–5304 帧已用同一份片尾计划和相同设置渲完，只需补渲第 5216–5253 帧。

```bash
PLAN="/path/to/om_remix_full_1080x1920/plan_zz_v2_end.json"
OUT="work/ending_corrected"

"$BLENDER" -b --python-exit-code 1 -P tools/video/marble_music/scene.py -- \
  --plan "$PLAN" --out "$OUT" --look v5 \
  --start 5216 --end 5304 \
  --samples 8 --res 1080x1920 --device "${MARBLE_DEVICE:-GPU}"
```
