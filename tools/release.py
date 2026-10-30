"""release.py: build -> tests -> smoke -> jp_left -> visual-QA gate -> checksum -> BPS (re-applied, compared) -> zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure. Writes release/DualOrb_EN_v<version>.{bps,zip} + README.txt (local, gitignored) and keeps
the playable patched image in build/dual_orb_en_v<version>.sfc. Refuses to overwrite an existing version's files
without --force. The debug tool is Lua only (tools/debug/warp.lua), so no debug code is ever in the ROM. Never
publishes anything.

jp_left scans the four dialogue banks (re-laid whole, so any unchanged Japanese there is a miss); names and system
text are covered by tests/test_extract.py (every census run is an extracted entry) and lint (no entry left Japanese).
"""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

ROM = ROOT / "rom" / "Dual Orb - Seirei Tama Densetsu (Japan).sfc"
BUILT = ROOT / "build" / "dual_orb_en.sfc"
QA = ROOT / "work" / "qa"
NAME = "DualOrb_EN"
DIALOGUE = ["78000-7FFFF", "88000-97FFF", "A8000-AFFFF"]  # banks $0F, $11-$12, $15
PY = [sys.executable, "-X", "utf8"]


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    if subprocess.run([*PY, *map(str, cmd)], cwd=ROOT).returncode:
        sys.exit(f"release: failed: {cmd[0]}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.2")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()
    out = ROOT / "release"
    patch, zpath = out / f"{NAME}_v{a.version}.bps", out / f"{NAME}_v{a.version}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"release: {patch.name} or {zpath.name} exists; pass --force to overwrite")

    run(ROOT / "tools" / "build.py")
    run(ROOT / "tools" / "check.py")
    run(Path(SCRIPTS) / "emu.py", BUILT, "--out", QA / "smoke", "--route", ROOT / "tools" / "routes" / "boot.txt",
        "--smoke")
    run(Path(SCRIPTS) / "jp_left.py", BUILT, "--tbl", ROOT / "tbl" / "jp.tbl", "--orig", ROM,
        *[x for r in DIALOGUE for x in ("--range", r)], "--known", ROOT / "tools" / "jp_known.txt")
    # shortcut: the gate checks the tour's sheets, not that the tour shot this build; re-tour after any change
    run(Path(SCRIPTS) / "qa_gate.py", "check", QA / "manifest.tsv", QA / "verdicts")

    final = ROOT / "build" / f"dual_orb_en_v{a.version}.sfc"
    run(ROOT / "tools" / "bps.py", "snes-checksum", BUILT, "--out", final)
    out.mkdir(exist_ok=True)
    run(ROOT / "tools" / "bps.py", "make", ROM, final, patch)
    work = ROOT / "work" / "release"
    work.mkdir(parents=True, exist_ok=True)
    check = work / "reapplied.sfc"
    run(ROOT / "tools" / "bps.py", "apply", ROM, patch, check)
    if check.read_bytes() != final.read_bytes():
        sys.exit("release: the re-applied patch differs from the build")
    check.unlink()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = (readme.replace("{VERSION}", a.version).replace("{BASE}", hashes(ROM.read_bytes()))
              .replace("{PATCHED}", hashes(final.read_bytes())))
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release: {zpath.relative_to(ROOT)} (patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}); "
          f"playable image {final.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
