# Visual-QA reviewer brief - Dual Orb: Seirei Tama Densetsu (SNES)

You review contact sheets from the English build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's sheets: `work/qa/tour_jp/<same id>.png` (page numbers can differ: text lengths differ, so
  match by content, not by tile), and `glossary.md`.

The tour warps from a cold boot to each scene (`tools/debug/scenes.lua`) and shoots every 30 frames; a sheet keeps
only frames that changed. Each scene starts with the title, file select and a short black load.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 ~/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png`
  (scratch = your agent's temp dir, never the repo) and read that.
- When something looks wrong, open the same scene's sheet in `tour_jp/`. If the original shows the same thing,
  it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (kana/kanji in text, menus, buttons);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out (the game prints letter by letter: "Ah", "Toda", "I wi" are frames mid-typing), a box
  mid-fade or mid-scroll, a cursor caught mid-blink;
- a page that ends mid-sentence without a `▼` while the text is still typing; the next frame continues it;
- a map or scene still loading after a warp, black frames, the field before a menu opens;
- the sign glyphs in the nursery/school room (a fictional script, not Japanese);
- `0/G` in the treasure-box game (the original's);
- sound-test titles in brackets;
- a party member or monster sprite overlapping a box (the original does it too);
- anything identical in the original's sheet.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
