"""batches.py: translation batches for agents (skill references/translation.md).

    python tools/batches.py split dialogue|names|system   -> work/tl/bNNN.tsv + build/terms_bNNN.txt for entries
                                                          with an empty en, numbered after the last existing batch
    python tools/batches.py check bNNN                    -> validates work/tl/bNNN.out.tsv; prints OK or the errors
    python tools/batches.py merge bNNN [...]              -> check, then write en into script/*.json
    python tools/batches.py pairs bNNN                    -> work/tl/bNNN.pairs.txt for the reviewer
Input TSV: id, speaker, form, limit, jp ({n} shown as " / "). Output: id<TAB>en, same ids in the same order."""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import wrap  # noqa: E402

TL = ROOT / "work" / "tl"
BUILD = ROOT / "build"
MAX_CHARS, MAX_ENTRIES = 3500, 150
TOK = re.compile(r"\{[^}]*\}|\[[0-9A-F]{2}\]")
FREE = {"{n}", "{fe}"}  # presentation codes the English may use more or fewer of (dialogue and system)
KATA = r"ァ-ヶー―"
HONORIFIC = re.compile(rf"(?:[{KATA}]+|\{{hero\d\}}|\{{t[0-9A-F]{{2}}:[0-9A-F]{{2}}\}})(さん|さま|様|くん|ちゃん|どの)")
SUFFIX = {"さん": "-san", "さま": "-sama", "様": "-sama", "くん": "-kun", "ちゃん": "-chan", "どの": "-dono"}
NAMES_KIND = {"E4": "heal spell", "F2": "attack spell", "E5": "key item", "E6": "weapon", "E7": "body armor",
              "E8": "shield/arm", "E9": "helmet", "EA": "shoes", "EB": "sword skill", "F3": "fighting skill",
              "EC": "person/term", "ED": "place", "F9": "monster", "3C0": "desc: key item", "3C1": "desc: heal spell",
              "3C2": "desc: attack spell", "3C3": "desc: sword skill", "3C4": "desc: fighting skill",
              "3C5": "desc: weapon", "3C6": "desc: shield", "3C7": "desc: helmet", "3C8": "desc: armor",
              "3C9": "desc: shoes"}


def files(kind):
    return sorted((ROOT / "script").glob("dialogue_*.json")) if kind == "dialogue" else [ROOT / "script" / f"{kind}.json"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, rows):
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def glyphs(jp):
    return TOK.sub("", jp)


def glossary():
    """[(jp, en, avoid list)] from every table in glossary.md with a JP | EN header."""
    rows, cols = [], None
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            cols = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[:2] == ["JP", "EN"]:
            cols = cells
        elif cols and not set(cells[0]) <= {"-", ":"} and cells[0] and cells[1]:
            r = dict(zip(cols, cells))
            avoid = [a.strip() for a in r.get("Avoid", "").split(",") if a.strip()]
            rows.append((r["JP"], r["EN"], avoid))
    return rows


def has_term(jp, term):
    """Whole-run match: a katakana/kanji term must not be part of a longer run of the same script."""
    for m in re.finditer(re.escape(term), jp):
        a, b = jp[m.start() - 1:m.start()], jp[m.end():m.end() + 1]
        if not (re.fullmatch(f"[{KATA}]", a) or re.fullmatch(f"[{KATA}]", b)):
            return True
    return False


def enforced(term):
    return re.search(rf"[{KATA}一-鿿]", term) is not None


def row_of(e, kind):
    jp = e["jp"].replace("{n}", " / ")
    if kind == "dialogue":
        return [e["id"], "-", "dlg", f"{wrap.BOX_PX}px x{wrap.LINES} per page", jp]
    if kind == "names":
        return [e["id"], NAMES_KIND.get(e["id"].split(":")[0], "-"), "name", f"~{8 * len(glyphs(e['jp']))}px", jp]
    lim = max(len(glyphs(x)) for x in e["jp"].split("{n}"))
    return [e["id"], e.get("block", "-")[:60].replace("\t", " "), "menu", f"~{8 * lim}px/line", jp]


def tokens_meaning(jp_all):
    """Lines '{tXX:YY} = JP -> EN' for each name token used in the batch."""
    names = {e["id"]: e for e in load(ROOT / "script" / "names.json")}
    out = []
    for t in sorted(set(re.findall(r"\{t([0-9A-F]{2}):([0-9A-F]{2})\}", jp_all))):
        e = names.get(f"{t[0]}:{t[1]}")
        if e:
            out.append(f"{{t{t[0]}:{t[1]}}} = {e['jp'].replace('{end}', '')} -> {e['en'].replace('{end}', '') or '?'}")
    return out


_names = {}


