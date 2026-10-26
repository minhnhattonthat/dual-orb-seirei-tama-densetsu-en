"""census.py [--min N] [--bank XX]: list FF-terminated runs in the original ROM that read as text.

Heuristic recon aid (not the extractor): a run is text when it decodes with tbl/jp.tbl and at least --min of its
characters are kana. Prints offset, CPU address, length and the text; a summary line per bank at the end.
runs() is also the coverage test's list of text-like bytes (tests/test_extract.py)."""
import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402


def is_kana(b):
    return 0x40 <= b <= 0xDF


def runs(d, lo, hi, min_kana=3):
    """Yield (start, end) of plausible strings in d[lo:hi], end = index of the FF."""
    start = lo
    for i in range(lo, hi):
        if d[i] == 0xFF:
            body = d[start:i]  # strings sit back to back, or after a record's FFFF list end
            kana = sum(1 for b in body if is_kana(b))
            common = sum(1 for b in body if 0x40 <= b <= 0x8F or b in (0x3F, 0xFD, 0xFE, 0x36, 0x37, 0x32, 0x28))
            if kana >= min_kana and common * 4 >= len(body) * 3 or (
                    len(body) >= 2 and all(0x90 <= b <= 0xDF or b == 0x32 for b in body)):
                yield start, i
            start = i + 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--bank")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    d = (ROOT / "rom" / "Dual Orb - Seirei Tama Densetsu (Japan).sfc").read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    per_bank = Counter()
    for bank in range(len(d) // 0x8000):
        if a.bank and int(a.bank, 16) != bank:
            continue
        for s, e in runs(d, bank * 0x8000, bank * 0x8000 + 0x8000, a.min):
            per_bank[bank] += e - s + 1
            if not a.quiet:
                text, _ = t.decode(d, s, e - s)
                print("%06X %02X:%04X %4d %s" % (s, bank, 0x8000 + s % 0x8000, e - s, text))
    print("bytes per bank:", " ".join("%02X:%d" % kv for kv in sorted(per_bank.items())), "total",
          sum(per_bank.values()))
