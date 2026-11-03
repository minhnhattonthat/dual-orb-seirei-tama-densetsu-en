"""signs.py: the Gold City "ホテル" signs in English (issue #5, docs/re/graphics.md G13).

The sign is 6x2 BG tiles (48x16 px, palette 6) of the Gold City map tileset, block $28:A87F, which $00:8AEE unpacks
to $7E:8000 (tile n at $7E:8000 + 32n; the sign = tiles $215-$21A over $225-$22A). asm/buttons.asm's unpack hook
copies build/vwf/hotel.bin over them when the 16 bytes at the first sign tile match the Japanese (SIG).
gfx/hotel.txt is the source: a sig line, then 16 rows x 48 px of palette indices (hex, '.' = 0).

    python -X utf8 tools/signs.py make WRAM.bin   gfx/hotel.txt from a 128 KB WRAM dump of Gold City (the Japanese sign;
                                                 tools/lua/vwfdump.lua), to be redrawn by hand
    python -X utf8 tools/signs.py                 build/vwf/hotel.bin + hotel_sig.bin (build.py runs it); --test
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "gfx" / "hotel.txt"
OUT = ROOT / "build" / "vwf"
TOP = 0x215          # first tile of the top row; the bottom row is TOP + 16; asm copies 6 tiles of each
W, H = 48, 16


def tile_of(x, y):
    return TOP + x // 8 + (16 if y >= 8 else 0)


def to_px(blk):
    """48x16 index grid from a block holding tile n at 32n"""
    g = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            b = blk[tile_of(x, y) * 32:]
            g[y][x] = sum(((b[(p // 2) * 16 + (y % 8) * 2 + (p & 1)] >> (7 - x % 8)) & 1) << p for p in range(4))
    return g


def to_tiles(g, blk):
    for y in range(H):
        for x in range(W):
            for p in range(4):
                i = tile_of(x, y) * 32 + (p // 2) * 16 + (y % 8) * 2 + (p & 1)
                bit = 1 << (7 - x % 8)
                blk[i] = (blk[i] | bit) if g[y][x] >> p & 1 else (blk[i] & ~bit)


def make(dump):
    blk = Path(dump).read_bytes()[0x8000:0x10000]
    lines = [f"sig {blk[TOP * 32:TOP * 32 + 16].hex()}"]
    lines += ["".join("0123456789ABCDEF"[v] for v in row).replace("0", ".") for row in to_px(blk)]
    SRC.parent.mkdir(exist_ok=True)
    SRC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SRC)


def build():
    words = SRC.read_text(encoding="utf-8").splitlines()
    rows = words[1:1 + H]
    assert len(rows) == H and all(len(r) == W for r in rows), SRC
    blk = bytearray(0x8000)
    to_tiles([[int(c.replace(".", "0"), 16) for c in r] for r in rows], blk)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hotel.bin").write_bytes(blk[TOP * 32:(TOP + 6) * 32] + blk[(TOP + 16) * 32:(TOP + 22) * 32])
    (OUT / "hotel_sig.bin").write_bytes(bytes.fromhex(words[0].split()[1]))


def test():
    blk = bytearray(i * 7 & 0xFF for i in range(0x8000))
    out = bytearray(0x8000)
    to_tiles(to_px(blk), out)
    for t in [*range(TOP, TOP + 6), *range(TOP + 16, TOP + 22)]:
        assert out[t * 32:(t + 1) * 32] == blk[t * 32:(t + 1) * 32], hex(t)
    print("signs ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["make"]:
        make(sys.argv[2])
    elif sys.argv[1:2] == ["--test"]:
        test()
    else:
        build()