def expand(text, lang):
    """Name tokens replaced by their names.json text (glossary check), other control codes dropped."""
    if not _names:
        _names.update({e["id"]: e for e in load(ROOT / "script" / "names.json")})

    def sub(m):
        e = _names.get(f"{m[1]}:{m[2]}")
        return e[lang].replace("{end}", "") if e else ""
    return TOK.sub("", re.sub(r"\{t([0-9A-F]{2}):([0-9A-F]{2})\}", sub, text))


def split(kind):
    TL.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    done = {re.sub(r"\D", "", p.name.split(".")[0]) for p in TL.glob("b*.tsv")}
    n = max(map(int, done), default=0)
    queued = {line.split("\t")[0] for p in TL.glob("b[0-9][0-9][0-9].tsv")
              for line in p.read_text(encoding="utf-8").splitlines()}
    gl = glossary()
    batches, cur, chars, seen = [], [], 0, set()
    for path in files(kind):
        for e in load(path):
            if e["en"] or not glyphs(e["jp"]).strip() or e["id"] in queued or e.get("kind") == "grid":
                continue
            if kind == "dialogue":  # identical strings are translated once; merge copies the en to the rest
                if e["jp"] in seen:
                    continue
                seen.add(e["jp"])
            c = len(glyphs(e["jp"]))
            if cur and (chars + c > MAX_CHARS or len(cur) >= MAX_ENTRIES):
                batches.append(cur)
                cur, chars = [], 0
            cur.append(row_of(e, kind))
            chars += c
    if cur:
        batches.append(cur)
    for rows in batches:
        n += 1
        name = f"b{n:03d}"
        tsv = TL / f"{name}.tsv"
        assert not tsv.exists(), tsv
        tsv.write_text("".join("\t".join(r) + "\n" for r in rows), encoding="utf-8", newline="\n")
        jp_all = "".join(r[4] for r in rows)
        terms = [f"{jp} -> {en}" + (f"  (avoid: {', '.join(av)})" if av else "") for jp, en, av in gl if jp in jp_all]
        (BUILD / f"terms_{name}.txt").write_text("\n".join(
            ["# glossary rows whose JP occurs in this batch"] + terms
            + ["", "# name tokens: the game inserts this text; keep the token (a {tEC} fragment may be written out instead)"]
            + tokens_meaning(jp_all)) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(rows)} entries, {sum(len(glyphs(r[4])) for r in rows)} JP chars ({kind})")


def entries():
    out = {}
    for kind in ("dialogue", "names", "system"):
        for path in files(kind):
            for e in load(path):
                out[e["id"]] = (kind, path, e)
    return out


