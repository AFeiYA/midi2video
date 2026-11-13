# 乐器击打件资产库（v3）

每个乐器一个文件夹：`build.py`（程序化几何）、`material.py`（共享材质 + 每颗键的主体材质）、`meta.json`（接触面、法线、销钉、变体、授权，以及 build_library 实测的接触高度和禁入包围盒）、
`model.blend` / `model.glb`（生成的缓存，可以重新生成）、`probe_<variant>.npy`（表面采样点，给 check_keepout.py 用）。

- 局部坐标：+Z 是挡板法线；撞击帧弹珠接触点在 (0,0,0.045)；X 是挡板方向，接触面 x∈[-0.31,0.31]（与规划器 0.62×0.09 的矩形一致）；Y 指向墙，墙在 y=0.30。
- 重新生成（在仓库根目录，用你本机的 Blender）：
  `"${BLENDER:-blender}" -b -P tools/video/marble_music/assets/instruments/build_library.py`
  请用即将用来渲染的同一大版本 Blender 生成缓存。Blender 5.x 写出的 `.blend` 无法用 4.2 打开；`scene.py` 渲染时会重新跑 `build.py`，不依赖这些缓存。
- 碰撞检查（可在仓库根目录执行，脚本按自身位置找资产，不依赖当前工作目录）：
  `python3 tools/video/marble_music/check_keepout.py work/plan_zz_v2.json --strict`
- 渲染：`scene.py --look v3`（也可用 `--look v2` / `--look v1`）。默认 v3。

## v4 覆盖版本（外观 `--look v4`，默认）

部分乐器有 `<乐器>/v4/` 子文件夹（同样包含 build.py / material.py / meta.json / model.blend / model.glb / probe_default.npy），只在 v4 里替换基础版本，v3 不受影响（`library.metas(look)` 负责挑选）：
guitar（日落色面板、深色琴弦、深色音孔花环、短指板、琴弦闪光）、ocarina（饱和青瓷、大号深色指孔）、vibraphone / marimba（共鸣管从击打件里拿出来，改成 `meta.hanging` 描述的世界坐标竖直悬挂件）、flute（更粗的银色管身、镀金按键、深色皮垫）、glockenspiel（加厚钢条、红色支架、黄铜螺钉）。
- 只重建 v4：`blender -b -P assets/instruments/build_library.py -- --only /v4`
- 额外闪光槽：`meta.flash_slots`（如吉他 `["body","strings"]`）
- 悬挂件：`meta.hanging = [{attach, radius, inner, length, role}]`，check_keepout.py 会在世界坐标里一起检查
