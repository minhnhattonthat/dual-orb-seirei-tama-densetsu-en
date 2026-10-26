"""Extract (phase 4): script/*.json roundtrips to the ROM bytes, and the items cover every text range."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from maps import ROM  # noqa: E402

if not ROM.is_file():
    pytest.skip("original ROM missing", allow_module_level=True)

import census  # noqa: E402
import extract  # noqa: E402
import names  # noqa: E402
import systext  # noqa: E402

ORIG = ROM.read_bytes()
MODEL = extract.items(ORIG)
# banks some pointer form reaches text in; census runs elsewhere are graphics/music/code (no pointer goes there)
TEXT_BANKS = {0x00, 0x01, 0x0C, 0x0F, 0x10, 0x11, 0x12, 0x15, 0x20, 0x21}
NONTEXT = [  # (file start, end, why) text-like bytes in TEXT_BANKS that are data
    (0x000FAC, 0x000FC0, "$00:8FAC code: LDA dp / EOR #$FFFF / STA dp,X runs"),
    (0x1083B0, 0x1084F8, "$21:83B3 byte table of flag values $00/$01/$02/$06/$40/$FF"),
]


def test_script_files_match_rom():
    # every entry's jp encodes to the ROM bytes at its place; the files hold exactly the model's ids
    for name, es in MODEL.items():
        rows = json.loads((extract.SCRIPT / name).read_text(encoding="utf-8"))
        assert [r["id"] for r in rows] == [e["id"] for e in es], f"{name}: re-run tools/extract.py"
        for r, e in zip(rows, es):
            assert r["jp"] == e["jp"], f"{name} {r['id']}: re-run tools/extract.py"
            assert extract.encode(r) == e["data"] == ORIG[e["off"]:e["off"] + len(e["data"])], r["id"]


def test_reextract_keeps_en(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "SCRIPT", tmp_path)
    model = {"names.json": MODEL["names.json"][:2]}
    extract.write(model)
    rows = json.loads((tmp_path / "names.json").read_text(encoding="utf-8"))
    rows[0]["en"], rows[1]["en"], rows[1]["jp"] = "Clothes", "stale", "old jp"
    (tmp_path / "names.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    extract.write(model)
    rows = json.loads((tmp_path / "names.json").read_text(encoding="utf-8"))
    assert [r["en"] for r in rows] == ["Clothes", ""]  # jp changed under the second: its en is dropped


def test_names_tile_region():
    assert names.tiling(ORIG) == []


def test_pointer_targets_are_piece_starts():
    starts = {p["addr"] for p in systext.pieces(ORIG)}
    rs = systext.refs(ORIG)
    out = [hex(a) for a in rs if a & 0xFFFF >= 0x8000 and a >> 16 < 0x7E and a not in starts]
    assert out == []
    assert {a >> 16 for a in rs if a & 0xFFFF >= 0x8000 and a >> 16 < 0x7E} <= TEXT_BANKS


def covered():
    spans = sorted((e["off"], e["off"] + len(e["data"])) for es in MODEL.values() for e in es)
    spans += [(s, e) for s, e, _ in NONTEXT]
    merged = []  # adjacent items join: a census run may span pieces split at FA
    for s, e in sorted(spans):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged


def test_census_runs_covered():
    # every FF-terminated run that reads as text, in a bank text pointers reach, is inside an item
    spans = covered()
    out = []
    for b in sorted(TEXT_BANKS):
        for s, e in census.runs(ORIG, b * 0x8000, b * 0x8000 + 0x8000):
            if not any(lo <= s and e < hi for lo, hi in spans):
                out.append(f"{s:06X} {extract.TBL.decode(ORIG, s, e - s)[0][:30]}")
    assert out == []