def read_out(name):
    out = []
    for line in (TL / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip():
            k, _, v = line.partition("\t")
            out.append((k.strip(), v))
    return out


def check(name, verbose=True):
    rows = [line.split("\t") for line in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()]
    ids = [r[0] for r in rows]
    errs, warns = [], []
    try:
        out = read_out(name)
    except FileNotFoundError:
        out = []
        errs.append(f"{name}.out.tsv missing")
    got = [k for k, _ in out]
    if got != ids:
        miss, extra = set(ids) - set(got), set(got) - set(ids)
        dup = [k for k, c in collections.Counter(got).items() if c > 1]
        errs.append(f"id set/order differs: missing {sorted(miss)[:8]} extra {sorted(extra)[:8]} dup {dup[:8]}"
                    + ("" if miss or extra or dup else " (order)"))
    db, gl = entries(), glossary()
    for k, en in out:
        if k in db:
            e_, w_ = entry(db[k][0], db[k][2], en, gl)
            errs += e_
            warns += w_
    if verbose:
        for x in warns:
            print("WARN", x)
        for x in errs:
            print("ERROR", x)
        print("OK" if not errs else f"{len(errs)} errors")
    return not errs, out


JP = wrap.Table.load(ROOT / "tbl" / "jp.tbl")


def holes(b):
    """Byte offsets of the '00' name slots battle/chest code overwrites (insert.far keeps them in place)."""
    return [i for i in range(len(b) - 1) if b[i] == 0 and b[i + 1] == 0 and (i == 0 or b[i - 1] != 0)]


def entry(kind, e, en, gl):
    """-> (errors, warnings) for one entry's English (also tools/lint.py over the whole script)."""
    k, jp, errs, warns = e["id"], e["jp"], [], []
    if not en.strip():
        return [f"{k}: empty"], warns
    if re.search(r"[^\x20-\x7e▲▼▶・]", en) or "\\u" in en:  # static marks: original tiles (shop scroll arrows)
        return [f"{k}: non-ASCII or \\u escape"], warns
    try:
        wrap.EN.encode(en)
    except ValueError as x:
        return [f"{k}: {x}"], warns
    free = FREE if kind != "names" else set()
    a = collections.Counter(t for t in TOK.findall(jp) if t not in free)
    b = collections.Counter(t for t in TOK.findall(en) if t not in free)
    # EC is half name table, half phrase dictionary (fragments like ドラゴン・ラーゼ): its tokens may be written out
    for t in list(a):
        if t.startswith("{tEC:") and b[t] <= a[t]:
            a[t] = b[t]
    if +a != +b:
        errs.append(f"{k}: control codes differ: missing {sorted((a - b).elements())} extra {sorted((b - a).elements())}")
    if e.get("block", "").startswith(("battle", "treasure chest")):  # code writes names over "00" by byte offset
        if holes(JP.encode(jp)) != holes(wrap.EN.encode(en)):
            errs.append(f"{k}: '00' name slots must sit at the JP byte offsets {holes(JP.encode(jp))}")
    if TOK.findall(jp) and not en.endswith(TOK.findall(jp)[-1]):
        errs.append(f"{k}: must end with {TOK.findall(jp)[-1]}")
    if re.search(r"\{(t[0-9A-F]{2}:[0-9A-F]{2}|hero\d)\}(s|st|nd|rd|th|es)\b", en):
        errs.append(f"{k}: suffix glued to a name token")
    if re.search(r"\b(a|an|A|An)\s+\{(t[0-9A-F]{2}:[0-9A-F]{2}|hero\d)\}", en):
        errs.append(f"{k}: a/an before a name token")
    for m in HONORIFIC.finditer(jp):
        who = m[0][:-len(m[1])]
        # only party names and glossary names: おうさま (king) or ゴキブリちゃん are not name + honorific
        if (who.startswith("{hero") or who in {r[0] for r in gl}) and SUFFIX[m[1]] not in en:
            errs.append(f"{k}: honorific {m[1]} needs {SUFFIX[m[1]]} (D1)")
    jx, ex = expand(jp, "jp"), expand(en, "en")
    for term, ten, avoid in gl:
        if enforced(term) and has_term(jx, term) and ten.lower() not in ex.lower():
            errs.append(f"{k}: glossary {term} -> {ten}")
        for av in avoid:
            if re.search(rf"\b{re.escape(av)}\b", en):
                errs.append(f"{k}: avoided spelling {av!r} (glossary: {ten})")
    if kind == "dialogue":
        errs += [f"{k}: {x}" for x in wrap.wrap(en)[1]]
        if en.count("{fe}") > jp.count("{fe}") + 1 + jp.count("{fe}") // 2:
            warns.append(f"{k}: {en.count('{fe}')} pages vs JP {jp.count('{fe}')} (fine if needed)")
    else:
        lim = 8 * max(len(glyphs(x)) for x in jp.split("{n}"))
        px = max(wrap.width(x) for x in re.sub(r"\{(end|fa)\}", "", en).split("{n}"))
        if px > lim:
            warns.append(f"{k}: {px}px over the original {lim}px (soft until phase 7)")
    return errs, warns


def merge(names):
    todo = {}
    for name in names:
        ok, out = check(name, verbose=False)
        if not ok:
            check(name)
            sys.exit(f"{name}: not merged")
        todo.update(out)
    db = entries()
    same = {db[k][2]["jp"]: en for k, en in todo.items() if db[k][0] == "dialogue"}
    for path in {db[k][1] for k in todo} | set(files("dialogue") if same else []):
        rows = load(path)
        n = 0
        for e in rows:
            if e["id"] in todo:
                e["en"] = todo[e["id"]]
                n += 1
            elif "dialogue" in path.name and e["jp"] in same:  # copies follow their (re-merged) original
                e["en"] = same[e["jp"]]
                n += 1
        save(path, rows)
        print(f"{path.name}: {n} entries")


def pairs(name):
    rows = [line.split("\t") for line in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()]
    out = dict(read_out(name))
    ids = [r[0] for r in rows]
    db = entries()
    # entries are in ROM order (one map's NPCs together), so neighbours are the context
    lines = [f"# {name}: every >> entry is to review. Pages split by {{fe}}; {{n}} = line break; the English is"
             " wrapped to the box by tools/wrap.py at build time."]
    for i, k in enumerate(ids):
        lines.append(f">> {k} [{rows[i][1]}] | {db[k][2]['jp']}\n   EN | {db[k][2]['en'] or out.get(k, '')}")
    lines.append("")
    (TL / f"{name}.pairs.txt").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(TL / f"{name}.pairs.txt")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "split":
        split(args[0])
    elif cmd == "check":
        sys.exit(0 if check(args[0])[0] else 1)
    elif cmd == "merge":
        merge(args)
    elif cmd == "pairs":
        for a in args:
            pairs(a)
