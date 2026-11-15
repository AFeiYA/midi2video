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
- **flute**：一根连续的长笛。沿用 v4 管身（击打件），笛尾在弹珠平面内和管身对齐（禁入检查允许到 x=0.44）。笛头没法放在弹珠平面内（弹珠从这一侧过来），所以它是 `meta.aligned` 描述的对齐部件：放在弹珠平面之后（y=0.22），沿相机穿过管身轴线的视线摆放，按深度缩放粗细。`scene.py` 每 2 帧按相机位置重新对齐一次，并挂在击打件上跟着下沉，所以从任何倾角看都和管身连成一根，不会再像两根错开的管子。
- **guitar**：6 根黑色琴弦是击打件，后面是正对相机的日落色琴身（上下两个圆弧和腰身、奶油色包边、深色音孔和音孔花环），加乌木琴桥和骨质琴枕，以及带品丝的指板和有 6 个弦钮的琴头。
- **piano**：真实的象牙白键和乌木黑键，按每个音符的音名选择（`meta.variant_rule = "pitch"`：自然音 C D E F G A B 用白键形和象牙色，升降音用更高、两端收窄的黑键形和乌木色），红色毛毡点缀保留。自然音键后面还有两块乌木黑键短块。Jingle Bells 钢琴段 22 个音全是自然音，所以 22 个都是白键。
- **xylophone**：琴条按音名着色（色表见下），涂层很薄（0.2），因为厚涂层会反射柔光箱、把颜色冲淡。

音名色表在 `_common.py`：`PITCH_HUE`、`PITCH_VAL` 和 `pitch_rgb(note)`，现在只有木琴用。暖色的线性亮度调低（C 0.55、D 0.5、E 0.42、F 0.5，其余 0.6），饱和度 1.0，这样 AgX 也不会把它们冲淡。C 红、D 橙、E 黄、F 绿、G 青、A 蓝、B 紫；升降音取两侧自然音中间的色相，饱和度和亮度都更低。

- 只重建 v5：`blender -b -P assets/instruments/build_library.py -- --only /v5`（也可以用 `--only piano/v5,guitar/v5` 只重建指定乐器）
- 新增 `check_pairs.py`（需要 scipy）：检查击打件之间（含悬挂件、对齐部件）在世界坐标里是否小于 `--min`（默认 1 cm）。`--strict` 下，只要有不在 `pairs_whitelist.json` 里的冲突就退出 1。白名单每条只放行指定的那一对键，而且间距不能小于 `min_gap_m`。陡角度时同侧相邻击打件只隔约 0.7 m，所以吉他琴颈、钟琴琴箱、管钟铜管的长度都按这个检查结果截短过。
  `python3 tools/video/marble_music/check_pairs.py work/plan_zz_v2.json --look v5 --strict`
- 对齐部件：`meta.aligned = [{name, a, b, y, radius}]`，`build.py` 里的 `build_aligned(C, name)` 沿 -X 建模（从原点开始，长度 |b-a|）。位姿由 `library.aligned_local()` 计算，`scene.py` 和 `check_pairs.py` 共用。

## hook50（50 秒 Shorts 副歌接力版）新增击打件（外观 v5 家族）

按音轨名选择（`meta.tracks_regex`；`meta.priority` 越大越优先，用来让 "Tubular Bells & Castanets" 选中组合件而不是单独的响板/管钟）：

- **bells_castanets**（`tubular.*castanet`，priority 5）：黄铜横梁是击打件，6 根逐级变短的铜管世界竖直悬挂（`meta.hanging`），横梁右端用红绳挂一对响板（在弹珠平面之后）。
- **music_box**（`music box`）：黄铜音梳是击打件（顶条 + 17 根逐级变短的梳齿），后面是带销钉的黄铜滚筒、胡桃木盒（黄铜嵌线、钥匙孔）、打开的红丝绒盒盖和发条钥匙。
- **marimba/v5**（覆盖 v4）：拱形红木琴条是击打件，后面是正对相机的 7 根逐级变短的红木琴条（红绳穿过节点、深色边框）。不再挂共鸣管，因为金色竖管和管钟太像。
- **koto**（`koto`）：红木琴边是击打件，后面是深色桐木琴面、琴弦、一排斜向的象牙色琴柱（ji）和带金边的红木端头。
- **pixel8bit**（`8-bit|square lead|chiptune`）：7 块像素方块是击打件（颜色逐键轮换），后面是黑色游戏机面板上发光的体素八分音符、十字键和两个按钮。
- **bagpipe**（`bagpipe`）：带象牙箍的黑木低音管是击打件，后面是红色苏格兰格纹气袋、两根向左上伸出的低音管、下垂的旋律管和红色流苏绳。
- **finale**（`tutti|finale`，priority 5）：单弹珠齐奏终章。抛光金条是击打件，后面是微微发光的金色圣诞星、红色蝴蝶结和两只挂在红绳上的金色铃铛。

