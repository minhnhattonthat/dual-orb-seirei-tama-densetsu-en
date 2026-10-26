"""names.py: the bank $00 name and description tables (docs/re/text.md, control codes E4-F9 and 3C).

Each table is a run of 16-bit pointers (bank $00) followed by FF-terminated strings; entry n (1-based) of the code
that names it is pointer n-1. The 23 tables and their strings tile $00:B422-$D753 with no gap (tests/test_extract.py).
3C (dict) takes a sub-table number (0-9) from the pointer list at $00:AA64.

Run alone: entries per table and the tiling report."""
from maps import ROM, off, string_end, w16

# control code -> table address (bank $00)
TABLES = {"E4": 0xC0DC, "E5": 0xBF5E, "E6": 0xC2BB, "E7": 0xB422, "E8": 0xC231, "E9": 0xB577, "EA": 0xB4F5,
          "EB": 0xB5EE, "EC": 0xB651, "ED": 0xC438, "F2": 0xC189, "F3": 0xB619, "F9": 0xC720}
DICT = 0xAA64  # 10 pointers to the 3C sub-tables
REGION = (0xB422, 0xD753)


def tables(d):
    """{name: address} for every table, 3C sub-tables named 3C0-3C9."""
    out = dict(TABLES)
    for i in range(10):
        out[f"3C{i}"] = w16(d, off(0, DICT + 2 * i))
    return out


def entries(d, a):
    """Pointers of the table at a: they run until the first string."""
    ptrs, p, first = [], a, 0x10000
    while p < first:
        ptrs.append(w16(d, off(0, p)))
        first = min(first, ptrs[-1])
        p += 2
    return ptrs


def scan(d):
    """[(table name, address, [(index from 1, string address, bytes)])], sorted by address."""
    out = []
    for name, a in sorted(tables(d).items(), key=lambda kv: kv[1]):
        strs = [(i + 1, p, bytes(d[off(0, p):string_end(d, 0, p)])) for i, p in enumerate(entries(d, a))]
        out.append((name, a, strs))
    return out


def tiling(d):
    """[(addr, gap)] in REGION: gap > 0 bytes no table or string covers, < 0 overlap. Empty when it tiles."""
    spans = []
    for name, a, strs in scan(d):
        spans.append((a, a + 2 * len(strs)))
        spans += [(p, p + len(b)) for _, p, b in strs]
    spans = sorted(set(spans))
    out, end = [], REGION[0]
    for s, e in spans:
        if s != end:
            out.append((end, s - end))
        end = max(end, e)
    if end != REGION[1]:
        out.append((end, REGION[1] - end))
    return out


if __name__ == "__main__":
    d = ROM.read_bytes()
    for name, a, strs in scan(d):
        print(f"{name} ${a:04X} {len(strs)} entries")
    print("tiling:", tiling(d) or "ok")
