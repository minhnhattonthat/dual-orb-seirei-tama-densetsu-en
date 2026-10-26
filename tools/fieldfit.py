"""fieldfit.py: widths of the item/equipment/magic info line the game builds as {name}:{description} ($0200,
e.g. E7 01 31 3C 01 08 FF; tools/lua/textdump.lua in a shop) and of other fixed fields, against budgets measured
in game (docs/re/windows.md). Prints every entry over its budget; exit 1 if any.

    python -X utf8 tools/fieldfit.py [--all]"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import wrap  # noqa: E402

PAIRS = {"E5": "3C0", "E4": "3C1", "F2": "3C2", "EB": "3C3", "F3": "3C4", "E6": "3C5", "E8": "3C6", "E9": "3C7",
         "E7": "3C8", "EA": "3C9"}  # name table -> description sub-table (same index)
INFO_PX = 232  # info line: shop/menu top box, text x=14..246 (shop_weapon shot)
# battle panel ($20:A44A: JSL $00A8BF at column 8/$0F/$17, row $16; description at column 8, row $19)
BATTLE = {"E6": 88, "F2": 88, "E4": 88, "F3": 88, "EB": 88}  # third field x=160..248 (asm/names.asm moves it)
# description x=64..: up to the count/cost at column $19 (x=200, $20:A57C/A5D0) for items/spells/skills
BATTLE_DESC = {"E6": 184, "F2": 136, "E4": 136, "F3": 136, "EB": 136}


def px(s):
    return wrap.width(re.sub(r"\{(end|fa)\}", "", s))


def check(show_all=False):
    es = {e["id"]: e for e in json.loads((ROOT / "script" / "names.json").read_text(encoding="utf-8"))}
    bad = []
    for t, dt in PAIRS.items():
        i = 1
        while f"{t}:{i:02X}" in es:
            n, dsc = es[f"{t}:{i:02X}"], es.get(f"{dt}:{i:02X}")
            w = px(n["en"]) + px(":") + (px(dsc["en"]) if dsc else 0)
            if w > INFO_PX or show_all:
                bad.append((w, n["id"], n["en"], dsc and dsc["en"]))
            if t in BATTLE and px(n["en"]) > BATTLE[t]:
                bad.append((px(n["en"]), n["id"], n["en"], f"battle field {BATTLE[t]} px"))
            if t in BATTLE and dsc and px(dsc["en"]) > BATTLE_DESC[t]:
                bad.append((px(dsc["en"]), dsc["id"], dsc["en"], f"battle description {BATTLE_DESC[t]} px"))
            i += 1
    return bad


if __name__ == "__main__":
    bad = check("--all" in sys.argv)
    for w, k, n, dsc in sorted(bad, reverse=True):
        print(f"{w:4} {k:6} {n!r:32} {dsc!r}")
    print(f"{len(bad)} info lines over {INFO_PX} px")
    sys.exit(1 if bad and "--all" not in sys.argv else 0)
