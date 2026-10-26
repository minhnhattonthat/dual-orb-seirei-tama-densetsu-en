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
HOOKS = [(0x2EB6, 0x2EE0), (0x00A9, 0x00AD)]  # $00:AEB6 stub, NMI JSL $00E388 -> vwf_nmi


def hooked(i):
    return any(lo <= i < hi for lo, hi in HOOKS)


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
    assert all(hooked(i) for i in changed(ORIG, out))


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
