# Marble Music（Z 字形）— MIDI 驱动的弹珠音乐 3D 动画

参考：Virtual 3D《iPhone Ringtone - Marble Music》。弹珠在左右交替的斜挡板之间来回碰撞下落，每次碰撞精确落在一个 MIDI 音符的帧上。

当前默认外观是 **v5**（“一眼认出乐器”版）：

- **乐器轮廓**：在弹珠平面之后（y>0.155，弹珠永远碰不到的区域）加了大块可辨认的轮廓：吉他琴身+音孔+琴颈+琴头、卡林巴长短不一的扇形琴键+木板、钢鼓正面圆盘和音区凹坑、管钟竖直悬挂的 5 根铜管、钟琴红色梯形琴箱+多根钢条、陶笛加大的红薯形+吹口、长笛的笛头和笛尾、响板成对的贝壳。
- **琴键**：木琴的琴条按音名着色（C 红、D 橙、E 黄、F 绿、G 青、A 蓝、B 紫；升降音用更暗、更灰的中间色）。暖色（红、橙、黄、绿）的亮度调低，涂层变薄，在棚拍灯光下也保持饱和。钢琴保持真实外观，按每个音符的音名决定：自然音（C D E F G A B）是象牙白键，升降音是乌木黑键，保留红色毛毡点缀。Jingle Bells 钢琴段 22 个音全是自然音，所以都是白键。白键后面还有两块乌木黑键短块，让 C 大调旋律看起来仍是键盘。
- **乐器名字幕**：默认只在左上角显示一个小标签（程序化图标 + 段落号 + 中文名 + 英文名，如 `01 响板 Castanets`），每个旋律段从第一个击打开始就显示，换段时用 0.3 秒交叉淡入淡出切换；开场第一段从 0.2 秒开始淡入、0.5 秒完全显示，不会在第一帧突然跳出。中途进入或 Shorts 循环播放的观众随时都知道当前是什么乐器，而且不挡弹珠路线。原来的大标题卡已默认去掉，需要时用 `titles.py --cards` 打开。字幕是后期合成层（`titles.py` + `composite.sh`），改文字不用重渲。

弹珠接触面几何不变，禁入检查 0 违规，新增的击打件之间互碰检查 `check_pairs.py --strict` 也没有新的冲突（唯一一对已知的马林巴共鸣管写在 `assets/instruments/pairs_whitelist.json`，有任何新冲突流水线就会停）。

`--look v4` 是 v3 的可读性优化版：吉他日落色面板和深色琴弦、更饱和的青瓷陶笛、竖直悬挂的电颤琴和马林巴共鸣管、更大的长笛和镀金按键、红色钟琴支架。`--look v3` 是 12 种程序化乐器击打件的第一版，`--look v2` 只用材质挡板，`--look v1` 还原已认可的 15 秒小样。所有乐器模型都是本仓库自己的程序化几何，没有第三方模型版权问题。

> 规划器和场景脚本不再写死机器路径。MIDI、输出目录用参数传入；Blender 用环境变量 `BLENDER`；计算设备用 `--device` 或 `MARBLE_DEVICE`。

## 1. 安装

在仓库根目录操作（克隆见文末快速开始）。需要：

- **Python 3**：`pip install mido numpy pillow matplotlib scipy`（`scipy` 只有 `check_pairs.py` 要用）
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
| `LOOK` | 仅 `run_marble.sh`：外观版本 | `v5` |

### Blender 5.x 兼容说明

- **不要用 4.2 打开 5.x 另存的 `.blend`**：5.0 起 blend 格式与 4.2 不兼容。`scene.py` 每次都是程序化建场景，渲染本身不受影响。`model.blend` / `model.glb` 只是缓存，可用当前 Blender 重新生成：
  `$BLENDER -b -P tools/video/marble_music/assets/instruments/build_library.py`
