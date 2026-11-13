#!/usr/bin/env bash
# Regenerate the bundled title-font subsets after changing names in titles.py.
# needs fontTools (pip install fonttools) and the full Noto Sans CJK fonts (Debian/Ubuntu: fonts-noto-cjk; or the OFL
# NotoSansCJKsc-*.otf / NotoSansSC-*.otf from https://github.com/notofonts/noto-cjk). SRC_BOLD/SRC_REG/FONT_NUMBER override.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; PY=${PY:-python3}
SRC_BOLD=${SRC_BOLD:-/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc}; SRC_REG=${SRC_REG:-/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc}; FN=${FONT_NUMBER:-2}
TXT="$("$PY" -c "import string,sys;s=open(sys.argv[1],encoding='utf-8').read();print(''.join(sorted(set(c for c in s if ord(c)>0x7f)))+string.printable.strip()+' ')" "$HERE/../titles.py")"
"$PY" -m fontTools.subset "$SRC_BOLD" --font-number="$FN" --text="$TXT" --layout-features='*' --output-file="$HERE/NotoSansSC-Bold-subset.otf"
"$PY" -m fontTools.subset "$SRC_REG" --font-number="$FN" --text="$TXT" --layout-features='*' --output-file="$HERE/NotoSansSC-Regular-subset.otf"
echo "subset glyph text: $TXT"
