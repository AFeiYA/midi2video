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
