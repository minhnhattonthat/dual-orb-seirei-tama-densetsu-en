"""textmap.py: the text banks ($0F $11 $12 $15) as items that tile each bank exactly, and the layout that writes them.

Item kinds (docs/re/text.md, map dialogue packages):
  list  NPC list: one 16-bit pointer per NPC to its first record
  rec   record: 4 condition words, 16-bit text pointer, set-flag list, clear-flag list (each FFFF-terminated)
  str   string, through its FF
Roots: NPC lists named by map entries (+10, maps.find_lists), less FALSE_LISTS, plus EXTRA (records and strings that
only code or scripts point at). Records after an NPC's unconditional record are never shown but stay items ("dead"),
so the bank still tiles. A layout must keep each run of records together, and the item after a conditional last
record next to it: the game steps to the next 16 bytes when no record matches ($11:A334 runs into its string).
layout() writes items from a base address with every pointer recomputed; build.py lays each
bank out from $8000 and the identity test (tests/test_identity.py) asserts the ROM comes back byte-identical.

Run alone: item counts per bank and any gap or overlap (there must be none)."""
from maps import ROM, TEXT_BANKS, find_lists, npc_list, off, parse_record, string_end, w16

# 24-bit pointers find_lists takes for NPC lists but that sit in other data (overlap real items; see tiling report)
FALSE_LISTS = {
    0x129B03: "bytes at $14:91F1 (+10 of no entry); its one 'NPC' is the string $12:ECFF",
    0x11BD14: "door records at $14:8759; would split the list at $11:BCF4",
    0x159E54: "bytes at $14:8968; inside the string $15:9E4E",
}
# sites (file offsets) find_lists takes for map-entry refs to a real list but that are other data: never rewritten
FALSE_REFS = {
    0x09E69B: "$13:E69B, read by $00:8BC7 (not the map loader $0C:B40A); rewriting it crashed boss07 (phase 5)",
}
# items no NPC list reaches: (kind, addr24)
EXTRA = [
    ("rec", 0x12E11F),  # 24-bit at file 0x46FA6
    ("rec", 0x15C900),  # 24-bit at file 0x20EF1
    ("str", 0x12D000),  # 24-bit at file 0x34DDB, 0x6552E, 0x842E3, 0x86816
]


def record(d, bank, addr):
    o = off(bank, addr)
    conds = [w16(d, o + 2 * i) for i in range(4)]
    text = w16(d, o + 8)
    lists, p = [], o + 10
    for _ in range(2):
        xs = []
        while w16(d, p) != 0xFFFF:
            xs.append(w16(d, p))
            p += 2
        p += 2
        lists.append(xs)
    return {"kind": "rec", "addr": addr, "conds": conds, "text": text, "set": lists[0], "clear": lists[1]}


def size(it):
    if it["kind"] == "list":
        return 2 * len(it["ptrs"])
    if it["kind"] == "rec":
        return 10 + 2 * (len(it["set"]) + 1) + 2 * (len(it["clear"]) + 1)
    return len(it["data"])


def scan(d):
    """{bank: [items sorted by addr]} and the 24-bit map-entry refs {file offset: addr24} to NPC lists."""
    lists = {k: v for k, v in find_lists(d).items() if k not in FALSE_LISTS}
    items = {}  # addr24 -> item

    def add_str(bank, a):
        k = bank << 16 | a
        if k not in items:
            e = string_end(d, bank, a)
            items[k] = {"kind": "str", "addr": a, "data": bytes(d[off(bank, a):e])}

    firsts = set()
    for k in lists:
        bank, a = k >> 16, k & 0xFFFF
        ptrs = npc_list(d, bank, a)
        items[k] = {"kind": "list", "addr": a, "ptrs": ptrs}
        firsts |= {bank << 16 | p for p in ptrs}
    firsts |= {a for kind, a in EXTRA if kind == "rec"}
    for kind, a in EXTRA:
        if kind == "str":
            add_str(a >> 16, a & 0xFFFF)
    # pass 1: live chains (to the first unconditional record); pass 2: dead tails up to the next known item
    for live in (True, False):
        for k in sorted(firsts):
            bank, p = k >> 16, k & 0xFFFF
            while True:
                if (bank << 16 | p) in items and items[bank << 16 | p]["kind"] != "rec":
                    break
                if parse_record(d, bank, p) is None:
                    break
                r = items.setdefault(bank << 16 | p, record(d, bank, p))
                add_str(bank, r["text"])
                p += size(r)
                if live and not any(r["conds"]):
                    break
                nxt = bank << 16 | p
                if nxt in firsts or (nxt in items and items[nxt]["kind"] != "rec"):
                    break
    banks = {b: sorted((it for k, it in items.items() if k >> 16 == b), key=lambda it: it["addr"]) for b in TEXT_BANKS}
    refs = {i: k for k, offs in lists.items() for i in offs if i not in FALSE_REFS}
    return banks, refs


def tiling(bank_items):
    """[(addr, gap)]: gap > 0 bytes no item covers, < 0 overlap. Empty when the items tile the bank."""
    out, end = [], None
    for it in bank_items:
        if end is not None and it["addr"] != end:
            out.append((end, it["addr"] - end))
        end = max(end or 0, it["addr"] + size(it))
    return out


def layout(bank_items, base, where=None):
    """Bytes for bank_items placed from base in order. where(old_addr) -> new addr for pointers to items outside
    this set (default: unchanged). Returns (bytes, {old addr: new addr})."""
    new, a = {}, base
    for it in bank_items:
        new[it["addr"]] = a
        a += size(it)
    move = lambda p: new[p] if p in new else (where(p) if where else p)  # noqa: E731
    out = bytearray()
    for it in bank_items:
        if it["kind"] == "list":
            for p in it["ptrs"]:
                out += move(p).to_bytes(2, "little")
        elif it["kind"] == "rec":
            for w in (*it["conds"], move(it["text"]), *it["set"], 0xFFFF, *it["clear"], 0xFFFF):
                out += w.to_bytes(2, "little")
        else:
            out += it["data"]
    return bytes(out), new


if __name__ == "__main__":
    d = ROM.read_bytes()
    banks, refs = scan(d)
    print(len(refs), "map-entry refs")
    for b, its in banks.items():
        n = {k: sum(it["kind"] == k for it in its) for k in ("list", "rec", "str")}
        end = its[-1]["addr"] + size(its[-1])
        print(f"bank {b:02X}: {n} ${its[0]['addr']:04X}-${end:04X}", "gaps:",
              " ".join(f"{a:04X}{g:+d}" for a, g in tiling(its)) or "none")
