"""peek.py OFF [LEN] [--split]: decode LEN bytes of the original ROM at file offset OFF with tbl/jp.tbl (hex dump
beside it). --split: one line per string instead, cut after each FF/FA (args of control codes skipped)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table

ROM = ROOT / "rom" / "Dual Orb - Seirei Tama Densetsu (Japan).sfc"
d = ROM.read_bytes()
t = Table.load(ROOT / "tbl" / "jp.tbl")
args = [a for a in sys.argv[1:] if a != "--split"]
off = int(args[0], 16)
n = int(args[1], 16) if len(args) > 1 else 0x100
if "--split" in sys.argv:
    argc = {c[0]: k for c, (name, k) in t.ctrl.items()}
    o = off
    while o < off + n:
        s = o
        while o < off + n and d[o] not in (0xFF, 0xFA):
            o += 1 + argc.get(d[o], 0)
        o += 1
        print("%06X %02X:%04X %s" % (s, s // 0x8000, 0x8000 | s % 0x8000, t.decode(d, s, o - s)[0]))
else:
    for o in range(off, off + n, 32):
        text, _ = t.decode(d, o, 32)
        print("%06X %s  %s" % (o, d[o:o + 32].hex(), text))
