"""namechart.py: the English name-entry chart (rename screen, field sub-mode 3) -> build/vwf/chart*.bin for
asm/namechart.asm. Pages are 10 x 4 (the game's row limit for its Latin page, applied to every page); button 0 goes
to the next page, button 1 to the previous one ($21:E6CC / $E6BB).

  chart.bin       3 x 90 codes: what a pick adds ($21:E718 index page*90 + row*10 + col); unused cells 3F
  chart_text.bin  3 words (offsets of each page's string from chart_text) + the strings: every letter at its own
                  {pos} cell (x 6,8,..14 17,..25; y 6,8,10,12), then the button labels on row 24

    python tools/namechart.py   (asm.py runs it)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

OUT = ROOT / "build" / "vwf"
PAGES = [
    ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ.-'&", "0123456789"],
    ["abcdefghij", "klmnopqrst", "uvwxyz.-'&", "0123456789"],
    ["!?,.-'&+=/", "():;\"%~…×・", "", ""],
]
TITLES = ["ABC", "abc", "!?&"]
COLS = [6, 8, 10, 12, 14, 17, 19, 21, 23, 25]
BUTTONS = [6, 12, 18, 23]  # next page, previous page, Back, End (row 24)


def build():
    tbl = Table.load(ROOT / "tbl" / "en.tbl")
    grid, texts = bytearray(), []
    for p, rows in enumerate(PAGES):
        cells = [tbl.encode(r.ljust(10, "_")) for r in rows]
        assert all(len(c) == 10 for c in cells), rows
        grid += b"".join(cells).ljust(90, b"\x3f")
        t = bytearray()
        for y, c in enumerate(cells):
            for x, b in zip(COLS, c):
                if b != 0x3F:
                    t += bytes([0xF4, x, 6 + 2 * y, b])
        labels = [TITLES[(p + 1) % 3], TITLES[(p - 1) % 3], "Back", "End"]
        for x, s in zip(BUTTONS, labels):
            t += bytes([0xF4, x, 24]) + tbl.encode(s)
        texts.append(bytes(t) + b"\xff")
    head, at = bytearray(), 6
    for t in texts:
        head += at.to_bytes(2, "little")
        at += len(t)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "chart.bin").write_bytes(bytes(grid))
    (OUT / "chart_text.bin").write_bytes(bytes(head) + b"".join(texts))
    return grid


if __name__ == "__main__":
    print(len(build()), "codes")
