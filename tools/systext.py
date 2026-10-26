"""systext.py: text that code reaches outside the dialogue banks (menus, shops, battle, intro, credits, names).

BLOCKS lists every such range found (docs/re/text.md, Other text sites). A block of kind
  text   splits into pieces, each ending after FF or FA (FA ends a battle/credits message; in menu strings the
         routine reads on past it, so pieces of one block stay together and in order)
  pairs  battle status messages: each entry is two 16-bit pointers (party / enemy wording) and then the pieces they
         point at; code loads the words by absolute address (LDA $D939 / $D93B ...)
  fixed  fixed-size fields (default hero names: 8 bytes, FF-padded, copied to WRAM $0E3B + $40n)
  grid   one raw item (name-entry character grid: glyph codes in screen order)
refs() finds the known pointers to each piece: B3 immediates (LDA #lo / STA $B3 + bank), pointer tables (TABLES),
the status words, MVN copy sources (LDX #lo / LDY #dst / LDA #len / MVN) and LDA abs,X loads.

Run alone: pieces per block, refs per kind, and pointer targets that fall outside every piece start."""
import re

from maps import ROM, off, w16

ARGC = {0x3C: 2, 0xE4: 1, 0xE5: 1, 0xE6: 1, 0xE7: 1, 0xE8: 1, 0xE9: 1, 0xEA: 1, 0xEB: 1, 0xEC: 1, 0xED: 1,
        0xEE: 2, 0xEF: 2, 0xF2: 1, 0xF3: 1, 0xF4: 2, 0xF6: 1, 0xF8: 1, 0xF9: 1, 0xFC: 1}

BLOCKS = [  # (start, end exclusive, kind, note); 24-bit CPU addresses
    (0x00AA97, 0x00AAA1, "text", "yes/no choice (F0 copies it with LDA $AA97,X; cursor at cells 1 and 5)"),
    (0x00FCAE, 0x00FD46, "text", "SRAM clear warning"),
    (0x01A56A, 0x01A5DD, "text", "shop: list"),
    (0x01B375, 0x01B44E, "text", "shop: buy"),
    (0x01BF60, 0x01BFD7, "text", "shop: sell"),
    (0x01F252, 0x01F746, "text", "credits, play record, thank-you"),
    (0x0CD6CD, 0x0CD9E4, "text", "intro crawl"),
    (0x0CDCE9, 0x0CE508, "text", "story so far (continue)"),
    (0x0CE6E5, 0x0CE916, "text", "sound test"),
    (0x0CFBD6, 0x0CFDAF, "text", "treasure-box game"),
    (0x10A15C, 0x10A1A5, "text", "treasure chest messages (MVN-copied to WRAM)"),
    (0x209364, 0x209612, "text", "battle: start, results, level up"),
    (0x20A5DB, 0x20A5E5, "text", "battle: item count"),
    (0x20A5FD, 0x20A60F, "text", "battle: TP/MP cost"),
    (0x20A645, 0x20A675, "text", "battle: commands"),
    (0x20BC9D, 0x20BD7A, "text", "battle: item/MP/TP, status turns"),
    (0x20D763, 0x20D939, "text", "battle: actions"),
    (0x20D939, 0x20DAC9, "pairs", "battle: status effects"),
    (0x20FC6C, 0x20FD5F, "text", "church"),
    (0x20FFE0, 0x20FFE4, "text", "battle: empty command names (free-space FFs)"),
    (0x219D4C, 0x219DBC, "text", "field menu"),
    (0x21B36F, 0x21B3D6, "text", "menu: magic"),
    (0x21C04F, 0x21C0BF, "text", "menu: items"),
    (0x21C56D, 0x21C575, "text", "menu: party names"),
    (0x21CEEC, 0x21CFB8, "text", "menu: equip"),
    (0x21DB41, 0x21DD39, "text", "menu: status"),
    (0x21E215, 0x21E2AD, "text", "menu: config"),
    (0x21ECC4, 0x21ECD5, "text", "menu: rename"),
    (0x21ECD5, 0x21ED9D, "grid", "name entry characters"),
    (0x21EF9B, 0x21EFBB, "fixed", "default hero names"),
    (0x21F723, 0x21F7B1, "text", "save menu"),
]
FIXED = 8
# pointer tables: (table address, entry size, bank (None: 3rd byte of the entry), entries)
TABLES = [(0x01AF2E, 4, None, 4), (0x01F204, 2, 0x01, 6), (0x0CD696, 2, 0x0C, 4), (0x0CDCC5, 2, 0x0C, 18),
          (0x0CE5FA, 2, 0x0C, 31), (0x20A5F5, 2, 0x20, 4), (0x20A61F, 2, 0x20, 8), (0x20A63D, 2, 0x20, 8),
          (0x21C6FC, 2, 0x21, 5), (0x21D46B, 4, None, 4)]


