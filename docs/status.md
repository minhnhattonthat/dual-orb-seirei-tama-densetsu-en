# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit) in progress 2026-10-27: relocation done, menus partly fitted.
  `tools/build.py` builds VWF + script (`--marker` for the marker build, `--identity` for the byte-identical ROM).
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/`, guard hook verified (blocks `sed -i`), pre-commit runs `tools/check.py`
    (a failing test was rejected), `rom.sha1` pinned, original ROM smoke-boots, Start/Lua probes work.
  - Phase 1: encoding + glyph table + all control codes (`tbl/jp.tbl`, `docs/re/text.md`); map dialogue package
    format and 379 packages found (`tools/maps.py`); font source (compressed, `$0D:BCA5`); free space; graphics
    survey (`docs/re/graphics.md`). No prior fan translation exists.
  - Phase 2: `tools/debug/warp.lua` + `scenes.lua` (111 scenes) from a cold boot; `tools/debug/warp_all.py` = 111/111
    ok, states `work/states/<scene>.mss`. Addresses: `docs/re/debug.md`.
  - Phase 3: `tools/textmap.py` item model of the 4 dialogue banks; `tools/build.py` re-lays them out ->
    byte-identical (`tests/test_identity.py`, plus a reversed-layout test).
  - Phase 4: `tools/extract.py` -> `script/dialogue_{0F,11,12,15}.json` (2257), `script/names.json` (773, bank $00
    tables E4-F9 + dict 3C0-3C9, `tools/names.py`), `script/system.json` (288 pieces in 30 blocks: shops, credits,
    intro, story-so-far, sound test, battle, menus, save, default names, name-entry chart; `tools/systext.py`).
    `tests/test_extract.py`: jp roundtrip to ROM bytes, names tile `$00:B422-$D753`, every `$B3`/table pointer
    target is a piece start, every census run in a text-pointer bank is covered, re-extract keeps `en`.
    Notes: `docs/re/text.md` §Other text sites, §Script files.
  - Phase 5: VWF (`asm/vwf.asm`, asar 1.91; font `fonts/vwf.txt` -> `tools/font.py`; `tbl/en.tbl`): glyphs drawn
    into the old glyph tiles (182 pairs) via a hook at `$00:AEB6`, uploaded by an NMI hook at `$00:80A9` in small
    vblank-checked chunks (`docs/re/vwf.md`). Insertion `tools/insert.py`: dialogue re-laid with overflow into
    banks $31-$3F; names/system text in place (byte limit). Marker build: 111/111 warp scenes ok, pool cells
    VRAM == shadow on menus/shops (`tools/vwfcheck.py`). Width gate `docs/re/windows.md`: dialogue 192 px x 3 lines
    measured, torture line ok (`tools/widthgate.py`). False map ref `$13:E69B` (`textmap.FALSE_REFS`) crashed boss07.
  - Phase 6: every entry translated (dialogue 2257 incl. 645 exact repeats copied on merge, names 773, system 289;
    28 batches b001-b028 in `work/tl/`, gitignored). Pipeline `tools/batches.py` (split/check/merge/pairs), wrap at
    build `tools/wrap.py` (192 px x 3, extra pages auto, party names budgeted 42 px), whole-script gate
    `tools/lint.py` in `check.py` (3055 entries, 0 errors). Every batch reviewed (reviewer agents); Critical/Important
    fixed; Minors in `docs/polish.md`. Glossary, `docs/synopsis.md`, `docs/style-reference.md`, briefs written.
    `{tEC}` tokens may be written out (EC = names + phrase fragments). In-game: English dialogue renders (opening).
  - Phase 7 (in progress): names in bank $3F via patched table handlers, insert buffer 256 B at `$7F:EF00`,
    `{jump}` (DF) far text in bank $3E for every over-long system piece (`asm/names.asm`, `docs/re/text.md`
    §Names relocated). 0 entries left Japanese. Battle `00` name slots kept at JP byte offsets (lint error).
    VWF per-cell pair memo (battle panel churn). Battle name field at column $14. `tools/fieldfit.py` (in check):
    info line 232 px, battle fields. 111/111 warps ok; checked shop, menus, status, rename, battle, battle_win,
    intro, credits, places. Debug probes: `tools/lua/{jumplog,textdump,bblog}.lua`.
    Name entry (rename screen = sub-mode 3, scenes `rename`/`name_entry`): English chart ABC/abc/symbols, 4 rows a
    page, drawn by text over the kana tilemaps, typed names capped at 42 px (`asm/namechart.asm`,
    `tools/namechart.py`, `docs/re/text.md`). Verified typing, pages, delete, cap, end (`work/play/neen`).
    2026-10-27 (2): lint WARNs (vs JP width) are a poor proxy; checked by screen instead. OK: file select, church
    (sub-mode 7, not inn), treasure-box game (sub-mode 8, not exchange; "0/G" is the original's), save slots.
    Fixed: save confirm Yes/No under the cursor sprites (x table `$21:F28D`), "Where will you save" / "Use it on
    whom?" etc. padded with `_` so a shorter prompt hides the longer one, file-select "New Game" window+cursor
    widened (`asm/names.asm`). Story-so-far: window x16 w224, text col 3 -> ~208 px; longest line 206 (not seen
    in game). New scenes: church, church_save/confirm/confirm_no/saved/revive, treasure_game, shop_buy (9999 G),
    menu_item_full (inventory poke). RAM: money `$7E:111B` (32-bit), inventory words `$0F3B..` (lo = item id,
    hi = count?). Warp fakes the APU ack the save waits on (`$21:F7E4`); probe `tools/lua/pcsample.lua`.
- **Next (phase 7 rest):**
  - **Field item/magic/equip info panel** (top right, `menu_item_full`): name field x=168..~236 (68 px) after the
    icon, description line x=128..~236 (~108 px). Names up to 91 px ("Mystic Mushroom" 88 runs off-screen),
    descriptions up to 136 px. Engine fix: find the panel's window/column bytes (bank $21, menu code near
    `$21:C04F` text refs), widen the panel left / start the name nearer the icon; shorten the left prompts box
    if needed. Then a fieldfit budget for it. Check equip + magic panels the same way (spell list needs a
    caster with spells: poke).
  - Battle target/magic/item selection lists; intro crawl re-check. `romdiff.py` with allowed ranges. Then
  phase 8 (QA tours + visual-QA gate) and the polish pass (`docs/polish.md`). Battle command buttons
  (アタック/オートバトル/にげる) are graphics: phase 8 graphics list.
- **Risks:** other `find_lists` refs may be false like `$13:E69B` (only those read by the map loader `$0C:B40A` are
  proven; probe: `work/tmp_refs.lua` idea, log reads of each ref site). Shadow `$7E:E000` is free in the scenes
  measured, not proven everywhere. A full screen of new VWF cells takes a few frames to appear.
- **Debug-tool limits:** a record saved after a warp (`church_saved`, SRAM `tools/mesen/Saves/<rom>.srm`) garbles
  the file select when loaded, on the original ROM too (`tools/routes/load1.txt`): story-so-far not reachable yet;
  delete that .srm after such a run. Scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped). Final boss
  can't be won; ending reached by steps 41/42. Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Non-blocking: sound-test titles are already English in fullwidth brackets;
  default plan is to keep their wording and only restyle.)
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it. Battle text ends at FA, not FF.
