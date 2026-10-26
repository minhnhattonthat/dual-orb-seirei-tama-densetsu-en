# Translation reviewer brief - Dual Orb: Seirei Tama Densetsu

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, honorific suffixes, glossary rows) is already
enforced by `tools/batches.py check` - judge translation quality. Return the report as your final message:
subagents cannot write files, so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/<batch>.pairs.txt`: every entry as `>> id [speaker] | JP` / `EN`, in ROM order (neighbours are
  context). Read ALL of it, in passes if large. The JP is kana only, spaces between words.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md` (spoilers marked), and
  `build/terms_<batch>.txt` (what each `{tXX:YY}` name token inserts; `{hero0..3}` = party names Ralph, Theo, Liz,
  Lumies).
- Dialogue English is written per page (`{fe}` between pages) and wrapped to the box at build time, so missing JP
  `{n}` breaks are correct. `{tEC:xx}` tokens may be dropped and written out (EC holds fragments as well as names).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means. Kana-only text is easy to misread: check homophones against context.
- Consistency: glossary names/terms exactly (a one-letter slip like "Bran" for "Plan" is what players notice);
  honorifics kept (D1); voice matches the style reference; item families keep their pattern.
- Grammar around name tokens: it must read right with the inserted name (see the terms file), no a/an before a
  token, no suffix glued on.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable
  ("1th"); abbreviated names or terms; stock phrases that read awkwardly ("... GET!"); spoilers given away early.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
