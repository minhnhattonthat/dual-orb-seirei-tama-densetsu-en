"""bg3text.py: a VRAM dump's BG3 tilemap ($7800 words) as a text grid, decoded through the original glyph table.

    python -X utf8 tools/bg3text.py work/qa/x/ppu_000029.vram.bin [--rows 0-28]
Each text row shows 32 cells: the glyph, ' ' blank, '.' any other tile (frames, icons, VWF pool tiles). Column
ruler on top; use it to read a field's start column and the next item's column (budget = cells * 8 px)."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from maps import ROM  # noqa: E402
from tbl import Table  # noqa: E402

T = Table.load(ROOT / "tbl" / "jp.tbl")


def grid(vram, rom):
    g = [struct.unpack_from("<HH", rom, 0x30A2 + 4 * c) for c in range(0xE0)]
    pair = {}
    for c in range(0xE0):
        pair.setdefault((g[c][0] & 0x3FF, g[c][1] & 0x3FF), c)
    m = [struct.unpack_from("<H", vram, 0xF000 + 2 * i)[0] & 0x3FF for i in range(32 * 64)]
    rows = []
    for r in range(28):
        line = ""
        for c in range(32):
            t, b = m[r * 32 + c], m[(r + 1) * 32 + c]
            code = pair.get((t, b))
            if t == 0x16A:
                line += " "
            elif code is not None and code != 0x3F:
                s = T.decode(bytes([code]), 0, 1)[0]
                line += s if len(s) == 1 else "?"
            else:
                line += "."
        rows.append(line)
    return rows


if __name__ == "__main__":
    v = Path(sys.argv[1]).read_bytes()
    print("   " + "".join(str(i % 10) for i in range(32)))
    for r, line in enumerate(grid(v, ROM.read_bytes())):
        print(f"{r:2} {line}")
