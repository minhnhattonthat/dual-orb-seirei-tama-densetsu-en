"""VWF engine + inserter: builds its own ROMs (asar must be in tools/asar/)."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from maps import ROM  # noqa: E402

if not ROM.is_file():
    pytest.skip("original ROM missing", allow_module_level=True)

import asm  # noqa: E402
import font  # noqa: E402
import insert  # noqa: E402
import textmap  # noqa: E402
from maps import off, w16  # noqa: E402

ORIG = ROM.read_bytes()
HOOKS, NAME_ARRAYS = asm.HOOKS, asm.NAME_ARRAYS


def hooked(i, arrays=False):
    return any(lo <= i < hi for lo, hi in HOOKS + ([NAME_ARRAYS] if arrays else []))


@pytest.fixture(scope="module")
def engine():
    return asm.patch(ORIG)


def changed(a, b, lo=0, hi=0x180000):
    return [i for i in range(lo, hi) if a[i] != b[i]]


def test_engine_touches_only_hook(engine):
    assert len(engine) == 0x200000
    assert all(hooked(i) for i in changed(ORIG, engine))
    assert engine[0x2EB6:0x2EBB] == bytes.fromhex("08 22 00 80 b0".replace(" ", ""))


def test_untranslated_en_build_keeps_text(engine, monkeypatch):
    blank = {name: [dict(e, en="") for e in es] for name, es in insert.script().items()}
    monkeypatch.setattr(insert, "script", lambda: blank)
    out = insert.insert(engine, "en")
    assert all(hooked(i, arrays=True) for i in changed(ORIG, out))


def test_en_dialogue_reaches_wrapped_english(engine):
    out = insert.insert(engine, "en")
    banks, refs = textmap.scan(ORIG)
    en = {e["id"]: e for name, es in insert.script().items() if name.startswith("dialogue") for e in es}
    seen = 0
    for i, k in list(refs.items())[:40]:
        a = int.from_bytes(out[i:i + 3], "little")
        first = w16(out, off(a >> 16, a))
        text = w16(out, off(a >> 16, first) + 8)
        s, _ = insert.EN.decode(out, off(a >> 16, text))
        orig_text = w16(ORIG, off(k >> 16, w16(ORIG, off(k >> 16, k & 0xFFFF))) + 8)
        e = en[f"{k >> 16:02X}:{orig_text:04X}"]
        assert s == (insert.wrap.wrap(e["en"])[0] if e["en"] else e["jp"]), e["id"]  # token-only strings stay
        seen += 1
    assert seen == 40


def test_build_changes_only_allowed_ranges(engine):
    import romdiff
    ok = insert.allowed(ORIG)
    out = insert.insert(engine, "en")
    assert romdiff.check(ORIG, out, ok, [])[0] == []
    bad = bytearray(out)
    bad[0x7FC0] ^= 1  # header title: outside every range
    assert romdiff.check(ORIG, bytes(bad), ok, [])[0]


def test_marker_build_reaches_markers(engine):
    out = insert.insert(engine, "marker")
    banks, refs = textmap.scan(ORIG)
    widths = (font.OUT / "widths.bin").read_bytes()
    seen = 0
    for i, k in list(refs.items())[:40]:
        a = int.from_bytes(out[i:i + 3], "little")
        b = a >> 16
        first = w16(out, off(b, a) + 0)  # NPC 0's first record
        text = w16(out, off(b, first) + 8)
        s, _ = insert.EN.decode(out, off(b, text))
        assert re.search(r"[0-9A-F]{2}:[0-9A-F]{4} ", s), s
        seen += 1
    assert seen
    assert font.width("Hi", widths) == widths[0x11] + widths[0x49]


def test_pool_excludes_static():
    pairs = font.pool(ORIG)
    tiles = {t for p in pairs for t in (p, p + 1)}
    assert not tiles & {0x16A, 0x48, 0x58, 0x4F, 0x5F, 0x60, 0x70}
    assert max(tiles) < 0x180 and len(pairs) > 150


def test_namechart_sites_match_original():
    """asm/namechart.asm patches these exact instructions ($21:E61E page-2 row limit, grid base, pick, page draw)."""
    import namechart
    at = lambda a, n: ORIG[off(0x21, a):off(0x21, a) + n].hex()  # noqa: E731
    assert at(0xE61E, 7) == "a532c90200d01c"
    assert at(0xE718, 3) == "69d5ec" and at(0xE739, 4) == "e230b200"
    assert at(0xE981, 10) == "547f7eabadd31309e0ff"
    grid = namechart.build()
    assert len(grid) == 270 and grid.count(0x3F) == 270 - 3 * 40 + 20  # 4 rows a page; symbols page has 2


def test_crawl_site_matches_original():
    """asm/crawl.asm rewrites $0C:D673-$D695 (cmd 1: clear half, print page $24 at row $22); the table at $D696 stays."""
    o = off(0x0C, 0xD673)
    assert ORIG[o:o + 0x23].hex() == "a520c90100f00160209ed6a5240aaabd96d6" \
                                      "85b3a90c0085b5a20400a42222bfa80060"
    assert [w16(ORIG, off(0x0C, 0xD696) + 2 * i) for i in range(4)] == [0xD6CD, 0xD7E3, 0xD8AE, 0xD9A6]


def test_names_hook_sites_match_original():
    """asm/names.asm patches these exact instruction sequences."""
    import names
    for a in [0xAB62 + 0x32 * k for k in range(13)]:
        o = off(0, a)
        assert ORIG[o:o + 3] == bytes([0xBD]) + ORIG[o + 1:o + 3]
        assert names.tables(ORIG)[next(n for n, t in names.TABLES.items() if t == w16(ORIG, o + 1))]
        assert ORIG[o + 3:o + 7] == bytes.fromhex("8500e220") and ORIG[o + 10:o + 15] == bytes.fromhex("b10099110e")
    assert ORIG[off(0, 0xAA3F):off(0, 0xAA43)] == bytes.fromhex("8502e220")
    assert ORIG[off(0, 0xAA46):off(0, 0xAA4B)] == bytes.fromhex("b10299110e")
    for a in (0xAA83, 0xAAC0, 0xAAFC, 0xAB3E):
        assert ORIG[off(0, a):off(0, a) + 3] == bytes.fromhex("9d110e")
    for a in (0xAF35, 0xAF41, 0xAF60):
        assert ORIG[off(0, a):off(0, a) + 3] == bytes.fromhex("b9110e")
    assert ORIG[off(0, 0xA98F):off(0, 0xA992)] == bytes.fromhex("20b6ae")
    assert max(a + 2 * len(s) for _, a, s in names.scan(ORIG)) <= 0xD680  # helpers after the last array