def a24(o):
    return (o // 0x8000) << 16 | 0x8000 | o % 0x8000


def piece_end(d, o):
    while d[o] not in (0xFF, 0xFA):
        o += 1 + ARGC.get(d[o], 0)
    return o + 1


def pieces(d):
    """[{id, addr, data, kind, block}] in ROM order; data of each block's pieces concatenates to the block."""
    out = []

    def add(o, e, kind, note):
        a = a24(o)
        out.append({"id": f"{a >> 16:02X}:{a & 0xFFFF:04X}", "addr": a, "data": bytes(d[o:e]), "kind": kind,
                    "block": note})

    for s, e, kind, note in BLOCKS:
        o, end = off(s >> 16, s), off(e >> 16, e)
        if kind in ("grid", "fixed"):
            n = FIXED if kind == "fixed" else end - o
            for p in range(o, end, n):
                add(p, p + n, kind, note)
            continue
        while o < end:
            if kind == "pairs":  # two pointer words, then the pieces they name
                add(o, o + 4, "data", note)
                last = max(w16(d, o), w16(d, o + 2))
                o += 4
                while a24(o) & 0xFFFF <= last:
                    q = piece_end(d, o)
                    add(o, q, "text", note)
                    o = q
            else:
                q = piece_end(d, o)
                add(o, q, kind, note)
                o = q
        assert o == end, f"block {s:06X} ends at {a24(o):06X}, not {e:06X}"
    return out


def refs(d):
    """{addr24: [ref]}: ref = 'kind FILEOFF', FILEOFF = where the pointer's low byte is."""
    out = {}

    def add(a, ref):
        out.setdefault(a, []).append(ref)

    for m in re.finditer(rb"\xA9(..)\x85\xB3(?:\xA9(.)\x00|\xE2\x20\xA9(.)|\xA9(.))\x85\xB5", d, re.S):
        bank = next(g for g in m.groups()[1:] if g is not None)[0]
        add(bank << 16 | w16(m.group(1), 0), f"b3 {m.start() + 1:06X}")
    for t, size, bank, n in TABLES:
        o = off(t >> 16, t)
        for i in range(n):
            p = o + i * size
            add((d[p + 2] if bank is None else bank) << 16 | w16(d, p), f"tab {p:06X}")
    for p in pieces(d):
        if p["kind"] == "data":  # status entry words (code loads them by absolute address)
            o = off(p["addr"] >> 16, p["addr"])
            for k in (0, 2):
                add(p["addr"] & 0xFF0000 | w16(d, o + k), f"word {o + k:06X}")
    for m in re.finditer(rb"\xA2(..)\xA0..\xA9..\x54", d, re.S):  # LDX #src / LDY #dst / LDA #len-1 / MVN
        a = (m.start() // 0x8000) << 16 | w16(m.group(1), 0)
        if any(s <= a < e for s, e, _, _ in BLOCKS):  # the pattern copies much else; keep copies of text only
            add(a, f"mvn {m.start() + 1:06X}")
    for m in re.finditer(rb"\xBD(..)\x9D\x3B\x0E", d, re.S):  # default names: LDA abs,X / STA $0E3B,X
        bank = m.start() // 0x8000
        for k in range(4):
            add(bank << 16 | w16(m.group(1), 0) + FIXED * k, f"absx {m.start() + 1 + 6 * k:06X}")
    return out


if __name__ == "__main__":
    d = ROM.read_bytes()
    ps = pieces(d)
    starts = {p["addr"] for p in ps}
    rs = refs(d)
    for s, e, kind, note in BLOCKS:
        n = [p for p in ps if p["block"] == note]
        print(f"{s:06X}-{e:06X} {kind:5} {len(n):3} pieces, {sum(p['addr'] in rs for p in n):3} with refs  {note}")
    out = {a: r for a, r in rs.items() if a not in starts and a & 0xFFFF >= 0x8000 and a >> 16 < 0x7E}
    print(len(out), "ref targets outside piece starts:")
    for a, r in sorted(out.items()):
        print(f"  {a:06X} {' '.join(r)}")
