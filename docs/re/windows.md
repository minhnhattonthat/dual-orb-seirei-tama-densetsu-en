# Text windows and width budgets (width gate, phase 5)

Box geometry from `tools/lua/boxes.lua` (box `$0E03/$0E05` x/w, `$0E07/$0E09` y/h at each glyph) over 24 warp scenes
on the JP-text build; pixel checks with `tools/widthgate.py` lines put in `11:854E` (the first opening line) via
`build.py --qa`. Shots: `work/qa/wg` (192 px limit), `work/qa/wg2` (torture line).

| Variant | Geometry | Budget | Status |
|---|---|---|---|
| NPC / event dialogue | x=4 w=24, y=19 h=6 (3 lines) | 192 px per line, 3 lines per page | measured: a 192 px line shows whole; the page ▼ goes in the next cell (x=224), still inside the band, so the last line also gets 192 px |
| Battle message, top | x=4 w=24, y=2 h=2 (1 line) | 192 px, 1 line | geometry; battle text is in place (byte limit) until relocated |
| Battle / game-over window, bottom | x=4 w=24, y=20 or 22 h=6 | 192 px, 3 lines | geometry |
| Names in dialogue (`{heroN}`, `{tXX:YY}`) | inline | count against the line's 192 px; budget the longest English name in the glossary | marker build subtracts the drawn name (`insert.name_px`) |
| Menus, shops, status, config, save, credits | w=32 (absolute `{pos}` placement) | a field's budget = x of the next thing on its row minus its x | in place (byte limit) now; measure per field from shots when system text relocates (phase 7) |

## Measured fields (phase 7; `tools/fieldfit.py`, run by `tools/check.py`)
| Field | Built by | Budget |
|---|---|---|
| Item/equipment info line (shops, menus) | `$0200` = `{tXX:n}:{dict:n,sub}` (`tools/lua/textdump.lua`); name table -> description sub-table pairs in `fieldfit.PAIRS` | 232 px (x=14..246, shop shot) |
| Battle panel row `$16` | `$20:A44A`: `JSL $00A8BF` at columns 8 (hero), `$0F` (command), `$17` (name) | hero 46 px, command 40 px, name 88 px after `asm/names.asm` moves the name to column `$14` (underlines are graphics: text may cross the gap) |
| Battle panel row `$19` | description at column 8; count/cost at column `$19` (`$20:A57C/A5D0`) | 136 px for items/spells/skills, 184 px for weapons |
| Config | `{pos}` + cell spaces; the cursor brackets sit at the JP option cells | option words within the JP cell count (`Remember` -> `Keep`) |
| Battle messages with `00` | copied 64 bytes to `$0200`, names written at fixed byte offsets (`$0201`, `$0202`, `$0205`, `$020A`) | slots at the JP offsets (lint error otherwise) |

The battle panel blanks its row and redraws every 3 frames; the VWF now remembers each cell's last pair
(`!MEMO`/`!OWNER` in `$7F:8900-$8E6B`) so a redrawn cell reuses it instead of churning the pool.

Torture line (all printable glyphs, double spaces): every glyph renders, widths look right (`work/qa/wg2`).
No auto-wrap: the engine moves only by codes, so a line over 192 px runs on into the next tilemap row.
English dialogue is authored per page and wrapped at build time by `tools/wrap.py` (192 px, 3 lines, extra pages
if needed). Party names count as `wrap.HERO_PX` = 42 px (default names are 20-36 px); phase 7 must cap the
name-entry screen so a typed name stays within it. Table names count at their English width.
