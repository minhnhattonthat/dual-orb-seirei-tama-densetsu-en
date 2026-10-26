"""font.py: fonts/vwf.txt + tbl/en.tbl -> the VWF data asm/vwf.asm includes (build/vwf/).

  font.bin     256 x 32 bytes: per code, rows 0-15 x (plane 0, plane 1) = one top+bottom tile pair, 2bpp.
               Body colour 3, shadow colour 1 (one pixel right, down, down-right of the body).
  widths.bin   256 bytes: advance in px (0 = not drawn by the VWF)
  flags.bin    256 bytes: 1 = static (original glyph-table tiles, snaps to a cell), 2 = blank (word space)
  shift.bin    8 x 256 words: byte b shifted right by s px -> low byte = left cell, high byte = right cell
  pairs.bin    POOL_N words: top tile of each pool pair (bottom = top + 1)
  tilepair.bin 384 bytes: tile -> pool pair index, FF = not a pool tile
  defs.asm     !POOL_N
Codes with no glyph that the VWF would draw get a hollow box (tofu), so stray Japanese shows up in QA.

    python tools/font.py   (build.py runs it; selftest: python tools/font.py --test)"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

OUT = ROOT / "build" / "vwf"
STATIC = {0x28, 0x2F, 0x30, 0x38, 0x3F}
GLYPHS = 0x30A2  # $00:B0A2 glyph table: code -> (top, bottom) tile words
TOP_ROW = 3      # file row 0 = cell row 3
TOFU = ["######", "#....#", "#....#", "#....#", "#....#", "#....#", "#....#", "#....#", "#....#", "######"]


def parse(path):
    """{char: (rows, advance)}"""
    out, name, adv, rows = {}, None, None, []

    def done():
        if name is not None:
            assert len(rows) == 12, f"{name}: {len(rows)} rows, need 12"
            w = len(rows[0])
            assert all(len(r) == w for r in rows), f"{name}: ragged rows"
            assert w <= 7, f"{name}: {w} px wide, max 7 (+ shadow)"
            out[" " if name == "space" else name] = (rows, adv if adv is not None else w + 1)

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and not set(line) <= {"#", "."}:
            continue
        if line.startswith("== "):
            done()
            parts = line[3:].split()
            name, adv, rows = parts[0], (int(parts[1]) if len(parts) > 1 else None), []
        elif line.strip():
            rows.append(line.strip())
    done()
    return out


def bitmap(rows):
    """32 bytes, 2bpp: body colour 3, shadow colour 1."""
    body = [[False] * 9 for _ in range(17)]
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            body[TOP_ROW + y][x] = c == "#"
    out = bytearray(32)
    for y in range(16):
        p0 = p1 = 0
        for x in range(8):
            b = body[y][x]
            s = not b and ((x and body[y][x - 1]) or (y and body[y - 1][x]) or (x and y and body[y - 1][x - 1]))
            bit = 0x80 >> x
            if b:
                p0 |= bit
                p1 |= bit
            elif s:
                p0 |= bit
        out[2 * y], out[2 * y + 1] = p0, p1
    return bytes(out)


def pool(rom):
    """Tiles the VWF may draw into: glyph-table tiles below $180, minus static glyphs' tiles. Paired (t, t+1)."""
    tiles, keep = set(), set()
    for c in range(0xE0):
        t, b = struct.unpack_from("<HH", rom, GLYPHS + 4 * c)
        (keep if c in STATIC else tiles).update({t & 0x3FF, b & 0x3FF})
    tiles = {t for t in tiles - keep if t < 0x180}
    pairs, t = [], 0
    while t < 0x180:
        if t in tiles and t + 1 in tiles:
            pairs.append(t)
            t += 2
        else:
            t += 1
    return pairs


def build(rom):
    glyphs = parse(ROOT / "fonts" / "vwf.txt")
    tbl = Table.load(ROOT / "tbl" / "en.tbl")
    font, widths, flags = bytearray(256 * 32), bytearray(256), bytearray(256)
    for ch, code in tbl.enc.items():
        c = code[0]
        if c in STATIC:
            flags[c] = 1
            continue
        rows, adv = glyphs[ch]
        font[32 * c:32 * c + 32] = bitmap(rows)
        widths[c] = adv
        if not any(set(r) - {"."} for r in rows):
            flags[c] = 2
    tofu = bitmap(TOFU + ["......"] * 2)
    for c in range(0xE0):  # any other drawable code: tofu
        if not widths[c] and not flags[c] and bytes([c]) not in tbl.ctrl:
            font[32 * c:32 * c + 32] = tofu
            widths[c] = 7
    shift = bytearray()
    for s in range(8):
        for b in range(256):
            shift += bytes([b >> s, (b << (8 - s)) & 0xFF])
    pairs = pool(rom)
    assert len(pairs) < 255
    tilepair = bytearray([0xFF] * 0x180)
    for i, t in enumerate(pairs):
        tilepair[t] = tilepair[t + 1] = i
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("font", font), ("widths", widths), ("flags", flags), ("shift", shift),
                       ("pairs", b"".join(struct.pack("<H", t) for t in pairs)), ("tilepair", tilepair)]:
        (OUT / f"{name}.bin").write_bytes(bytes(data))
    (OUT / "defs.asm").write_text(f"!POOL_N = {len(pairs)}\n")
    return widths, len(pairs)


def width(text, widths=None, tbl=None):
    """Pixel width of an en string (no line breaks): VWF advances; static glyphs snap to the next cell."""
    tbl = tbl or Table.load(ROOT / "tbl" / "en.tbl")
    widths = widths or (OUT / "widths.bin").read_bytes()
    px = 0
    for c in tbl.encode(text):
        if c in STATIC:
            px = (px + 7) // 8 * 8 + 8
        else:
            px += widths[c]
    return px


if __name__ == "__main__":
    from maps import ROM
    w, n = build(ROM.read_bytes())
    if "--test" in sys.argv:
        b = bitmap(["#"] + ["."] * 11)
        assert b[6] == 0xC0 and b[7] == 0x80 and b[8] == 0xC0 and b[9] == 0x00, b.hex()
        assert width("Hi", w) == w[0x11] + w[0x49] and width("_", w) == 8 and width("a_", w) == 16
        print("selftest ok")
    print(f"build/vwf: {n} pool pairs")