- 布尔引擎：4.2 用 `EXACT`，4.5/5.x 已改为 `MANIFOLD`，脚本会自动回退。
- 按角度平滑：4.x 用 `shade_smooth_by_angle`，5.x 可能要用 `shade_auto_smooth`，脚本会自动回退。
- **Action 动画曲线（macOS Blender 5.3 必看）**：5.0 起 `Action.fcurves` 已移除，改为 slotted channelbags。`scene.py` / `scene_zigzag.py` 通过 `blender_compat.py` 兼容 4.2 与 5.x；未打此补丁时，在设关键插值处会直接 `AttributeError`，一帧都渲不出来。
- Blender 5 的工作色域默认可能不再是 Linear Rec.709，同一帧的颜色会和 4.2 参考图有细微差别。若要对齐参考，可在 Blender 里把 Working Space 设为 Linear Rec.709 再渲。
- macOS：官方 Blender 5.0+ 只支持 Apple Silicon，不再提供 Intel Mac 安装包。GPU 渲染用 `MARBLE_DEVICE=GPU`（会优先选 Metal）。
- 全片如果 4.2 和 5.3 混渲，建议先对比同一帧再拼接。

## 2. 运行顺序

以 Jingle Bells 全曲（`projects/jingle-bells-marble-music/source/jingle.mid`，约 176.3 秒，30 fps）为例。建议在仓库根目录执行。

1. **提取击打点** `extract_hits.py`：读 MIDI，建立 tempo map，只取 `01.`–`12.` 主旋律轨（13–16 伴奏只出声不出画），60ms 内叠音合并为一次击打（取最高音）。
2. **逆向规划轨迹** `plan_zigzag.py`：先定时间再反推几何；左右交替挡板；段间是抛物线；挡板法线为入射反向与出射方向的角平分线。全曲规划约 0 次穿模。
3. **禁入检查** `check_keepout.py`：用资产库表面采样点检查装饰几何、销钉是否侵入弹道（v3 及以后必做，按 `--look` 读取对应外观的资产，`--strict` 有违规会退出；竖直悬挂件也会一起检查）。v5 再跑 `check_pairs.py --strict`，检查击打件之间（含悬挂铜管、长笛笛头）是否小于 1 cm。v4 起就有的一对马林巴共鸣管（间距 9 mm，没有碰到）写在白名单 `assets/instruments/pairs_whitelist.json` 里，只要间距不变小就放行；其他任何新冲突都会让脚本退出 1，`run_zigzag.sh` 会停下。
4. **渲 12 张乐器静帧**（材质/外形确认）：帧号为各段落中段的击打帧。
5. **渲 15 秒小样**，再合成音频、出接触点拼图。
6. **全曲渲染**（可断点续渲，已有帧会跳过），然后 `mux.sh` 合成。
7. **v5 字幕合成**：`titles.py` 生成每帧 RGBA 字幕层，`composite.sh` 把渲染帧、字幕层和对应时段的音频合成为成片。`run_zigzag.sh` 在 v5 下会自动做，输出 `*_titled.mp4`。

规划器可调参数：`--g` 重力，`--half-gap` 左右间距，`--drop-rate` 最大下落速度，`--frac` 弹跳高度系数（越小越平），`--frame-margin` 镜头跟随裕度（v2 及以后用 0.8）。

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
  work/plan_zz_v2.json --look v5 --out work/keepout_report_v5.json --strict
python3 tools/video/marble_music/check_pairs.py \
  work/plan_zz_v2.json --look v5 --out work/pairs_report_v5.json --strict

# 自动挑 12 张静帧的帧号（打印每段的画面内击打件数和最后一行逗号分隔的帧列表）
python3 tools/video/marble_music/select_stills.py work/plan_zz_v2.json
```

可选：画出整条轨迹总览 `python3 tools/video/marble_music/plot_trajectory.py work/plan_zz_v2.json work/trajectory.png`

### 3.2 十二张乐器静帧（推荐先做）

帧号由 `select_stills.py work/plan_zz_v2.json` 自动挑选：每个乐器段落里画面内同乐器击打件最多、弹珠在画面中上部的击打帧（避开长距离下落）：响板 92、钢琴 230、电颤琴 597、管钟 928、马林巴 1341、卡林巴 1772、长笛 2089、木琴 2677、陶笛 3233、钟琴 3572、钢鼓 4427、吉他 4734。（v3 用的是旧的中段帧 73,257,597,1010,1460,1763,2186,2654,3086,3655,4280,4895。）

```bash
mkdir -p work/stills_v5
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v5 \
  --plan work/plan_zz_v2.json \
  --out work/stills_v5 \
  --frames 92,230,597,928,1341,1772,2089,2677,3233,3572,4427,4734 \
  --samples 12 --res 1080x1920 --device "${MARBLE_DEVICE:-GPU}"

