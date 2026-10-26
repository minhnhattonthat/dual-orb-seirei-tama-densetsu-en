# Translator brief - Dual Orb: Seirei Tama Densetsu (SNES, 1993)

You translate part of the Japanese script of Dual Orb, a classic dragon-and-orbs fantasy RPG (Dragon Quest style:
towns, NPCs, shops, a boy hero sent by a dragon to seal the source of evil), into English for a fan patch.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - voice and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch and what each name token inserts.
   Full table in `glossary.md` (read its Rulings and Style rules once).
3. `docs/synopsis.md` - plot and who is who. Don't give the marked spoilers away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. The Japanese is all kana with spaces between words (the game has no
kanji). ` / ` = line break, `{fe}` = next page (wait for a key). Entries are in ROM order: one map's NPCs together, so
neighbours are context (often the same NPC before/after an event, or a whole cutscene split into parts).
- form `dlg`: an NPC/cutscene box, 192 px x 3 lines per page (about 36 characters a line).
- form `name`: an item/spell/monster/place/person name, or (speaker `desc: ...`) a one-line description shown in a
  menu. limit = the original field width (8 px per character); a soft target for now (menus get measured later):
  keep names reasonably short (most under 12 characters) without abbreviating.
- form `menu`: system text (shops, battle messages, menus, credits, intro, story-so-far). speaker = what the block is.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, no tabs inside the
English, no Japanese or fullwidth characters, no `\uXXXX`. Characters the font lacks: `# * @ [ ] < > $ ^ | \` and
backtick; `&` and `%` exist.

### Control codes
Copy every `{...}` code from the Japanese, in the same place in the sentence flow, and end with the same terminator
(`{end}`, `{f0}`, `{f1}`, `{fa}`). Meanings: `{f0}` shows a Yes/No choice; `{f1}` ends and re-runs the NPC's script;
`{sync}` waits on a sound; `{pos:XXYY}`, `{right}`, `{down}` etc. place the cursor (system text: keep them).
- **Dialogue line breaks:** write each page as running text. The build wraps it to the box (`tools/wrap.py`), so
  don't copy the JP `{n}` breaks; use `{n}` only for a deliberate break (a list, a poem, a pause). Use `{fe}` between
  pages; you may add or drop `{fe}`. A page holds 3 wrapped lines; past that the wrapper starts a new page at an
  arbitrary word, so split long pages yourself where the pause reads well.
  Dry run: `python -X utf8 tools/wrap.py "text"` prints the wrapped lines with their widths.
- **Name tokens** `{hero0}`-`{hero3}` (party names, default Ralph, Theo, Liz, Lumies; the player can rename them),
  `{tED:xx}` (place), `{tE5:xx}` (item) and others insert a name: keep them, write grammar around them
  (`{hero0}-san`, `{hero0}'s`), never a/an before them, never a suffix glued on (`{tE5:05}s` is wrong).
- **`{tEC:xx}` tokens** are special: the EC table is half names, half text fragments (`ドラゴン・ラーゼ` + `ス`,
  `し、 パンジェを`, shop phrases). The terms file shows what each inserts. Keep a `{tEC:xx}` that inserts a whole
  name or phrase; when it inserts a fragment, drop it and write the English out in full. Dropping is allowed, adding
  one is not.
- System text with fixed layouts (`{pos}`, padded columns, menus): keep the layout codes; the check allows more or
  fewer `{n}`.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every ERROR until it prints OK.
WARN lines are information (e.g. a name wider than the original field): fine, but prefer the shorter of two equally
good wordings.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Use names and terms exactly as in the glossary. Never abbreviate to fit. If something can't be said well within a
  name's soft limit, keep the meaning and report it as `LONG: id`.
- Honorifics kept, Western name order (D1): `{hero0}さん` -> `{hero0}-san`, `さま` -> `-sama`, `くん` -> `-kun`,
  `ちゃん` -> `-chan`, `どの` -> `-dono` when attached to a name or name token. Not on common nouns (おかあさん = Mom).
- Punctuation: 「」 -> "...", ・・・ -> `...`, ！？ -> `!?`, `ー`/`~` stretched words -> repeated letters
  (`ウゥ~~~` -> `Uuuugh...`).
- `{hero0}たち` = "{hero0} and the others", "{hero0}'s party", or "you" in direct address.
- Kana-only Japanese is ambiguous: read the neighbours before deciding what a homophone means.
- Item and spell names in a family keep the family pattern (e.g. tiers: base, -a, -ia, -am, -iam).

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Notes from earlier batches
- Never "a"/"an" before a token, never a plural or suffix on one (`a {tE5:0C}`, `{tE5:0C}s`): the check fails both.
  Use "the {tE5:0C}", rephrase, or write a common noun out ("looms").
- Read what the token inserts before building grammar on it: `{tEC:10}` = "Six Generals" (a group: "one of the
  {tEC:10}", never "a fine {tEC:10}"); `{tEC:4B}` = singular "Knight of Joshua" (for the knights as a group drop it and
  write "the knights of Joshua"); `{tEC:37}` = "King of Joshua" (no -sama: おうさま is just "king").
- One-line EC phrase tokens wider than a line (`{tEC:86}`, `{tEC:5E}`) can't wrap: write them out.
- Dish brothers: `{tEC:13}・{tEC:14}` -> "{tEC:13} and {tEC:14}".
- No a/an or gendered "sir" for おきゃくさま (party includes women): "customer", or rephrase.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
