"""Warp to every scene in scenes.lua: shot + savestate per scene, one contact sheet, pass/fail per scene.

    python -X utf8 tools/debug/warp_all.py [--rom ROM] [--jobs 4] [scene ...]

Writes work/qa/warp_all/<scene>/ (log.txt, warp.png), work/states/<scene>.mss and work/qa/warp_all/sheet.png.
A scene fails when the run errors, never logs "warp: ready", or logs "warp: check FAIL".
"""
import argparse, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path(subprocess.check_output([sys.executable, str(ROOT / "tools/skill.py")], text=True).strip())
DEBUG = ROOT / "tools/debug"
LONG = {"intro": 14000, "credits": 13000}  # frames; everything else is ready well inside 9000
SAVES = {"church_saved"}  # scenes that write SRAM


def scene_names(text):
    body = text[text.index("SCENE_LIST = {") + len("SCENE_LIST = {"):]
    body = re.sub(r"--[^\n]*", "", body)
    body = re.sub(r'"[^"]*"', "", body)
    prev = None
    while prev != body:  # drop nested tables and calls, leaving the top-level `name = ...` pairs
        prev, body = body, re.sub(r"\{[^{}]*\}|\([^()]*\)", "", body)
    return re.findall(r"(\w+)\s*=", body)


def run(rom, name, out, states):
    d = out / name
    state = states / f"{name}.mss"
    cmd = [sys.executable, "-X", "utf8", str(SKILL / "scripts/emu.py"), rom, "--out", str(d),
           "--script", str(DEBUG / "scenes.lua"), "--script", str(DEBUG / "warp.lua"),
           "--var", f"SCENE='{name}'", "--var", "WARP_STOP=1", "--var", f"WARP_STATE=[[{state}]]",
           "--frames", str(LONG.get(name, 9000))]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    ok = p.returncode == 0 and "warp: ready" in log and "check FAIL" not in log
    why = "" if ok else (f"exit {p.returncode}" if p.returncode else "not ready" if "warp: ready" not in log
                         else "map check FAIL")
    return name, ok, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=str(ROOT / "rom/Dual Orb - Seirei Tama Densetsu (Japan).sfc"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "work/qa/warp_all"), help="shots and logs (other builds: elsewhere)")
    ap.add_argument("--states", default=str(ROOT / "work/states"), help="savestates (default: the original-ROM set)")
    ap.add_argument("scenes", nargs="*")
    a = ap.parse_args()
    names = scene_names((DEBUG / "scenes.lua").read_text(encoding="utf-8"))
    assert len(names) == len(set(names)) and "home" in names and "place73" in names, names
    names = a.scenes or names
    out, states = Path(a.out).resolve(), Path(a.states).resolve()  # Mesen doesn't run in the repo dir
    states.mkdir(parents=True, exist_ok=True)
    # a record saved after a warp garbles the file select of every later boot: save scenes run last, then the
    # ROM's battery file (Mesen keeps it per ROM name) is deleted
    srm = ROOT / "tools/mesen/Saves" / (Path(a.rom).stem + ".srm")
    srm.unlink(missing_ok=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda n: run(a.rom, n, out, states), [n for n in names if n not in SAVES]))
    results += [run(a.rom, n, out, states) for n in names if n in SAVES]
    srm.unlink(missing_ok=True)
    for name, ok, why in results:
        print(f"{'ok  ' if ok else 'FAIL'} {name} {why}")
    shots = [str(out / n / "warp.png") for n, ok, _ in results if (out / n / "warp.png").exists()]
    if shots:
        subprocess.run([sys.executable, str(SKILL / "scripts/sheet.py"), *shots, "--cols", "10", "--max", "500", "--out", str(out / "sheet.png")],
                       cwd=ROOT)
    bad = sum(not ok for _, ok, _ in results)
    print(f"{len(results) - bad}/{len(results)} scenes ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