齐奏终章只用一颗弹珠：`extract_hits.py --tutti-min 3` 把 3 条及以上乐器轨同时起音的音合并成一次击打，音轨名标为 `09/09. Grand Tutti Finale`，音频仍然是 8 种乐器一起响。

```
python extract_hits.py hook50/02_..._Split.mid --start 0 --end 50.2 --tutti-min 3 -o work_hook50/hits.json
python fix_clearance.py work_hook50/hits.json -o work_hook50/plan_zz_v2.json --look v5
blender -b -P assets/instruments/build_library.py -- --only bells_castanets,music_box,koto,pixel8bit,bagpipe,finale,marimba/v5
python hook50_sheet.py work_hook50/plan_zz_v2.json stills/ hook50_instrument_sheet.png
```

## 珠匣乐团 Jewelbox Orchestra：64 乐器注册表（registry）

64 款 GM 乐器（+ 终章 65）的统一入口，供程序化调用。系列名是工作名，只在 `registry.json` 的 `series` 里改。

- `registry.json`：每个乐器一条：`num`（01–65）、`id`（稳定 slug）、`gm`（GM program 0–127）、`family`（F1–F6）、
  `en` / `zh` / `aliases`（和 MIDI 标记里的写法一致）、`asset`（本目录下的击打件文件夹）、`status`
  （`reuse` 直接用现有 / `adapt` 在现有基础上改的新文件夹 / `new` 全新）、`title.icon`（titles.py 的 NAMES 编号，没有就 null）、
  `title.accent`（强调色 RGB）、`track`（标准标记文字 `"NN. Name (中文)"`）。`sets` 里是命名乐器组（hook50、jingle12）。
- `registry.py`（不依赖 bpy）：
  ```python
  get_instrument('gm:0') / get_instrument('num:12') / get_instrument('id:dulcimer') / get_instrument('颤音琴') / get_instrument('08. Vibraphone (颤音琴)')
  resolve_track(track_or_marker_name, program=None)   # 先按名字，再按 GM program
  instrument_set('jewelbox')      # 65 条；'jewelbox:F1'..':F6' 单个家族；'hook50' / 'jingle12'
  striker(entry, look='v5')       # 资产目录、接触点/法线、包围盒、keep-out、销钉、悬挂件、闪光色、变体
  ```
- 选择乐器组后的映射：`library.assign(keys, M, instrument_set=...)` 先用 registry 解析每个键的 track 名（或 `key['program']`），
  解析不到或资产还没建的，回到原来的 `tracks_regex` 匹配。不传 `instrument_set` 时行为和以前完全一样。
  scene.py / check_keepout.py / check_pairs.py 都读 `plan['instrument_set']`。
- 珠匣新文件夹的 `tracks_regex` 都是 `(?!)`（永不匹配），所以老歌的乐器映射一个都不会变；只能通过 registry 用到。
- 64 乐器 MIDI 一条龙：
  ```bash
  python extract_hits.py 02_Jingle_Bells_64_Instruments_Family_MultiTrack.mid --tracks 1,2,3,4,5,6 --markers --instrument-set jewelbox -o hits.json
  python plan_zigzag.py hits.json -o plan.json        # plan 里带 instrument_set，每个键带 program
  ```
  `--markers` 用 Track 0 当前标记（"08. Vibraphone (颤音琴)"）给每个音命名（latin-1 → UTF-8 已修正），并记下 GM program。
- 资产生成器在 `gen/`（纯 python，不要 bpy）：`gen/assetgen.py`（write 工具）、`gen/hook50.py`、`gen/jewelbox_f1.py`。
  生成后用 `blender -b -P build_library.py -- --only grand_piano,rhodes,...` 建缓存和 probe。
- 乐器展示图：`python showcase.py plan.json --set jewelbox:F1` → `scene.py --frames $(python showcase.py --frames plan.json)` →
  `python showcase.py --sheet plan.json frames/ sheet.png --closeups close.png`（标签默认取自 registry）。

### 家族 1（01–12，键盘·钟·槌击）
| # | 乐器 | 资产 | 状态 |
|---|---|---|---|
| 01 | 大钢琴 | grand_piano | 新：象牙/乌木键（按音高）+ 黑漆三角钢琴侧影、撑起的琴盖、金弦、琴腿、踏板 |
| 02 | 电大钢琴 | electric_grand | 新：珍珠白短尾舞台钢琴、红条、镀铬 X 架、卷线 |
| 03 | 罗兹电钢 | rhodes | 新：黑色皮革手提箱、银色铭牌条、红色标牌、外撇镀铬腿、延音踏板 |
| 04 | 羽管键琴 | harpsichord | 新：反色键（乌木白键/骨色黑键）+ 上层键盘、红漆长琴箱、彩绘琴盖、镀金车腿 |
| 05 | 钢片琴 | celesta | 新：蜂蜜木立式琴柜、拱顶、镀金镂空格栅、竖琴形踏板架 |
| 06 | 钟琴 | glockenspiel (v5) | 复用 |
| 07 | 八音盒 | music_box | 复用 |
| 08 | 颤音琴 | jb_vibraphone | 改：铝条 + 两侧小琴条、三根金色共鸣管（世界竖直）、风扇片 + 电机轴 |
| 09 | 马林巴琴 | marimba (v5) | 复用 |
| 10 | 木琴 | jb_xylophone | 改：按音高的彩虹琴条 + 彩虹儿童木琴图标、交叉琴槌 |
| 11 | 管钟 | tubular_bells (v5) | 复用 |
| 12 | 扬琴 | dulcimer | 新：带银弦的胡桃木击打条 + 梯形扬琴、两个金色音孔、琴码、交叉琴竹 |

