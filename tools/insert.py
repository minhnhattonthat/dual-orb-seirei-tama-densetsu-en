"""insert.py: put script text into a ROM image (after asm.patch), English or marker.

  insert(rom, mode)   mode "en": each entry's en (tbl/en.tbl) where set, else its original bytes
                      mode "marker": every entry replaced by its id + filler (pipeline phase 5)
Dialogue (script/dialogue_XX.json) is laid out again from the item model (tools/textmap.py): items joined by a
pointer, and each record with the item after it (runs of records and the string after a conditional last record
must stay adjacent), form a component that moves as one. Components fill their own bank first and overflow into
banks $31-$3F; map entries (+10) are rewritten. Names and system text are written in place for now: the en/marker
bytes must fit the original length; spare bytes become {nop} before the terminator so stepped-into blocks keep
their offsets (shortcut: no relocation yet; phase 7 moves them when English outgrows them).

    python tools/insert.py   (build.py calls it)"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import textmap  # noqa: E402
import wrap  # noqa: E402
from extract import items  # noqa: E402
from maps import off  # noqa: E402
from tbl import Table  # noqa: E402

EN = Table.load(ROOT / "tbl" / "en.tbl")
JP = Table.load(ROOT / "tbl" / "jp.tbl")
NEW_BANKS = range(0x31, 0x40)
NOP = 0x3A
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. "
BREAKS = {"n", "fe", "clear", "down", "downn", "pos", "end", "fa", "f0", "f1"}
DIALOGUE_PX = 192  # NPC box: 24 cells (docs/re/text.md); the width gate checks it in game


def script():
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "script").glob("*.json"))}


def fill(px, widths, start=""):
    """start + filler words, as long as fits in px."""
    s, i = start, 0
    while True:
        nxt = s + FILLER[i % len(FILLER)]
        if font.width(nxt.rstrip(), widths, EN) > px:
            return s.rstrip()
        s, i = nxt, i + 1


HEROES = ["21:EF9B", "21:EFA3", "21:EFAB", "21:EFB3"]  # default names, copied to the party at new game
_names = {}


def name_px(tok, widths):
    """Width the marker build's name for {tXX:YY} / {heroN} draws (its in-place marker), else 0."""
    if not _names:
        sc = script()
        _names.update({e["id"]: e for f in ("names.json", "system.json") for e in sc[f]})
    m = re.fullmatch(r"\{t([0-9A-F]{2}):([0-9A-F]{2})\}|\{hero([0-3])\}", tok)
    if not m:
        return 0
    e = _names.get(HEROES[int(m[3])] if m[3] else f"{m[1]}:{m[2]}")
    if not e:
        return 0
    s = marker_inplace(e).split("{")[0].rstrip("_")
    return font.width(s, widths, EN)


def marker_lines(e, widths, px=DIALOGUE_PX):
    """Dialogue marker: the JP's control codes kept, each line's glyphs replaced by filler to px minus the names the
    line draws; id first."""
    out, first, text, used = [], True, False, 0
    for tok in re.split(r"(\{[^}]*\})", e["jp"]):
        if tok.startswith("{"):
            name = tok[1:].split(":")[0].rstrip("}")
            if name in BREAKS:
                if text:
                    out.append(fill(px - used, widths, (e["id"] + " ") if first else ""))
                    first, text = False, False
                used = 0
            used += name_px(tok, widths)
            out.append(tok)
        elif tok:
            text = True
    if first:  # only names/controls: the id goes in front so the box still shows it
        out.insert(0, e["id"] + " ")
    return "".join(out)


def marker_inplace(e):
    """Same byte length as the JP: glyphs (not spaces or static marks) become id + filler, one char per byte."""
    src = (e["id"] + " " + FILLER.replace(" ", "")) * 4
    out, k = [], 0
    for tok in re.split(r"(\{[^}]*\}|\[[0-9A-F]{2}\])", e["jp"]):
        if tok.startswith(("{", "[")):
            out.append(tok)
            continue
        for ch in tok:
            if ch in " ・▲▼▶":
                out.append("_" if ch == " " else ch)
            else:
                c = src[k]
                out.append("_" if c == " " else c)
                k += 1
    return "".join(out)


LONG = []  # in-place entries whose en outgrew the JP bytes (left Japanese until phase 7)
QA = {}  # id -> en text that overrides the mode (build.py --qa ID=text): width-gate stress lines


def encode(e, mode, widths):
    if e["id"] in QA:
        return EN.encode(QA[e["id"]])
    if mode == "marker":
        return EN.encode(marker_lines(e, widths) if "dialogue" in e.get("_file", "") else marker_inplace(e))
    if e["en"]:
        return EN.encode(wrap.wrap(e["en"])[0] if "dialogue" in e.get("_file", "") else e["en"])
    return None


