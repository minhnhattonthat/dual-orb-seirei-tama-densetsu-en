"""lint.py: the batch checks (tools/batches.py entry) over every translated entry in script/*.json.
tools/check.py runs it, so the pre-commit hook gates on it. Exit 1 on any error; warnings are only counted."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches  # noqa: E402

gl = batches.glossary()
errs, warns, n = [], 0, 0
for kind, _, e in batches.entries().values():
    if not e["en"] and kind == "dialogue":  # kept JP bytes (token-only shop lines): no wrap, so each line must fit (#1)
        errs += [f"{e['id']}: {px} px > {batches.wrap.BOX_PX}: {line}" for p in batches.wrap.pages(e["jp"])
                 for line in p if (px := batches.wrap.width(line)) > batches.wrap.BOX_PX]
    if e["en"]:
        n += 1
        er, w = batches.entry(kind, e, e["en"], gl)
        errs += er
        warns += len(w)
for x in errs:
    print("ERROR", x)
print(f"lint: {n} entries, {len(errs)} errors, {warns} warnings")
sys.exit(1 if errs else 0)