python3 tools/video/marble_music/instrument_sheet.py \
  work/plan_zz_v2.json work/stills_v5 work/instrument_stills_v5.png \
  --frames 92,230,597,928,1341,1772,2089,2677,3233,3572,4427,4734

# v4 / v5 对比（先按同样参数把 v4 渲到 work/stills_v4）
python3 tools/video/marble_music/compare_sheet.py \
  work/plan_zz_v2.json work/stills_v4 work/stills_v5 work/instrument_stills_v4_vs_v5.png v4 v5 \
  --frames 92,230,597,928,1341,1772,2089,2677,3233,3572,4427,4734
```

只渲其中一张（例如钢琴，低采样试跑）：

```bash
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v5 --plan work/plan_zz_v2.json --out work/stills_v5 \
  --frames 230 --samples 4 --res 540x960 --device "${MARBLE_DEVICE:-GPU}"
```

### 3.3 15 秒小样

```bash
tools/video/marble_music/run_zigzag.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 \
  0 15 30 12 1080x1920 v5 "${MARBLE_DEVICE:-GPU}"
# 输出：.../om_zigzag_0_15/marble_zigzag_v5_0_15.mp4（无字幕）和 marble_zigzag_v5_0_15_titled.mp4（带字幕）
```

或用旧入口（第 8 个参数仍是设备；外观用 `LOOK=v5`，默认就是 v5）：

```bash
LOOK=v5 tools/video/marble_music/run_marble.sh \
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
  0 176.3 30 12 1080x1920 v5 "${MARBLE_DEVICE:-GPU}"

# 或后台启动 / 续渲
tools/video/marble_music/resume_full.sh v5
# 日志：projects/jingle-bells-marble-music/om_zigzag_full/render_v5.log
```

若只想把已渲好的帧和音频合成（默认 `render_audio.sh` 会在流水线里自动做）：

```bash
tools/video/marble_music/mux.sh \
  projects/jingle-bells-marble-music/om_zigzag_full/frames_zz_v5 \
  projects/jingle-bells-marble-music/om_zigzag_full/audio.wav \
  30 \
  projects/jingle-bells-marble-music/om_zigzag_full/marble_zigzag_v5_0_176.3.mp4
```

### 3.5 v5 字幕层（角标；标题卡可选），后期合成

字幕不进 Blender，单独生成一层 RGBA PNG（编号和渲染帧一致，`%05d.png`），再用 ffmpeg `overlay` 叠上去。改文字、时长、位置只需重跑下面两步，不用重渲。

```bash
# 全曲字幕层（默认只有角标）：几秒钟，5290 帧里只有约 130 张不同的图，其余用硬链接
python3 tools/video/marble_music/titles.py work/plan_zz_v2.json work/overlay_v5
#   --start/--end 帧范围；--res 默认 1080x1920；--label-fade 换段交叉淡化时长（默认 0.3 秒）
#   --cards 另外打开大标题卡（可选，默认关）；--no-corner 关掉角标（只配合 --cards 用）

# 看一帧效果：把第 1925 帧（长笛段开头）的角标叠在一张渲染图上
python3 tools/video/marble_music/titles.py work/plan_zz_v2.json --still 1925 \
  --bg work/stills_v5/02089.png --png work/label_still.png

# 合成：渲染帧（任意分辨率，会用 lanczos 放大到字幕层尺寸）+ 字幕层 + 对应时段音频
#   composite.sh FRAMES_DIR OVERLAY_DIR AUDIO.wav FPS START_FRAME OUT.mp4
#   audio.wav 要从 t=0 开始的整曲音频，脚本会按 START_FRAME/FPS 裁剪
tools/video/marble_music/composite.sh \
  projects/jingle-bells-marble-music/om_zigzag_full/frames_zz_v5 work/overlay_v5 \
  projects/jingle-bells-marble-music/om_zigzag_full/audio.wav 30 0 work/marble_v5_titled.mp4
