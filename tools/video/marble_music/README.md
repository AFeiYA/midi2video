# Marble Music (zig-zag) — MIDI 驱动的弹珠音乐 3D 动画

参考：Virtual 3D《iPhone Ringtone - Marble Music》。弹珠在左右交替的斜挡板之间来回碰撞下落，每次碰撞精确落在一个 MIDI 音符的帧上。

## 做法（4 步）

1. **提取击打点** `extract_hits.py`
   用 mido 读 MIDI，建立 tempo map 把 tick 换算成秒；只取名字匹配 `01.`–`12.` 的主旋律轨（伴奏轨 13–16 只出声不出画）；
   时间窗内的 note_on 按时间排序，60ms 内的和弦/叠音合并成一次击打（取最高音）。输出 `hits.json`。
2. **逆向规划轨迹** `plan_zigzag.py`（核心）
   不是靠物理引擎“碰运气”，而是先定时间再反推几何：
   - 第 i 个音的挡板放在左/右交替的一侧（x = ±half_gap），时间 T_i 吸附到帧网格；
   - 两次击打之间是抛物线：水平速度恒定 vx = Δx/Δt，竖直按重力 g 计算，下落高度由 Δt 决定（长间隔会被限速成“抛高”）；
   - 挡板法线 = 入射反向与出射方向的角平分线，所以反弹在视觉上符合物理；
   - 逐段采样检查弹珠不会穿过其它挡板；输出每帧弹珠位置、挡板位姿、相机路径到 `plan.json`。
3. **Blender 渲染** `scene_zigzag.py`
   程序化建场景：灰墙、实木/象牙挡板+销钉、翡翠绿玻璃弹珠（透射+IOR）、柔光；
   击打帧挡板下沉 + Emission 闪光；相机平滑下摇跟随弹珠；Cycles + OIDN 降噪 + 运动模糊。
   支持断点续渲（已存在的帧自动跳过），`--device AUTO` 在 Mac 上用 Metal GPU。
4. **音频与合成** `render_audio.sh` + `mux.sh`
   FluidSynth + GeneralUser GS 音色库把整份 MIDI（全部 17 轨）合成 48k WAV 并裁剪到同一时间窗；
   ffmpeg 合成 H.264 + AAC；`contact_sheet.py` 输出击打帧拼图用来检查对拍。

## 运行

```bash
cd /Users/luca/OpenMontage
pip install mido numpy pillow   # 如未安装
# 音色库(未入库): 下载 GeneralUser GS 放到 tools/video/marble_music/GeneralUser.sf2，或用 SF2=路径 指定
tools/video/marble_music/run_marble.sh \
  projects/jingle-bells-marble-music/source/jingle.mid \
  projects/jingle-bells-marble-music/om_zigzag_0_15 0 15        # 15 秒小样
# 全曲: ... om_zigzag_full 0 176.3
# 参数: [FPS=30] [SAMPLES=12] [RES=1080x1920] [DEVICE=AUTO|CPU|METAL]
```
环境变量：`BLENDER`（默认 /Applications/Blender.app/Contents/MacOS/Blender）、`SF2`、`PY`。

## 可调参数（plan_zigzag.py）
`--g` 重力，`--half-gap` 左右间距，`--drop-rate` 最大下落速度，`--frac` 弹跳高度系数（越小越平）。
已知问题：部分挡板角度偏平（16–31°），像“落在板上”；长下落后镜头构图偏低。下一版计划把挡板角度限制在 40–60°，相机把弹珠保持在画面中上方。
