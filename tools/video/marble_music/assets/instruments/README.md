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

v5 的 `<乐器>/v5/` 覆盖版本。`library.metas(look)` 按外观版本号取不超过所选外观的最新覆盖版本（`LOOK_ORDER = ['v3','v4','v5','v6','v7']`），所以没有 v5 子文件夹的乐器（颤音琴、马林巴）沿用 v4，v3/v4 完全不受影响。v6 没有新的几何覆盖，沿用 v5 资产，只在 `scene.py` 里加阶段 3 特效。v7 为笛子、木琴、钢鼓、吉他增加了新的几何覆盖（乐器本身作为击打面，接触点和法线仍与规划器一致）；其余 8 种沿用 v5（或 v4）。v7 保留段落主题色和更克制的 Bloom，不再使用雪花和撞击火花。

思路：相机基本看到的是击打件在 XZ 平面的侧影。y∈[0.155, 0.285] 在弹珠平面之后，弹珠永远碰不到，所以大块的可辨认轮廓都放在这里。弹珠平面内（|y|<0.15）的接触几何基本不变，`check_keepout.py --look v5 --strict` 是 0 违规。

- **castanets**：一对打开的贝壳，正面朝相机。前壳是击打件，顶部和接触面齐平；后壳在弹珠平面之后。深色边，两只耳朵用红绳圈连起来。
- **kalimba**：钢制琴桥横条是击打件，下面是 9 根长短不一的 V 形扇形钢片，装在带深色音孔的圆角胡桃木板上。钢片和木板都在弹珠平面之后。
- **glockenspiel**：钢条是击打件，后面是红色梯形琴箱，里面还有 4 根逐级变短的钢条和黄铜螺钉。
- **ocarina**：加大的红薯形（有圆尾巴），面向相机的一面有 4 个大指孔和深色出音窗，吹口在弹珠平面之后、伸出轮廓外。
- **tubular_bells**：黄铜横梁是击打件，5 根逐级变短、带顶帽的铜管在世界坐标里竖直悬挂（`meta.hanging` 新增 `cap_role`）。
- **steel_drums**：镀铬边条是击打件，后面是正对相机的圆形钢鼓面：碗形鼓面、中心音区，加 6 个有深色沟槽轮廓的凹坑音区。
- **flute**：一根连续的长笛。沿用 v4 管身（击打件），笛尾在弹珠平面内和管身对齐（禁入检查允许到 x=0.44）。笛头没法放在弹珠平面内（弹珠从这一侧过来），所以它是 `meta.aligned` 描述的对齐部件：放在弹珠平面之后（y=0.22），沿相机穿过管身轴线的视线摆放，按深度缩放粗细。`scene.py` 每 2 帧按相机位置重新对齐一次，并挂在击打件上跟着下沉，所以从任何倾角看都和管身连成一根，不会再像两根错开的管子。
- **guitar**：6 根黑色琴弦是击打件，后面是正对相机的日落色琴身（上下两个圆弧和腰身、奶油色包边、深色音孔和音孔花环），加乌木琴桥和骨质琴枕，以及带品丝的指板和有 6 个弦钮的琴头。
- **piano**：真实的象牙白键和乌木黑键，按每个音符的音名选择（`meta.variant_rule = "pitch"`：自然音 C D E F G A B 用白键形和象牙色，升降音用更高、两端收窄的黑键形和乌木色），红色毛毡点缀保留。自然音键后面还有两块乌木黑键短块。Jingle Bells 钢琴段 22 个音全是自然音，所以 22 个都是白键。
- **xylophone**：琴条按音名着色（色表见下），涂层很薄（0.2），因为厚涂层会反射柔光箱、把颜色冲淡。

音名色表在 `_common.py`：`PITCH_HUE`、`PITCH_VAL` 和 `pitch_rgb(note)`，现在只有木琴用。暖色的线性亮度调低（C 0.55、D 0.5、E 0.42、F 0.5，其余 0.6），饱和度 1.0，这样 AgX 也不会把它们冲淡。C 红、D 橙、E 黄、F 绿、G 青、A 蓝、B 紫；升降音取两侧自然音中间的色相，饱和度和亮度都更低。

- 只重建 v5：`blender -b -P assets/instruments/build_library.py -- --only /v5`（也可以用 `--only piano/v5,guitar/v5` 只重建指定乐器）
- 新增 `check_pairs.py`（需要 scipy）：检查击打件之间（含悬挂件、对齐部件）在世界坐标里是否小于 `--min`（默认 1 cm）。`--strict` 下，只要有不在 `pairs_whitelist.json` 里的冲突就退出 1。白名单每条只放行指定的那一对键，而且间距不能小于 `min_gap_m`。陡角度时同侧相邻击打件只隔约 0.7 m，所以吉他琴颈、钟琴琴箱、管钟铜管的长度都按这个检查结果截短过。
  `python3 tools/video/marble_music/check_pairs.py work/plan_zz_v2.json --look v5 --strict`
- 对齐部件：`meta.aligned = [{name, a, b, y, radius}]`，`build.py` 里的 `build_aligned(C, name)` 沿 -X 建模（从原点开始，长度 |b-a|）。位姿由 `library.aligned_local()` 计算，`scene.py` 和 `check_pairs.py` 共用。