### 家族 2（13–24，风琴·手风琴·口琴·吉他·贝斯·竖琴）— `gen/jewelbox_f2.py`
| # | 乐器 | 资产 | 状态 |
|---|---|---|---|
| 13 | 拉杆风琴 | drawbar_organ | 新：按音高的琴键 + 左侧九根拉杆（棕/白/黑）、胡桃木琴台、镀铬饰条、木质低音踏板 |
| 14 | 教堂管风琴 | church_organ | 新：琴键 + 两侧象牙音栓、V 形锡管立面（中间短，小球落在缺口里）、橡木哥特塔 + 金尖顶 |
| 15 | 手风琴 | accordion | 新：琴键 + 正面红珠光手风琴：镀铬菱格网罩、黑白风箱、贝斯按钮阵、背带 |
| 16 | 口琴 | harmonica | 新：击打件本身是十孔口琴（镀铬盖板 + 木梳 + 十个孔）+ 打开的红色铁盒、蓝丝绒、备用口琴 |
| 17 | 古典尼龙弦吉他 | nylon_guitar | 改（基于 guitar v5）：白色尼龙弦 + 缠弦、浅色云杉面板、马赛克音孔、开槽琴头 |
| 18 | 民谣钢弦吉他 | guitar (v5) | 复用 |
| 19 | 清音电吉他 | electric_guitar | 新：天蓝双切角琴身、白护板、三个单线圈、枫木琴颈、六联琴头 |
| 20 | 失真摇滚电吉他 | distortion_guitar | 新：红色 V 形琴身、双双线圈、箭头琴头、卷线接迷你音箱 |
| 21 | 原声立式贝斯 | upright_bass | 新：深琥珀小提琴族大琴身、f 孔、琴马、尾柱、琴头涡卷（无弓；28 低音提琴会带弓） |
| 22 | 无品贝斯 | fretless_bass | 新：深紫偏腰琴身、玳瑁护板、无品乌木指板（只有白线）、四联大琴头 |
| 23 | 弦乐拨奏 | pizzicato | 新：羊肠弦 + 三把扇形排开的小提琴（弦乐组，无弓） |
| 24 | 管弦乐竖琴 | harp | 新：镀金琴颈是击打件；金色凹槽琴柱 + 琴冠、斜面音板、红 C 弦 / 蓝 F 弦、底座踏板 |

### 家族 3（25–32，独奏弦乐·合奏·人声·齐奏重音）— `gen/jewelbox_f3.py`
（拉弓 vs 拨弦：小提琴 / 中提琴身后有弓，23 弦乐拨奏没有弓；大提琴 / 低音提琴 / 弦乐合奏直接用**弓**当击打件、琴竖立在后面，21 原声贝斯是拨弦、横放）
| # | 乐器 | 资产 | 状态 |
|---|---|---|---|
| 25 | 小提琴 | violin | 新：钢弦击打件 + 亮橙红小提琴正面（f 孔、乌木指板、腮托、琴头涡卷）+ 斜放的琴弓 |
| 26 | 中提琴 | viola | 新：同上但琴身更大、深栗色、弓反方向斜放 |
| 27 | 大提琴 | cello | 新：琴弓是击打件（木杆、白马尾、乌木弓根 + 珍珠眼、象牙弓尖）+ 竖立的深牛血红大提琴、尾柱 |
| 28 | 低音提琴 | contrabass | 新：琴弓击打件 + 竖立的近黑色大号低音提琴（溜肩）、尾柱 |
| 29 | 交响弦乐合奏 | string_ensemble | 新：琴弓击打件 + 中间竖立大提琴、两侧外倾的小提琴（橙）和中提琴（栗色）、第二把弓、红丝绒台阶 |
| 30 | 人声合唱团 | choir | 新：橡木合唱台阶是击打件 + 两排穿酒红长袍、白色圣带、拿黑色歌本、张嘴“啊”的合唱队员（前排中间留空给小球） |
| 31 | 人声哼鸣 | voice_oohs | 新：镀铬吊杆（带配重球）是击打件 + 末端金色支架上的复古装饰艺术风镀铬麦克风、立杆、黑色底座、卷线、红色 ON-AIR 灯 |
| 32 | 交响齐奏重音 | orchestra_hit | 新：定音鼓鼓皮 + 镀铬鼓圈是击打件 + 铜鼓身、调音杆、底座踏板；旁边金色吊镲 + 金色冲击光线，另一侧交叉鼓槌 |
