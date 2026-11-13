# Marble Music（Z 字形）— MIDI 驱动的弹珠音乐 3D 动画

参考：Virtual 3D《iPhone Ringtone - Marble Music》。弹珠在左右交替的斜挡板之间来回碰撞下落，每次碰撞精确落在一个 MIDI 音符的帧上。

当前默认外观是 **v3**（工作室灯光 + 12 种程序化乐器击打件）。`--look v2` 只用材质挡板，`--look v1` 还原已认可的 15 秒小样。所有乐器模型都是本仓库自己的程序化几何，没有第三方模型版权问题。

> 规划器和场景脚本不再写死机器路径。MIDI、输出目录用参数传入；Blender 用环境变量 `BLENDER`；计算设备用 `--device` 或 `MARBLE_DEVICE`。

## 1. 安装

在仓库根目录操作（克隆见文末快速开始）。需要：

- **Python 3**：`pip install mido numpy pillow matplotlib`
- **Blender 4.2+**（ macOS 安装后一般是 `/Applications/Blender.app/Contents/MacOS/Blender`）
  - 本管线在 **Blender 4.2.3 LTS** 上开发并验证。
  - **Blender 5.x**（例如本机的 5.3）可以用来渲染：程序化建场景，不依赖 4.2 的 `.blend` 缓存。注意下面的兼容说明。
- **ffmpeg**
- **FluidSynth** + **GeneralUser GS** 音色库（约 30MB，未入库）
  - 下载：https://schristiancollins.com/generaluser.php
  - 保存为 `tools/video/marble_music/GeneralUser.sf2`，或设置 `SF2=/path/to/GeneralUser.sf2`

macOS 可用 Homebrew：

```bash
brew install python ffmpeg fluid-synth
# Blender 5.3 若已安装在 /Applications 则可直接用；否则从 https://www.blender.org 安装 4.2+ 或 5.x
```

环境变量：

| 变量 | 含义 | 默认 |
|---|---|---|
| `BLENDER` | Blender 可执行文件 | 若存在则用 `/Applications/Blender.app/Contents/MacOS/Blender`，否则 `blender`（需在 PATH 中） |
| `MARBLE_DEVICE` | Cycles 设备：`AUTO`/`GPU`/`CPU`/`METAL`/`CUDA`/`OPTIX`/`HIP` | `AUTO`（`GPU` 等同 `AUTO`：先 Metal，再 OptiX/CUDA/HIP，没有则回退 CPU） |
| `SF2` | Soundfont 路径 | `tools/video/marble_music/GeneralUser.sf2` |
| `PY` | Python 解释器 | `python3` |
| `LOOK` | 仅 `run_marble.sh`：外观版本 | `v3` |

### Blender 5.x 兼容说明

- **不要用 4.2 打开 5.x 另存的 `.blend`**：5.0 起 blend 格式与 4.2 不兼容。`scene.py` 每次都是程序化建场景，渲染本身不受影响。`model.blend` / `model.glb` 只是缓存，可用当前 Blender 重新生成：
  `$BLENDER -b -P tools/video/marble_music/assets/instruments/build_library.py`
- 布尔引擎：4.2 用 `EXACT`，4.5/5.x 已改为 `MANIFOLD`，脚本会自动回退。
- 按角度平滑：4.x 用 `shade_smooth_by_angle`，5.x 可能要用 `shade_auto_smooth`，脚本会自动回退。
- Blender 5 的工作色域默认可能不再是 Linear Rec.709，同一帧的颜色会和 4.2 参考图有细微差别。若要对齐参考，可在 Blender 里把 Working Space 设为 Linear Rec.709 再渲。
- macOS：官方 Blender 5.0+ 只支持 Apple Silicon，不再提供 Intel Mac 安装包。
- 全片如果 4.2 和 5.3 混渲，建议先对比同一帧再拼接。

## 2. 运行顺序

以 Jingle Bells 全曲（`projects/jingle-bells-marble-music/source/jingle.mid`，约 176.3 秒，30 fps）为例。建议在仓库根目录执行。

1. **提取击打点** `extract_hits.py`：读 MIDI，建立 tempo map，只取 `01.`–`12.` 主旋律轨（13–16 伴奏只出声不出画），60ms 内叠音合并为一次击打（取最高音）。
2. **逆向规划轨迹** `plan_zigzag.py`：先定时间再反推几何；左右交替挡板；段间是抛物线；挡板法线为入射反向与出射方向的角平分线。全曲规划约 0 次穿模。
3. **禁入检查** `check_keepout.py`：用资产库表面采样点检查装饰几何、销钉是否侵入弹道（v3 必做，`--strict` 有违规会退出）。
4. **渲 12 张乐器静帧**（材质/外形确认）：帧号为各段落中段的击打帧。
5. **渲 15 秒小样**，再合成音频、出接触点拼图。
6. **全曲渲染**（可断点续渲，已有帧会跳过），然后 `mux.sh` 合成。

规划器可调参数：`--g` 重力，`--half-gap` 左右间距，`--drop-rate` 最大下落速度，`--frac` 弹跳高度系数（越小越平），`--frame-margin` 镜头跟随裕度（v2/v3 用 0.8）。

## 3. 具体命令

先设置 Blender 和设备（macOS Metal GPU 示例）：

```bash
export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
export MARBLE_DEVICE=GPU          # 或 METAL；没有 GPU 时改 CPU
export SF2=tools/video/marble_music/GeneralUser.sf2   # 若音色库不在默认位置
mkdir -p work
```

### 3.1 提取击打、规划、禁入检查

