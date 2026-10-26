# Graphics text survey

Every Japanese element drawn as tiles rather than through the text engine. Status: what is known after phase 1
(boot, title, file select, intro, first room). G6-G12 confirmed from cold-boot warp shots in phase 2
(`tools/debug/warp_all.py`, `work/qa/warp_all/`); "font" means it looks like the dialogue font, not yet traced.

| # | Screen | Element | Kind | Japanese? | Plan |
|---|---|---|---|---|---|
| G1 | Boot | `I'MAX PRESENTS` | sprites/BG | no, English | none |
| G2 | Title | `DUAL ORB` logo, `(c)1993 I'MAX` | BG graphic | no, English; subtitle 聖霊珠伝説 not shown | none |
| G3 | File select | `はじめから`, `きろく1-4` | font (text engine) | yes | text, not graphics (find strings) |
| G4 | Nursery / school sign | 6 glyphs + 5 small marks | map tileset | no: a fictional script, not kana/kanji | leave |
| G5 | Dialogue box | frame, `▼` page arrow | font codes 2F/30 | no | none |
| G6 | Battle (warp `battle`, `boss00`) | buttons `アタック` `オートバトル` `にげる` | guess: graphic tiles (orange on striped grey, not the font) | yes | redraw as English tiles (find in VRAM, phase 5) |
| G6b | Battle | `HP` `TP` labels, digits, messages (`〜が あらわれた`, `ダメージをあたえた!!`) | messages font; HP/TP Latin | messages yes | messages as text |
| G7 | Field menu (Y/B; warp `menu*`) | `まほう` `アイテム` `そうび` `ステータス` `コンフィグ` `ほうがく`, status/equip/config labels | font (same glyphs as dialogue) | yes | text; find strings |
| G8 | Shops, inn, save (warp `shop_*`, `inn`, `save`, `exchange`) | headers, `D/G` price column, item names | font | yes | text |
| G9 | Name entry | none: new game goes title -> intro -> school room with fixed names (`warp1`, `ng4`) | - | - | none |
| G10 | World map (warp `worldmap`) | no place-name banner on the world map; towns show the font banner | font | yes (banners) | text (place-name table) |
| G11 | Ending, credits (warp `ending_lab`, `credits`) | staff roll, play record | text (bank $00) | a few JP nicknames; record labels | translate as text |
| G12 | Game over | none: a party wipe prints a battle message and respawns at home (`go1`, warp `gameover`) | - | - | none |

Font: `docs/re/text.md` (compressed at `$0D:BCA5`); English needs lowercase glyphs, so the font is edited in phase 5.
