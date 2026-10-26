"""peek.py OFF [LEN]: decode LEN bytes of the original ROM at file offset OFF with tbl/jp.tbl (hex dump beside it)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table

ROM = ROOT / "rom" / "Dual Orb - Seirei Tama Densetsu (Japan).sfc"
d = ROM.read_bytes()
t = Table.load(ROOT / "tbl" / "jp.tbl")
off = int(sys.argv[1], 16)
n = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100
for o in range(off, off + n, 32):
    text, _ = t.decode(d, o, 32)
    print("%06X %s  %s" % (o, d[o:o + 32].hex(), text))
