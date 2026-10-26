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

Torture line (all printable glyphs, double spaces): every glyph renders, widths look right (`work/qa/wg2`).
No auto-wrap: the engine moves only by codes, so a line over 192 px runs on into the next tilemap row.
