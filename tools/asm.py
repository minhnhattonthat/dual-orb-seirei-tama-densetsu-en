"""asm.py: apply asm/vwf.asm to a ROM image with tools/asar/asar.exe (asar 1.91, github.com/RPGHacker/asar).

patch(rom) -> bytes: the ROM padded with FF to 2 MB (banks $30-$3F; the header already says 2 MB), font data
regenerated (tools/font.py), then asar run on a temp copy. The release step owns the checksum."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402

ASAR = ROOT / "tools" / "asar" / "asar.exe"
SIZE = 0x200000


def patch(rom: bytes, asm=ROOT / "asm" / "vwf.asm") -> bytes:
    if not ASAR.is_file():
        sys.exit(f"{ASAR} missing: unzip asar191.zip from github.com/RPGHacker/asar/releases (v1.91) there")
    font.build(rom)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "rom.sfc"
        p.write_bytes(rom.ljust(SIZE, b"\xff"))
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(asm), str(p)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"asar failed:\n{r.stdout}{r.stderr}")
        return p.read_bytes()
