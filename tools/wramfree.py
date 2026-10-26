"""wramfree.py: union of tools/lua/wramuse.lua runs -> the WRAM pages no run wrote.

    python tools/wramfree.py work/qa/wram_*/wramuse.txt
"""
import sys

used = {}
for path in sys.argv[1:]:
    for line in open(path):
        a, s = line.split()
        used[a] = [x or c == "#" for x, c in zip(used.get(a, [False] * 16), s)]
for a in sorted(used):
    print(a, "".join("#" if x else "." for x in used[a]))
