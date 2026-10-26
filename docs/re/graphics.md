# Graphics text survey

Every Japanese element drawn as tiles rather than through the text engine. Status: what is known after phase 1
(boot, title, file select, intro, first room). Rows marked "check" get confirmed with a zoomed cold-boot warp shot
once the debug tool (phase 2) reaches the screen.

| # | Screen | Element | Kind | Japanese? | Plan |
|---|---|---|---|---|---|
| G1 | Boot | `I'MAX PRESENTS` | sprites/BG | no, English | none |
| G2 | Title | `DUAL ORB` logo, `(c)1993 I'MAX` | BG graphic | no, English; subtitle 聖霊珠伝説 not shown | none |
| G3 | File select | `はじめから`, `きろく1-4` | font (text engine) | yes | text, not graphics (find strings) |
| G4 | Nursery / school sign | 6 glyphs + 5 small marks | map tileset | no: a fictional script, not kana/kanji | leave |
| G5 | Dialogue box | frame, `▼` page arrow | font codes 2F/30 | no | none |
| G6 | Battle | command window, status | check | check | check |
| G7 | Field menu, status, equip, magic | labels, stats | check (bank $20/$21 strings suggest text) | check | check |
| G8 | Shop / inn | labels | text (bank $01 strings) | check | check |
| G9 | Name entry (if any) | kana grid | check | check | check |
| G10 | World map | place names | check | check | check |
| G11 | Ending, credits | credits are text (bank $00) | text | a few JP nicknames | translate as text |
| G12 | Game over | check | check | check | check |

Font: `docs/re/text.md` (compressed at `$0D:BCA5`); English needs lowercase glyphs, so the font is edited in phase 5.
