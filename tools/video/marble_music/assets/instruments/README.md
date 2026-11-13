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

## v4 覆盖版本（外观 `--look v4`）

部分乐器有 `<乐器>/v4/` 子文件夹（同样包含 build.py / material.py / meta.json / model.blend / model.glb / probe_default.npy），只在 v4 里替换基础版本，v3 不受影响（`library.metas(look)` 负责挑选）：
guitar（日落色面板、深色琴弦、深色音孔花环、短指板、琴弦闪光）、ocarina（饱和青瓷、大号深色指孔）、vibraphone / marimba（共鸣管从击打件里拿出来，改成 `meta.hanging` 描述的世界坐标竖直悬挂件）、flute（更粗的银色管身、镀金按键、深色皮垫）、glockenspiel（加厚钢条、红色支架、黄铜螺钉）。
- 只重建 v4：`blender -b -P assets/instruments/build_library.py -- --only /v4`
- 额外闪光槽：`meta.flash_slots`（如吉他 `["body","strings"]`）
- 悬挂件：`meta.hanging = [{attach, radius, inner, length, role}]`，check_keepout.py 会在世界坐标里一起检查

## v5 覆盖版本（外观 `--look v5`，默认）：一眼认出乐器

v5 的 `<乐器>/v5/` 覆盖版本。`library.metas(look)` 按 `LOOK_ORDER = ['v3','v4','v5']` 取不超过所选外观的最新覆盖版本，所以没有 v5 子文件夹的乐器（颤音琴、马林巴）沿用 v4，v3/v4 完全不受影响。

思路：相机基本看到的是击打件在 XZ 平面的侧影。y∈[0.155, 0.285] 在弹珠平面之后，弹珠永远碰不到，所以大块的可辨认轮廓都放在这里。弹珠平面内（|y|<0.15）的接触几何基本不变，`check_keepout.py --look v5 --strict` 是 0 违规。

- **castanets**：一对打开的贝壳，正面朝相机。前壳是击打件，顶部和接触面齐平；后壳在弹珠平面之后。深色边，两只耳朵用红绳圈连起来。
- **kalimba**：钢制琴桥横条是击打件，下面是 9 根长短不一的 V 形扇形钢片，装在带深色音孔的圆角胡桃木板上。钢片和木板都在弹珠平面之后。
- **glockenspiel**：钢条是击打件，后面是红色梯形琴箱，里面还有 4 根逐级变短的钢条和黄铜螺钉。
- **ocarina**：加大的红薯形（有圆尾巴），面向相机的一面有 4 个大指孔和深色出音窗，吹口在弹珠平面之后、伸出轮廓外。
- **tubular_bells**：黄铜横梁是击打件，5 根逐级变短、带顶帽的铜管在世界坐标里竖直悬挂（`meta.hanging` 新增 `cap_role`）。
- **steel_drums**：镀铬边条是击打件，后面是正对相机的圆形钢鼓面：碗形鼓面、中心音区，加 6 个有深色沟槽轮廓的凹坑音区。
- **flute**：沿用 v4 管身，在弹珠平面之后加一根连续的长管（笛头 → 笛尾），带唇板、笛头塞、接口环和笛尾按键，整体读成一根细长的长笛。用连续长管而不是分开的两段，是因为相机向下看、又偏在一侧，弹珠平面之后的部件会随每个键的倾角错位，分开的两段看起来会断开。
- **guitar**：6 根黑色琴弦是击打件，后面是正对相机的日落色琴身（上下两个圆弧和腰身、奶油色包边、深色音孔和音孔花环），加乌木琴桥和骨质琴枕，以及带品丝的指板和有 6 个弦钮的琴头。
- **piano**：真实的象牙白键和乌木黑键，按每个音符的音名选择（`meta.variant_rule = "pitch"`：自然音 C D E F G A B 用白键形和象牙色，升降音用更高、两端收窄的黑键形和乌木色），红色毛毡点缀保留。自然音键后面还有两块乌木黑键短块。Jingle Bells 钢琴段 22 个音全是自然音，所以 22 个都是白键。
- **xylophone**：琴条按音名着色（色表见下）。

音名色表在 `_common.py`：`PITCH_HUE` 和 `pitch_rgb(note)`，现在只有木琴用。C 红、D 橙、E 黄、F 绿、G 青、A 蓝、B 紫；升降音取两侧自然音中间的色相，饱和度和亮度都更低。

- 只重建 v5：`blender -b -P assets/instruments/build_library.py -- --only /v5`（也可以用 `--only piano/v5,guitar/v5` 只重建指定乐器）
- 新增 `check_pairs.py`（需要 scipy）：检查击打件之间（含悬挂件）在世界坐标里是否小于 `--min`（默认 1 cm）。陡角度时同侧相邻击打件只隔约 0.7 m，所以吉他琴颈、钟琴琴箱、管钟铜管的长度都按这个检查结果截短过。
  `python3 tools/video/marble_music/check_pairs.py work/plan_zz_v2.json --look v5`
