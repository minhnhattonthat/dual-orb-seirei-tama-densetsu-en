"""wrap.py: lay authored English dialogue out into the NPC box (192 px x 3 lines, docs/re/windows.md).

Translators write each page as running text; {fe} ends a page, {n} forces a break. wrap() adds {n} at word spaces so
no line passes the box width, and starts a new page ({fe}) after 3 lines. Names count at their English width
(script/names.json en, else 8 px per JP glyph); party names at HERO_PX, the cap for the name-entry screen.

    python tools/wrap.py "text"     -> the wrapped text and each line's width (dry-run fitter for translators)"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
from tbl import Table  # noqa: E402

BOX_PX = 192
LINES = 3
HERO_PX = 42  # shortcut: budget for a party name the player types; phase 7 caps name entry to fit it
EN = Table.load(ROOT / "tbl" / "en.tbl")
TOK = re.compile(r"(\{[^}]*\})")
PAGE_END = {"{fe}", "{end}", "{f0}", "{f1}", "{fa}"}
_names = {}
_widths = []


def widths():
    if not _widths:
        _widths.append((font.OUT / "widths.bin").read_bytes())
    return _widths[0]


def name_px(tok):
    """Width a name token draws: party names HERO_PX, table names their en (or JP glyph count x 8), else 0."""
    if re.fullmatch(r"\{hero[0-3]\}", tok):
        return HERO_PX
    m = re.fullmatch(r"\{t([0-9A-F]{2}):([0-9A-F]{2})\}", tok)
    if not m:
        return 0
    if not _names:
        for f in ("names.json", "system.json"):
            _names.update({e["id"]: e for e in json.loads((ROOT / "script" / f).read_text(encoding="utf-8"))})
    e = _names.get(f"{m[1]}:{int(m[2], 16):02X}")
    if not e:
        return 0
    if e["en"]:
        return width(e["en"].replace("{end}", ""))
    return 8 * len(TOK.sub("", e["jp"]))


def width(s):
    """Pixel width of one line of en text with control tokens."""
    px = 0
    for part in TOK.split(s):
        if part.startswith("{"):
            px += name_px(part)
        elif part:
            px += font.width(part, widths(), EN)
    return px


def wrap(text, px=BOX_PX, lines=LINES):
    """-> (wrapped text, problems). Problems: a word wider than the box."""
    out, bad, cur, n_lines = [], [], "", 1
    for part in re.split(r"(\{(?:n|fe|end|f0|f1|fa)\})", text):
        if part == "{f0}" and cur:  # yes/no goes on its own line: its cursor sits at fixed cells 1 and 5
            out.append(cur)
            cur = ""
            n_lines += 1
            out.append("{fe}" if n_lines > lines else "{n}")
            n_lines = 1 if n_lines > lines else n_lines
        if part == "{n}" or part in PAGE_END:
            out.append(cur)
            cur = ""
            if part == "{n}":
                n_lines += 1
                if n_lines > lines:
                    out.append("{fe}")
                    n_lines = 1
                else:
                    out.append("{n}")
            else:
                out.append(part)
                n_lines = 1
            continue
        for i, word in enumerate(part.split(" ")):
            if i == 0:
                cand = cur + word
            else:
                cand = cur + " " + word
            if width(cand) <= px or (i == 0 and not cur):
                cur = cand
                if width(cur) > px:
                    bad.append(f"too wide: {word!r}")
                continue
            out.append(cur)
            n_lines += 1
            if n_lines > lines:
                out.append("{fe}")
                n_lines = 1
            else:
                out.append("{n}")
            cur = word
            if width(cur) > px:
                bad.append(f"too wide: {word!r}")
    out.append(cur)
    return "".join(out), bad


def pages(wrapped):
    """Wrapped text -> list of pages, each a list of lines (control tokens kept)."""
    return [p.split("{n}") for p in re.split(r"\{fe\}", re.sub(r"\{(end|f0|f1|fa)\}", "", wrapped))]


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        w, bad = wrap("a b{n}c{n}d{n}e{end}")
        assert w == "a b{n}c{n}d{fe}e{end}" and not bad, w
        long = " ".join(["word"] * 40) + "{end}"
        w, _ = wrap(long)
        assert all(width(line) <= BOX_PX for p in pages(w) for line in p) and "{fe}" in w, w
        assert w.replace("{n}", " ").replace("{fe}", " ") == long
        print("selftest ok")
        sys.exit()
    w, bad = wrap(sys.argv[1])
    for i, p in enumerate(pages(w)):
        for line in p:
            print(f"p{i + 1} {width(line):4d}px  {line}")
    for b in bad:
        print("ERROR", b)
    print(w)
