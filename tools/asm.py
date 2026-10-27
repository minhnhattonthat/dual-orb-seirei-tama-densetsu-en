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
import namechart  # noqa: E402
import buttons  # noqa: E402

ASAR = ROOT / "tools" / "asar" / "asar.exe"
SIZE = 0x200000
# File offset ranges [lo, hi) the asm may change below the expansion banks (tests/test_vwf.py, insert.allowed)
HOOKS = [(0x2EB6, 0x2EE0), (0x00A9, 0x00AD),  # $00:AEB6 stub, NMI JSL $00E388 -> vwf_nmi
         (0x298F, 0x2992), (0x2A30, 0x2F63), (0x5680, 0x5753),  # asm/names.asm: jump, handlers, helpers
         (0x10250F, 0x102510), (0x10F28D, 0x10F291),  # battle panel field column, save confirm cursor x
         (0x10F29E, 0x10F29F), (0x10F2CD, 0x10F2D2), (0x10F1A1, 0x10F1A5),  # file select "New Game" column, window, cursor
         (0x10E623, 0x10E625), (0x10E719, 0x10E71B), (0x10E739, 0x10E73D), (0x10E985, 0x10E98B),  # namechart.asm
         # menus.asm: magic underlines + description, window records, item icon x/frame, underlines + strings,
         # icon x (whom/town), prompt columns, item window records
         (0x10A22F, 0x10A235), (0x10A375, 0x10A3E3), (0x10B324, 0x10B336), (0x10B568, 0x10B56A),
         (0x10B5F1, 0x10B5F2), (0x10B60C, 0x10B6E0), (0x10B8FF, 0x10B901), (0x10BCB4, 0x10BCB6),
         (0x10B91D, 0x10B91E), (0x10B990, 0x10B991), (0x10BACE, 0x10BACF), (0x10BDC5, 0x10BDC6),
         (0x10BF4F, 0x10BF88),
         # menus.asm town picker: index math, scroll/page/column limits, name cells, cursor brackets
         (0x10ACF3, 0x10ACF8), (0x10AE90, 0x10AE95), (0x10AEC0, 0x10AEC5), (0x10BD7C, 0x10BD81),
         (0x10ADEF, 0x10ADF0), (0x10AE30, 0x10AE31), (0x10AE22, 0x10AE23), (0x10AFCB, 0x10AFCC),
         (0x10AF27, 0x10AF28), (0x10AE50, 0x10AE51), (0x10AF6B, 0x10AF83), (0x10AEEE, 0x10AF06),
         (0x10AED1, 0x10AED3),
         (0x065673, 0x06568D),  # crawl.asm: intro crawl page command -> crawl_page / crawl_tick
         (0x000AEE, 0x000AF2)]  # buttons.asm: unpacker entry -> btn_unpack
NAME_ARRAYS = (0x3422, 0x5680)  # pointer arrays rewritten by insert.names_far (strings now in bank $3F)


def patch(rom: bytes, asm=ROOT / "asm" / "vwf.asm") -> bytes:
    if not ASAR.is_file():
        sys.exit(f"{ASAR} missing: unzip asar191.zip from github.com/RPGHacker/asar/releases (v1.91) there")
    font.build(rom)
    namechart.build()
    buttons.build()
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "rom.sfc"
        p.write_bytes(rom.ljust(SIZE, b"\xff"))
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(asm), str(p)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"asar failed:\n{r.stdout}{r.stderr}")
        return p.read_bytes()
