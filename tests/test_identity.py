"""Identity build: unpack the text banks, repack with no edits, get the original bytes back."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from maps import ROM  # noqa: E402

if not ROM.is_file():
    pytest.skip("original ROM missing", allow_module_level=True)

import build  # noqa: E402
import textmap  # noqa: E402
from tbl import Table  # noqa: E402

ORIG = ROM.read_bytes()
BANKS, REFS = textmap.scan(ORIG)


def test_banks_tile():
    for b, its in BANKS.items():
        assert textmap.tiling(its) == [], f"bank {b:02X}"


def test_build_identical():
    assert build.build(ORIG) == ORIG


def test_layout_moves_pointers():
    # the same bank laid out $100 higher: every list/record pointer inside it shifts by $100
    its = BANKS[0x0F]
    data, new = textmap.layout(its, 0x8100)
    assert all(n == a + 0x100 for a, n in new.items())
    rec = next(it for it in its if it["kind"] == "rec")
    o = new[rec["addr"]] - 0x8100 + 8
    assert int.from_bytes(data[o:o + 2], "little") == rec["text"] + 0x100


RECS = {b << 16 | it["addr"]: it for b, its in BANKS.items() for it in its if it["kind"] == "rec"}


def chain_len(bank, p):
    """Records the game can show from p: up to the unconditional one, or until the run of records ends."""
    n = 0
    while (bank << 16 | p) in RECS:
        r = RECS[bank << 16 | p]
        n += 1
        if not any(r["conds"]):
            break
        p += textmap.size(r)
    return n


def shown(d):
    """What the game can show per map entry: each NPC's records with their string bytes."""
    out = []
    for i in sorted(REFS):
        bank, a = d[i + 2], textmap.w16(d, i)
        lst = next(it for it in BANKS[bank] if it["addr"] == REFS[i] & 0xFFFF)
        for k, p0 in enumerate(lst["ptrs"]):
            p = textmap.w16(d, textmap.off(bank, a) + 2 * k)
            for _ in range(chain_len(bank, p0)):
                r = textmap.record(d, bank, p)
                s = textmap.off(bank, r["text"])
                out.append((r["conds"], r["set"], r["clear"], d[s:textmap.string_end(d, bank, r["text"])]))
                p += textmap.size(r)
    return out


def test_reversed_layout_shows_same_text():
    # every bank laid out back to front. A run of records stays one unit (the game steps from one to the next), and
    # so does whatever follows a conditional last record ($11:A334 runs into its string)
    d = bytearray(ORIG)
    moved = {}
    for b, its in BANKS.items():
        units = []
        for it in its:
            last = units and units[-1][-1]
            if last and last["kind"] == "rec" and (it["kind"] == "rec" or any(last["conds"])):
                units[-1].append(it)
            else:
                units.append([it])
        data, new = textmap.layout([it for u in units[::-1] for it in u], 0x8000)
        d[textmap.off(b, 0x8000):textmap.off(b, 0x8000) + len(data)] = data
        moved.update({b << 16 | a: b << 16 | n for a, n in new.items()})
    for i, k in REFS.items():
        d[i:i + 3] = moved[k].to_bytes(3, "little")
    assert bytes(d) != ORIG
    assert shown(d) == shown(ORIG)


def test_strings_roundtrip():
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for its in BANKS.values():
        for it in its:
            if it["kind"] == "str":
                text, n = t.decode(it["data"])
                assert n == len(it["data"]) and t.encode(text) == it["data"], hex(it["addr"])
