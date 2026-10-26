"""maps.py: find every map dialogue package (NPC list -> condition records -> strings). docs/re/text.md.

Map entries (bank $13, variable length) hold a 24-bit pointer at +10 to the package's NPC list: one 16-bit pointer
per NPC to its first record. A record is 4 condition words (2 flags that must be clear, 2 that must be set; 0 = none,
>= 1000 = item check), a 16-bit text pointer (same bank), then two FFFF-terminated flag lists (set, clear). The game
walks an NPC's records in order and shows the first whose conditions hold ($10:86B7, $0C:BADF).

Run alone: prints a summary (packages, records, strings) per bank."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Dual Orb - Seirei Tama Densetsu (Japan).sfc"
TEXT_BANKS = (0x0F, 0x11, 0x12, 0x15)
# argument bytes after each control code (tbl/jp.tbl)
ARGC = {0xE4: 1, 0xE5: 1, 0xE6: 1, 0xE7: 1, 0xE8: 1, 0xE9: 1, 0xEA: 1, 0xEB: 1, 0xEC: 1, 0xED: 1, 0xEE: 2, 0xEF: 2,
        0xF2: 1, 0xF3: 1, 0xF4: 2, 0xF6: 1, 0xF8: 1, 0xF9: 1, 0xFC: 1}


def off(bank, addr):
    return (bank & 0x7F) * 0x8000 + (addr & 0x7FFF)


def w16(d, o):
    return d[o] | d[o + 1] << 8


def parse_record(d, bank, addr):
    """Return (text_ptr, length, conds) or None if the bytes don't form a record."""
    o = off(bank, addr)
    if addr < 0x8000 or o + 14 > len(d):
        return None
    conds = [w16(d, o + 2 * i) for i in range(4)]
    if any(c == 0xFFFF for c in conds):
        return None
    ptr = w16(d, o + 8)
    if ptr < 0x8000:
        return None
    p = o + 10
    for _ in range(2):
        n = 0
        while w16(d, p) != 0xFFFF:
            p += 2
            n += 1
            if n > 16:
                return None
        p += 2
    return ptr, p - o, conds


def string_end(d, bank, addr, limit=2048):
    """Offset just past the FF that ends the string at addr (args of control codes skipped), or None."""
    o = off(bank, addr)
    end = o + limit
    while o < end:
        b = d[o]
        if b == 0xFF:
            return o + 1
        if b == 0x3C:
            o += 3
        elif b >= 0xE0:
            o += 1 + ARGC.get(b, 0)
        else:
            o += 1
    return None


def find_lists(d):
    """24-bit pointers in bank $13 that point at an NPC list in a text bank. Returns {list_addr24: [entry offsets]}."""
    found = {}
    for i in range(off(0x13, 0x8000), off(0x14, 0xFFFF) - 1):  # map entries live in banks $13-$14
        bank = d[i + 2]
        addr = w16(d, i)
        if bank not in TEXT_BANKS or addr < 0x8000:
            continue
        recs = npc_list(d, bank, addr)
        if recs:
            found.setdefault(bank << 16 | addr, []).append(i)
    return found


def npc_list(d, bank, addr):
    """Record start addresses of the NPC list at bank:addr, or None if it isn't one."""
    o = off(bank, addr)
    ptrs = []
    first = 0x10000
    a = addr
    while a < first and len(ptrs) < 64:
        p = w16(d, off(bank, a))
        if p < 0x8000 or parse_record(d, bank, p) is None:
            break
        ptrs.append(p)
        first = min(first, p)
        a += 2
    if not ptrs or a != first and first != 0x10000 and a < first:
        pass
    return ptrs or None


def chains(d, bank, addr, stops):
    """All records reachable from the NPC list: each NPC's records run on until an unconditional record or a stop."""
    out = []
    for p in npc_list(d, bank, addr):
        while True:
            r = parse_record(d, bank, p)
            if r is None:
                break
            out.append((p, r))
            p += r[1]
            if not any(r[2]) or p in stops:
                break
    return out


if __name__ == "__main__":
    import sys
    d = ROM.read_bytes()
    lists = find_lists(d)
    print(len(lists), "candidate NPC lists")
    stops = {k & 0xFFFF for k in lists}
    texts = set()
    for k in sorted(lists):
        for p, r in chains(d, k >> 16, k & 0xFFFF, stops | {x for x in range(0)}):
            texts.add((k >> 16, r[0]))
    print(len(texts), "strings referenced by records")
    # census strings in text banks that no record reaches
    cen = [l.split() for l in open(ROOT / "work" / "census.txt", encoding="utf-8") if l[:1] != "b"]
    miss = [c for c in cen if int(c[1][:2], 16) in TEXT_BANKS and (int(c[1][:2], 16), int(c[1][3:], 16)) not in texts]
    print(len(miss), "census strings in text banks not reached")
    for c in miss[:int(sys.argv[1]) if len(sys.argv) > 1 else 30]:
        print(" ".join(c)[:120])
