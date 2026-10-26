"""vwfcheck.py: after tools/lua/vwfdump.lua, compare each VWF pool cell the tilemap buffer shows with VRAM.

    python tools/vwfcheck.py work/qa/DIR
Prints per text row: cells showing pool tiles, how many have VRAM == shadow, VRAM empty, shadow empty, and the
VWF vars (pen, rover, used pairs)."""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

d = Path(sys.argv[1])
vram = (d / "vwf.vram.bin").read_bytes()
wram = (d / "vwf.wram.bin").read_bytes()
tilepair = (ROOT / "build/vwf/tilepair.bin").read_bytes()
w = lambda a: struct.unpack_from("<H", wram, a)[0]  # noqa: E731
n = len((ROOT / "build/vwf/pairs.bin").read_bytes()) // 2
print(f"sig {w(0xF800):04X} pencell {w(0xF802):04X} sub {w(0xF804)} open {w(0xF806):04X} rover {w(0xF808)}"
      f" used {sum(wram[0xF860:0xF860 + n])} pending {sum(wram[0xF920:0xF920 + n])}"
      f" ring {w(0xF820):X}-{w(0xF822):X}")
buf = [w(0x1F000 + 2 * i) & 0x3FF for i in range(2048)]
for r in range(64):
    stats = [0, 0, 0, 0]
    for c in range(32):
        t = buf[r * 32 + c]
        if t < 0x180 and tilepair[t] != 0xFF:
            sh = wram[0xE000 + t * 16:0xE000 + t * 16 + 16]
            vr = vram[0x4000 + t * 16:0x4000 + t * 16 + 16]
            stats[0] += 1
            stats[1] += sh == vr
            stats[2] += not any(vr)
            stats[3] += not any(sh)
    if stats[0]:
        print(f"row {r:2}: pool cells {stats[0]:2}, vram==shadow {stats[1]:2}, vram empty {stats[2]:2}, shadow empty {stats[3]:2}")