def fit(new, old, eid):
    """In-place bytes: pad with {nop} before the final terminator to the old length."""
    if len(new) > len(old):
        raise ValueError(f"{eid}: {len(new)} bytes, room for {len(old)} (in place)")
    return new[:-1] + bytes([NOP]) * (len(old) - len(new)) + new[-1:]


def components(its):
    parent = list(range(len(its)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    idx = {it["addr"]: i for i, it in enumerate(its)}
    for i, it in enumerate(its):
        links = []
        if it["kind"] == "list":
            links = it["ptrs"]
        elif it["kind"] == "rec":
            links = [it["text"]] + ([its[i + 1]["addr"]] if i + 1 < len(its) else [])
        for a in links:
            if a in idx:
                parent[find(idx[a])] = find(i)
    groups = {}
    for i in range(len(its)):
        groups.setdefault(find(i), []).append(its[i])
    return list(groups.values())


def insert(rom, mode="en"):
    d = bytearray(rom)
    TOP.clear()
    orig = bytes(rom[:0x180000])
    widths = (font.OUT / "widths.bin").read_bytes()
    sc = script()
    model = items(orig)
    # dialogue
    banks, refs = textmap.scan(orig)
    new_text = {}
    for name, es in sc.items():
        if name.startswith("dialogue"):
            for e in es:
                b = encode({**e, "_file": name}, mode, widths)
                if b is not None:
                    new_text[e["id"]] = b
    moved, free = {}, list(NEW_BANKS)
    spill = []
    for b, its in banks.items():
        its = [dict(it, data=new_text.get(f"{b:02X}:{it['addr']:04X}", it.get("data")))
               if it["kind"] == "str" else it for it in its]
        keep, used = [], 0
        for comp in components(its):
            n = sum(textmap.size(it) for it in comp)
            if used + n <= 0x8000:
                keep += comp
                used += n
            else:
                spill.append((b, comp, n))
        place(d, b, b, keep, moved)
    while spill:
        nb = free.pop(0)
        here, used, rest = [], 0, []
        for b, comp, n in spill:
            if used + n <= 0x8000:
                here.append((b, comp))
                used += n
            else:
                rest.append((b, comp, n))
        assert here, "a component larger than a bank"
        for b in {b for b, _ in here}:
            place(d, b, nb, [it for bb, c in here if bb == b for it in c], moved)
        spill = rest
    for i, k in refs.items():
        d[i:i + 3] = moved[k].to_bytes(3, "little")
    # names and system text: in place
    for name in ("names.json", "system.json"):
        for e, m in zip(sc[name], model[name]):
            assert e["id"] == m["id"]
            if e.get("kind") == "grid":
                continue
            new = encode(e, mode, widths)
            if new is None:
                continue
            if e.get("kind") == "fixed":
                new = new.rstrip(b"\xff")[:e["size"]].ljust(e["size"], b"\xff")
            elif len(new) > len(m["data"]) and mode == "en":
                LONG.append(e["id"])  # shortcut: keeps the JP bytes; phase 7 relocates names/system text
                continue
            else:
                new = fit(new, m["data"], e["id"])
            d[m["off"]:m["off"] + len(new)] = new
    return bytes(d)


TOP = {}  # bank -> next free address


def place(d, src_bank, dst_bank, its, moved):
    """Lay its (items of one source bank, kept in order) out at dst_bank's next free address. A text bank's own
    layout starts at $8000 and FF-fills the bank."""
    its = sorted(its, key=lambda it: it["addr"])
    base = 0x8000 if src_bank == dst_bank else TOP.get(dst_bank, 0x8000)
    data, new = textmap.layout(its, base)
    assert base + len(data) <= 0x10000, f"bank {dst_bank:02X} overflows"
    o = off(dst_bank, base)
    d[o:o + len(data)] = data
    if src_bank == dst_bank:
        d[o + len(data):off(dst_bank, 0x8000) + 0x8000] = b"\xff" * (0x8000 - len(data))
    TOP[dst_bank] = base + len(data)
    moved.update({src_bank << 16 | a: dst_bank << 16 | n for a, n in new.items()})


if __name__ == "__main__":
    e = {"id": "0F:8038", "jp": "{hero0}さん、{n}あ{fe}い{end}"}
    print(marker_lines(e, (font.OUT / "widths.bin").read_bytes()))
    print(marker_inplace({"id": "21:9D4C", "jp": "まほう  アイテム{end}"}))
