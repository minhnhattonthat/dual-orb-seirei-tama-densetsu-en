"""doors.py: walk the door graph from the new-game map and list every map entry with a spawn point.

Map entry (banks $13/$14, docs/re/debug.md): +0 place-name index (bit 7 = no name banner), +10 NPC list (24-bit),
+23 door list (24-bit). Door record, 8 bytes: x, y, size?, destination map (24-bit), dest x, dest y byte
((dir << 6) | y tile); FFFF ends the list.

  python -X utf8 tools/debug/doors.py          # one line per map: ptr, place, spawn, how many doors lead in
  python -X utf8 tools/debug/doors.py --lua    # same as Lua table rows for scenes.lua
  python -X utf8 tools/debug/doors.py --places # one Lua row per place name: its map with the most doors in"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from maps import ROM, find_lists, off, w16  # noqa: E402
from tbl import Table  # noqa: E402

START = 0x13A3FF  # new-game map ($21:F041)
PLACES = 0x00C438  # place-name pointer table (control code ED)


def r24(d, o):
    return d[o] | d[o + 1] << 8 | d[o + 2] << 16


def is_entry(p):
    return p >> 16 in (0x13, 0x14) and p & 0xFFFF >= 0x8000


def doors(d, entry):
    """[(x, y, size, dest, dx, dy)] from the entry's door list."""
    lst = r24(d, off(entry >> 16, entry) + 23)
    if not is_entry(lst):
        return []
    o, out = off(lst >> 16, lst), []
    while w16(d, o) != 0xFFFF and len(out) < 64:
        dest = r24(d, o + 3)
        out.append((d[o], d[o + 1], d[o + 2], dest, d[o + 6], d[o + 7]))
        o += 8
    return out


def place(d, t, idx):
    if idx == 0:
        return ""
    p = w16(d, off(0, PLACES) + 2 * (idx - 1))
    return t.decode(d, off(0, p), 32)[0].split("{end}")[0]


def entries(d):
    """Every map entry: those whose +10 points at an NPC list (maps.py), plus door destinations."""
    out = set()
    for offs in find_lists(d).values():
        for i in offs:
            e = i - 10
            out.add((e // 0x8000) << 16 | 0x8000 | e % 0x8000)
    return out


def walk(d):
    """{entry: [(src, x, y)]}: every map entry, with the door spawns that lead into it (START gets the new-game
    spawn). Sources are all known entries, not only those reachable from START: towns join through the world map."""
    seen = {START: [(None, 0x1A, 0x05)]}
    q = deque(sorted(entries(d) | {START}))
    done = set()
    while q:
        m = q.popleft()
        if m in done:
            continue
        done.add(m)
        seen.setdefault(m, [])
        for x, y, size, dest, dx, dy in doors(d, m):
            if not is_entry(dest):
                continue
            seen.setdefault(dest, []).append((m, dx, dy))
            q.append(dest)
    return seen


def selftest():
    d = ROM.read_bytes()
    # school room -> village outside Aleitos' house, the door verified in the emulator (docs/re/debug.md)
    assert doors(d, 0x13A3FF) == [(0x18, 0x0E, 0x01, 0x13A3E4, 0x0B, 0x46)], doors(d, 0x13A3FF)
    assert len(walk(d)) > 50


if __name__ == "__main__":
    d = ROM.read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    seen = walk(d)
    if "--places" in sys.argv:
        best = {}
        for m in sorted(seen):
            idx = d[off(m >> 16, m)] & 0x7F
            if seen[m] and idx and (idx not in best or len(seen[m]) > len(seen[best[idx]])):
                best[idx] = m
        for idx, m in sorted(best.items()):
            src, x, y = seen[m][0]
            print(f"  place{idx:02d} = {{ map = 0x{m:06X}, x = 0x{x:02X}, y = 0x{y:02X} }},  -- {place(d, t, idx)}")
        sys.exit()
    lua = "--lua" in sys.argv
    for m in sorted(seen):
        idx = d[off(m >> 16, m)] & 0x7F
        if not seen[m]:
            if not lua:
                print(f"{m:06X} place {idx:2d} {place(d, t, idx):<16} no door leads in")
            continue
        src, x, y = seen[m][0]
        name = place(d, t, idx)
        if lua:
            print(f"  m{m:06X} = {{ map = 0x{m:06X}, x = 0x{x:02X}, y = 0x{y:02X} }},  -- {idx} {name}")
        else:
            print(f"{m:06X} place {idx:2d} {name:<16} spawn {x:02X},{y:02X} in {len(seen[m])}")
    if not lua:
        print(len(seen), "maps reachable by doors")
