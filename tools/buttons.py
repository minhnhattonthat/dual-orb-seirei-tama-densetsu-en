"""buttons.py: the battle command buttons (アタック / オートバトル / にげる, docs/re/graphics.md G6) in English.

They are 4bpp sprite tiles in the compressed block $29:EE12 (format not decoded), unpacked to $7E:8000 by
$00:8AEE. asm/buttons.asm hooks $00:8AEE and, when the unpacked block holds the Japanese buttons (SIG below),
copies build/vwf/buttons.bin over them. gfx/buttons.txt is the source: per button 16 rows x 64 px of palette
indices (hex, '.' = 0), sprite palette 2.

    python -X utf8 tools/buttons.py make WRAM.bin   gfx/buttons.txt from a WRAM dump taken right after the unpack
                                                   (tools/lua/btnwram.lua), English labels drawn over the Japanese
    python -X utf8 tools/buttons.py                 build/vwf/buttons.bin (build.py runs it); --test self-check
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "gfx" / "buttons.txt"
OUT = ROOT / "build" / "vwf"
# 16x16 sprites (tile n: n, n+1 top row, n+16, n+17 bottom row), left to right
BUTTONS = {"attack": [0x68, 0xC8, 0xCA, 0xCC], "auto": [0xC0, 0xC2, 0xC4, 0xC6], "flee": [0x88, 0x8A, 0x8C, 0x8E]}
LABELS = {"attack": "ATTACK", "auto": "AUTO", "flee": "FLEE"}
# block byte ranges the copy writes, in buttons.bin order (asm/buttons.asm has the same list)
RANGES = [(0x0D00, 0x0D40), (0x0F00, 0x0F40), (0x1100, 0x1200), (0x1300, 0x1400), (0x1800, 0x19C0), (0x1A00, 0x1BC0)]
SIG = 0x1100  # 16 bytes here identify the Japanese block (first tile of にげる)
X0, X1, Y0, Y1 = 7, 57, 3, 12  # label area (inclusive) inside a button
BODY, EDGE, LETTERS = 8, 1, {8, 1}
FONT = {  # 5x8 caps, '#' = body
    "A": [".###.", "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#....", "#...#", ".###."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#....", "#...."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
}


def tiles_to_px(blk, sprites):
    """64x16 index grid of one button from the 4bpp block"""
    g = [[0] * 64 for _ in range(16)]
    for y in range(16):
        for x in range(64):
            t = sprites[x // 16] + (x % 16) // 8 + (16 if y >= 8 else 0)
            b = blk[t * 32:(t + 1) * 32]
            g[y][x] = sum(((b[(p // 2) * 16 + (y % 8) * 2 + (p & 1)] >> (7 - x % 8)) & 1) << p for p in range(4))
    return g


def px_to_tiles(g, sprites, blk):
    for y in range(16):
        for x in range(64):
            t = sprites[x // 16] + (x % 16) // 8 + (16 if y >= 8 else 0)
            for p in range(4):
                i = t * 32 + (p // 2) * 16 + (y % 8) * 2 + (p & 1)
                bit = 1 << (7 - x % 8)
                blk[i] = (blk[i] | bit) if g[y][x] >> p & 1 else (blk[i] & ~bit)


def relabel(g, text):
    """Japanese label -> English: the stripes (period 23, rising to the right) restored under the old letters, then
    the new ones drawn centred, body 8 with a highlight 1 above and left of each stroke, like the original's."""
    top, bottom = g[Y0 - 1][:], g[Y1 + 1][:]  # the inner rows just above and below the label are letter-free
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):  # stripes rise to the right: follow the diagonal to a clean row
            u = x + y - (Y0 - 1)
            g[y][x] = top[u] if u <= X1 else bottom[x - (Y1 + 1 - y)]
    w = 6 * len(text) - 1
    left, top = X0 + (X1 - X0 + 1 - w) // 2 + 1, Y0 + 1
    body = {(left + 6 * i + c, top + r) for i, ch in enumerate(text) for r, row in enumerate(FONT[ch])
            for c, v in enumerate(row) if v == "#"}
    for x, y in body:
        for ex, ey in ((x, y - 1), (x - 1, y)):
            if (ex, ey) not in body:
                g[ey][ex] = EDGE
    for x, y in body:
        g[y][x] = BODY
    return g


def make(dump):
    blk = Path(dump).read_bytes()[0x8000:0xA000]
    lines = [f"sig {blk[SIG:SIG + 16].hex()}"]
    for name, sprites in BUTTONS.items():
        g = relabel(tiles_to_px(blk, sprites), LABELS[name])
        lines.append(name)
        lines += ["".join("0123456789ABCDEF"[v] for v in row).replace("0", ".") for row in g]
    SRC.parent.mkdir(exist_ok=True)
    SRC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SRC)


def parse():
    words = SRC.read_text(encoding="utf-8").splitlines()
    sig = bytes.fromhex(words[0].split()[1])
    grids = {}
    for i, name in enumerate(BUTTONS):
        rows = words[2 + 17 * i:2 + 17 * i + 16]
        assert words[1 + 17 * i] == name and len(rows) == 16 and all(len(r) == 64 for r in rows), name
        grids[name] = [[int(c.replace(".", "0"), 16) for c in r] for r in rows]
    return sig, grids


def build():
    sig, grids = parse()
    blk = bytearray(0x2000)
    for name, sprites in BUTTONS.items():
        px_to_tiles(grids[name], sprites, blk)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "buttons.bin").write_bytes(b"".join(blk[lo:hi] for lo, hi in RANGES))
    (OUT / "buttons_sig.bin").write_bytes(sig)


def test():
    blk = bytearray(range(256)) * 32
    g = tiles_to_px(blk, BUTTONS["flee"])
    out = bytearray(0x2000)
    px_to_tiles(g, BUTTONS["flee"], out)
    for s in BUTTONS["flee"]:
        for t in (s, s + 1, s + 16, s + 17):
            assert out[t * 32:(t + 1) * 32] == blk[t * 32:(t + 1) * 32], hex(t)
    covered = {t for s in sum(BUTTONS.values(), []) for t in (s, s + 1, s + 16, s + 17)}
    assert covered == {o // 32 for lo, hi in RANGES for o in range(lo, hi)}, "RANGES must be exactly the tiles"
    print("buttons ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["make"]:
        make(sys.argv[2])
    elif sys.argv[1:2] == ["--test"]:
        test()
    else:
        build()
