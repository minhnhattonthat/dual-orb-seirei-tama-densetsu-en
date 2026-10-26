"""extract.py: dump every text item of the original ROM to script/*.json, keeping existing translations.

  script/dialogue_XX.json  map dialogue strings of text bank XX (tools/textmap.py); id = BB:AAAA. Translate them
                           all: strings behind "dead" records (after an NPC's unconditional one) include shop lines
  script/names.json        bank $00 name/description tables (tools/names.py); id = <code>:<1-based index>,
                           e.g. E5:01 for {tE5:01}; 3C0-3C9 are the {dict} sub-tables
  script/system.json       menus, shops, battle, intro, credits (tools/systext.py); id = BB:AAAA, block = where,
                           refs = known pointers to it (none: reached by stepping from the piece before)
Entry fields: id, jp (tbl/jp.tbl text, exact bytes), en ("" until translated), plus the ones above. kind "fixed"
entries are padded with FF to size; jp holds the name without the padding. A "grid" entry is the name-entry chart.
An en survives a re-extract while its jp is unchanged.

items(d) is the model the tests check: every item with its file offset and bytes."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import names  # noqa: E402
import systext  # noqa: E402
import textmap  # noqa: E402
from maps import ROM, off  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"
TBL = Table.load(ROOT / "tbl" / "jp.tbl")


def jp(data):
    text, n = TBL.decode(data, 0, len(data))
    assert n == len(data)
    return text


def items(d):
    """{file name: [entry dict with 'off' (file offset) and 'data' (bytes) added]}."""
    out = {}
    banks, _ = textmap.scan(d)
    for b, its in banks.items():
        out[f"dialogue_{b:02X}.json"] = [
            {"id": f"{b:02X}:{it['addr']:04X}", "jp": jp(it["data"]), "en": "", "off": off(b, it["addr"]),
             "data": it["data"]} for it in its if it["kind"] == "str"]
    es = []
    for name, a, strs in names.scan(d):
        for i, p, data in strs:
            es.append({"id": f"{name}:{i:02X}", "jp": jp(data), "en": "", "off": off(0, p), "data": data})
    out["names.json"] = es
    rs = systext.refs(d)
    es = []
    for p in systext.pieces(d):
        if p["kind"] == "data":
            continue
        e = {"id": p["id"], "jp": "", "en": "", "block": p["block"]}
        if p["kind"] == "fixed":
            body = p["data"].rstrip(b"\xff")
            e.update(jp=jp(body), kind="fixed", size=len(p["data"]))
        else:
            e["jp"] = jp(p["data"])
            if p["kind"] == "grid":
                e["kind"] = "grid"
        if p["addr"] in rs:
            e["refs"] = rs[p["addr"]]
        es.append({**e, "off": off(p["addr"] >> 16, p["addr"]), "data": p["data"]})
    out["system.json"] = es
    return out


def encode(e):
    """Bytes of an entry's jp as the ROM holds them."""
    data = TBL.encode(e["jp"])
    return data.ljust(e["size"], b"\xff") if e.get("kind") == "fixed" else data


def write(model):
    SCRIPT.mkdir(exist_ok=True)
    for name, es in model.items():
        path = SCRIPT / name
        old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))} if path.is_file() else {}
        rows = []
        for e in es:
            row = {k: v for k, v in e.items() if k not in ("off", "data")}
            prev = old.get(e["id"])
            if prev and prev["jp"] == row["jp"]:
                row["en"] = prev["en"]
            rows.append(row)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"script/{name}: {len(rows)} entries, {sum(bool(r['en']) for r in rows)} translated")


if __name__ == "__main__":
    write(items(ROM.read_bytes()))