```

- **时间（默认，只有角标）**：每段第一个击打时刻开始显示，0.3 秒淡入（`--label-fade`），换段时旧标签淡出、新标签淡入同时进行（交叉淡化）；第一段从 t=0 开始，所以晚 `--first-delay`（默认 0.2 秒）开始淡入，0.5 秒时完全显示。不透明度 0.8。
- **大标题卡（可选，`--cards`）**：每段开始淡入 0.3 秒、停 1.6 秒、淡出 0.4 秒，然后才出现角标；第一张晚 0.4 秒。位置 `--place auto`（默认）用和 `scene.py` 一样的相机，把击打件（按 0.45 m 半径算上轮廓）和弹珠投影到画面上，在安全区里挑全曲统一、被遮挡最少的位置（本曲左下 (28, 1342)）；`--place section` 每段各选一个位置，`--place top` 固定在左上。`--card-scale`（默认 0.8）、`--card-alpha`（默认 150/255）。
- **安全区（9:16 / YouTube Shorts）**：全部内容在 x∈[28, 900]、y∈[214, 1536] 像素（以 1080×1920 计），避开顶部约 10%（192 px）、底部约 20%（384 px）和右侧约 15% 的按钮栏。
- **字体**：Noto Sans CJK SC 粗体和常规体，SIL Open Font License 1.1。仓库里只放了用到的字形子集 `fonts/NotoSansSC-{Bold,Regular}-subset.otf`（约 64 KB，许可证见 `fonts/OFL.txt`、`fonts/README.txt`）。改了 `titles.py` 里的乐器名后，用 `fonts/make_subset.sh` 重新生成子集（需要 `pip install fonttools` 和完整的 Noto Sans CJK 字体），或用 `--font-bold/--font-regular` 指定其他字体。
- **图标**：12 个乐器图标全部用 PIL 在 `titles.py` 里程序化绘制，没有第三方图片。

## 4. 做法说明（4 步）

1. **提取击打点** `extract_hits.py` — 见上文。
2. **逆向规划轨迹** `plan_zigzag.py` — 向量化碰撞检测；输出每帧弹珠位置、挡板位姿、相机路径到 `plan_zz_v2.json`。
3. **Blender 渲染** `scene.py` — 程序化建场景：灰墙、翡翠绿玻璃弹珠、柔光；v3 及以后从 `assets/instruments/` 实例化 12 种击打件（`--look vN` 会选不超过 N 的最新覆盖版本 `<乐器>/vN/`；共鸣管和管钟铜管作为世界坐标竖直的悬挂件单独生成）；击打帧挡板下沉 + 边缘闪光；相机平滑下摇。Cycles + OIDN + 运动模糊 + AgX。已存在且大于 1KB 的帧自动跳过。
4. **音频与合成** `render_audio.sh` + `mux.sh` — FluidSynth + GeneralUser GS 把整份 MIDI（全部 17 轨）合成 48k WAV 并裁到同一时间窗；ffmpeg 合成 H.264 + AAC。v5 再用 `titles.py` + `composite.sh` 叠字幕层。

升级路线和特效规划见同目录 `UPGRADE_PLAN.md`。历史脚本 `scene_zigzag.py` 是最早的 v1 快照，新流程请用 `scene.py`。

## 快速开始（Mac 本机）

```bash
git clone https://github.com/AFeiYA/midi2video.git
cd midi2video
pip install mido numpy pillow matplotlib scipy
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
  work/plan_zz_v2.json --look v5 --out work/keepout_report_v5.json --strict
python3 tools/video/marble_music/check_pairs.py \
  work/plan_zz_v2.json --look v5 --out work/pairs_report_v5.json --strict

# 12 张乐器静帧
mkdir -p work/stills_v5
"$BLENDER" -b -P tools/video/marble_music/scene.py -- \
  --look v5 --plan work/plan_zz_v2.json --out work/stills_v5 \
  --frames 92,230,597,928,1341,1772,2089,2677,3233,3572,4427,4734 \
  --samples 12 --res 1080x1920 --device GPU

# 15 秒小样
tools/video/marble_music/run_zigzag.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 \
  0 15 30 12 1080x1920 v5 GPU
# 带字幕的成片：.../om_zigzag_0_15/marble_zigzag_v5_0_15_titled.mp4
```
