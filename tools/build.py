"""build.py: build/dual_orb_en.sfc from the dump in rom.sha1.

Lays every text bank out again from the item model (tools/textmap.py) and rewrites the map entries' NPC-list
pointers. With no edits the output is byte-identical to the original (tests/test_identity.py)."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import asm  # noqa: E402
import check_rom  # noqa: E402
import insert  # noqa: E402
from maps import ROM, off  # noqa: E402
from textmap import layout, scan  # noqa: E402

OUT = ROOT / "build" / "dual_orb_en.sfc"


def build(orig: bytes) -> bytes:
    d = bytearray(orig)
    banks, refs = scan(orig)
    moved = {}
    for b, its in banks.items():
        data, new = layout(its, 0x8000)
        o = off(b, 0x8000)
        d[o:o + len(data)] = data
        moved.update({b << 16 | a: b << 16 | n for a, n in new.items()})
    for i, k in refs.items():  # map entry +10: 24-bit NPC-list pointer
        d[i:i + 3] = moved[k].to_bytes(3, "little")
    return bytes(d)


def patched(orig: bytes, mode="en") -> bytes:
    """VWF engine (asm/vwf.asm) + script text (tools/insert.py); mode "marker" = the phase-5 marker build."""
    return insert.insert(asm.patch(orig), mode)


if __name__ == "__main__":
    check_rom.check()
    orig = ROM.read_bytes()
    mode = "marker" if "--marker" in sys.argv else "en"
    for i, a in enumerate(sys.argv):  # --qa ID=text (repeatable): override one entry, e.g. a width-gate line
        if a == "--qa":
            k, _, v = sys.argv[i + 1].partition("=")
            insert.QA[k] = v
    out = patched(orig, mode) if "--identity" not in sys.argv else build(orig)
    path = OUT.with_name("dual_orb_marker.sfc") if mode == "marker" else OUT
    if "--out" in sys.argv:
        path = (ROOT / sys.argv[sys.argv.index("--out") + 1]).resolve()
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(out)
    print(path.relative_to(ROOT), hashlib.sha1(out).hexdigest(), "identical" if out == orig else "patched")
    if insert.LONG:
        print(f"{len(insert.LONG)} in-place entries too long, left Japanese until phase 7: {' '.join(insert.LONG[:12])}")