```bash
python3 tools/video/marble_music/extract_hits.py \
  projects/jingle-bells-marble-music/source/jingle.mid \
  --start 0 --end 176.3 -o work/hits.json

python3 tools/video/marble_music/plan_zigzag.py \
  work/hits.json --fps 30 --frame-margin 0.8 -o work/plan_zz_v2.json

python3 tools/video/marble_music/check_keepout.py \
  work/plan_zz_v2.json --out work/keepout_report.json --strict
```

可选：画出整条轨迹总览 `python3 tools/video/marble_music/plot_trajectory.py work/plan_zz_v2.json work/trajectory.png`

### 3.2 十二张乐器静帧（推荐先做）

帧号对应 12 个乐器段落的中段击打：响板 73、钢琴 257、电颤琴 597、管钟 1010、马林巴 1460、卡林巴 1763、长笛 2186、木琴 2654、陶笛 3086、钟琴 3655、钢鼓 4280、吉他 4895。

```bash
mkdir -p work/stills_v3
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v3 \
  --plan work/plan_zz_v2.json \
  --out work/stills_v3 \
  --frames 73,257,597,1010,1460,1763,2186,2654,3086,3655,4280,4895 \
  --samples 12 --res 1080x1920 --device "${MARBLE_DEVICE:-GPU}"

python3 tools/video/marble_music/instrument_sheet.py \
  work/plan_zz_v2.json work/stills_v3 work/instrument_stills_v3.png
```

只渲其中一张（例如钢琴，低采样试跑）：

```bash
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v3 --plan work/plan_zz_v2.json --out work/stills_v3 \
  --frames 257 --samples 4 --res 540x960 --device "${MARBLE_DEVICE:-GPU}"
```

### 3.3 15 秒小样

```bash
tools/video/marble_music/run_zigzag.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 \
  0 15 30 12 1080x1920 v3 "${MARBLE_DEVICE:-GPU}"
# 输出：.../om_zigzag_0_15/marble_zigzag_v3_0_15.mp4
```

或用旧入口（第 8 个参数仍是设备；外观用 `LOOK=v3`，默认就是 v3）：

```bash
LOOK=v3 tools/video/marble_music/run_marble.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 \
  0 15 30 12 1080x1920 "${MARBLE_DEVICE:-GPU}"
```

### 3.4 全曲渲染再合成

```bash
# 前台（可随时 Ctrl-C，下次会跳过已有帧）
tools/video/marble_music/run_zigzag.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_full \
  0 176.3 30 12 1080x1920 v3 "${MARBLE_DEVICE:-GPU}"

# 或后台启动 / 续渲
tools/video/marble_music/resume_full.sh v3
# 日志：projects/jingle-bells-marble-music/om_zigzag_full/render_v3.log
```

若只想把已渲好的帧和音频合成（默认 `render_audio.sh` 会在流水线里自动做）：

```bash
tools/video/marble_music/mux.sh \
  projects/jingle-bells-marble-music/om_zigzag_full/frames_zz_v3 \
  projects/jingle-bells-marble-music/om_zigzag_full/audio.wav \
  30 \
  projects/jingle-bells-marble-music/om_zigzag_full/marble_zigzag_v3_0_176.3.mp4
```

## 4. 做法说明（4 步）

1. **提取击打点** `extract_hits.py` — 见上文。
2. **逆向规划轨迹** `plan_zigzag.py` — 向量化碰撞检测；输出每帧弹珠位置、挡板位姿、相机路径到 `plan_zz_v2.json`。
3. **Blender 渲染** `scene.py` — 程序化建场景：灰墙、翡翠绿玻璃弹珠、柔光；v3 从 `assets/instruments/` 实例化 12 种击打件；击打帧挡板下沉 + 边缘闪光；相机平滑下摇。Cycles + OIDN + 运动模糊 + AgX。已存在且大于 1KB 的帧自动跳过。
4. **音频与合成** `render_audio.sh` + `mux.sh` — FluidSynth + GeneralUser GS 把整份 MIDI（全部 17 轨）合成 48k WAV 并裁到同一时间窗；ffmpeg 合成 H.264 + AAC。

升级路线和特效规划见同目录 `UPGRADE_PLAN.md`。历史脚本 `scene_zigzag.py` 是最早的 v1 快照，新流程请用 `scene.py`。

## 快速开始（Mac 本机）

```bash
git clone https://github.com/AFeiYA/midi2video.git
cd midi2video
pip install mido numpy pillow matplotlib
brew install ffmpeg fluid-synth
# 下载 GeneralUser GS 为 tools/video/marble_music/GeneralUser.sf2
# https://schristiancollins.com/generaluser.php

export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
export MARBLE_DEVICE=GPU
mkdir -p work

python3 tools/video/marble_music/extract_hits.py \
  projects/jingle-bells-marble-music/source/jingle.mid \
  --start 0 --end 176.3 -o work/hits.json
python3 tools/video/marble_music/plan_zigzag.py \
  work/hits.json --fps 30 --frame-margin 0.8 -o work/plan_zz_v2.json
python3 tools/video/marble_music/check_keepout.py \
  work/plan_zz_v2.json --out work/keepout_report.json --strict

# 12 张乐器静帧
mkdir -p work/stills_v3
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v3 --plan work/plan_zz_v2.json --out work/stills_v3 \
  --frames 73,257,597,1010,1460,1763,2186,2654,3086,3655,4280,4895 \
  --samples 12 --res 1080x1920 --device GPU

# 15 秒小样
tools/video/marble_music/run_zigzag.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 \
  0 15 30 12 1080x1920 v3 GPU
```
