"""widthgate.py: width-gate stress lines for the dialogue box (pipeline phase 5), for build.py --qa.

    python tools/widthgate.py limit PX     -> 3 lines: exactly PX, PX+1..PX+3 (the first glyph past the limit), PX
    python tools/widthgate.py torture      -> every printable glyph of tbl/en.tbl plus double spaces, in lines <= 192 px
Prints the {n}/{fe}-joined text; pass it as  build.py --qa 11:854E="$(python tools/widthgate.py limit 192)"."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402

LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def exact(px, start=""):
    """start + letters, at exactly px if some prefix hits it, else the longest under it."""
    s, i = start, 0
    while font.width(s + LETTERS[i % len(LETTERS)]) <= px:
        s += LETTERS[i % len(LETTERS)]
        i += 1
    return s


def limit(px):
    a = exact(px, "I")
    return "{n}".join([a, exact(px + 3, "I"), a]) + "{end}"


def torture(px=192):
    chars = "0123456789 abcdefghijklmnopqrstuvwxyz  ABCDEFGHIJKLMNOPQRSTUVWXYZ  !?()\",.:;'-+/%&=~×…—_"
    lines, cur = [], ""
    for ch in chars:
        if font.width(cur + ch) > px:
            lines.append(cur)
            cur = ""
        cur += ch
    lines.append(cur)
    pages = ["{n}".join(lines[i:i + 3]) for i in range(0, len(lines), 3)]
    return "{fe}".join(pages) + "{end}"


if __name__ == "__main__":
    if sys.argv[1] == "limit":
        print(limit(int(sys.argv[2])))
    else:
        print(torture())
