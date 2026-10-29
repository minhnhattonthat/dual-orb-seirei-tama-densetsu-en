# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done 2026-10-27: v1.0 published.
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
    2026-10-27 (3): field menu info panels (`asm/menus.asm`, `docs/re/windows.md` §Field menu machinery). Items:
    prompt box + panel merged into one x8 w240 window, icon frame col $0F, name col $13 (88 px), description own
    row col 2 (224 px), prompts col 2 ("Use it on whom?" padding 1 cell, 21:C098 blank 12 cells; lint
    `batches.MOVED` allows the C04F `{pos}` move). Magic: panel x112 w136, description col $0F (120 px). Equip uses
    the 232 px info line (ok). `fieldfit.FIELD` budgets. Scenes: menu_item_list/_long/_long2, menu_magic_list/_long
    (Theo alive + all spells by poke), menu_equip_info. Probes `tools/lua/{tilestr,windows,nbufidx}.lua`.
    Fixed (pre-existing since the 256-byte buffer): `church_saved` map check FAIL. The save line's `ED 00` (record
    after a warp) reads a garbage pointer, the bank-$3F copy ran ~4.5 KB and `$7F:EF00+X` wrapped into bank $80 =
    direct page. Buffer writers now drop index >= $100 (`asm/names.asm`). `warp_all.py` runs SRAM-writing scenes
    last and deletes the build's .srm (a mid-run save garbled the file select of the later scenes).
    2026-10-27 (4): magic panel slot 3 ok (`menu_magic_slot3`; `$111F` = party size-1). Town picker (Telepiam /
    "Go to which town?", `asm/menus.asm`): 3x2 grid of 72 px overlapped -> 2x2 of 104 px (towns <= 81 px), verified
    scroll and the pick lands where the original's same index does (`menu_magic_town/_town2`, `telepiam_go`).
    Visited towns: byte per town `$7FD01C+n`. Fixed "Use it on whom?" (21:B393) padding that erased the spell icon
    frame; its clear string 21:B39E now 12 cells (`menu_magic_whom/_whom_back`). Probe `tools/lua/calls.lua`
    (log reaches of any ADDR). `warp_all.py` 131/131 ok.
    2026-10-27 (5): battle lists ok (scene `battle_party`: Theo + every item; panel = down, A on a member, commands
    cycle with right; magic/item grids show name/description/MP or count fine; targeting has no text). Intro crawl
    fixed (`asm/crawl.asm`, `docs/re/text.md` §Intro crawl): pages printed whole overflowed the VWF pool (183-260
    cells vs 182); now a line at a time as it nears the screen, rows above the window blanked. VWF fix: bottom-half
    cells record `!OWNER` (a top cell's memo stole a shown pair). `build.py` now fails on any change outside
    `insert.allowed()` (romdiff; hook list moved to `asm.HOOKS`). Probes `tools/lua/{regwrites,hdma,crawllog}.lua`.
    EN savestates for play sessions: `warp_all.py --rom build/dual_orb_en.sfc --states work/states/en`.
  - Phase 8 (in progress, 2026-10-27 (6)): tour = `warp_all.py --tour` (shot every 30 frames until ready, per-scene
    `sheet*.png`): EN `--rom build/dual_orb_en.sfc --out work/qa/tour --states work/states/en`, JP `--out
    work/qa/tour_jp`; delete the top-level `sheet*.png` overview before `qa_gate.py init work/qa/manifest.tsv
    work/qa/tour --glob "sheet*.png"`. Brief `docs/visual-qa-brief.md`; chunks 000-010 dispatched (312 sheets),
    verdicts in `work/qa/verdicts/`. Battle buttons (G6) now
    ATTACK/AUTO/FLEE (`asm/buttons.asm`, `tools/buttons.py`, `gfx/buttons.txt`). Story-so-far reachable: scenes
    `story00-17` (warp `story = n`: new game takes the load path `$21:EE80` -> `$0C:DB4F`, piece forced at
    `$0C:DBE1`); all 18 fit (checked by eye), not yet in the manifest.
    2026-10-27 (7): visual-QA issues 1-8 fixed. VWF upload also on idle NMIs (`vwf_idle`, hook `$00:85E8`: menus
    ready a game frame only every ~5 NMIs; menus/shops now clean at fade-in; also fixed shop_buy "+80" junk; probe
    `tools/lua/nmiprof.lua`). Place-name label = window record `$10:84C3` w80 -> 136. Compass screen
    (`asm/compass.asm`): stored tilemap `$2A:C03C` copied into the BG3 buffer bottom half, labels printed in English
    (North .. Northwest). Field menu window/text/left bracket 8 px left (right bracket fixed x `$F2`, `$21:94CE`).
    Money "./G": narrow `.` shared the `/` cell. "Aleitos's House". Intro f900 glitch not reproduced frame by frame
    (f300-1000) on the new build. asar math is left to right: bracket offsets (`!X+(2*$40)`).
    2026-10-27 (8): full EN re-tour 150/150, 350 sheets, `qa_gate.py check` exit 0 (verdicts `r2_chunk_000-011`,
    `r3_story`, `r3_controller`). Fixed: story08/12 pages over the VWF pool (197/192 cells; a later cell stole a
    line's first word); story08/12/13 text trimmed, gate in `tools/fieldfit.py` (<= 180 cells). All 18 pages
    checked fully typed (`warp.lua --var "STORY_HOLD=true"`, `--frames 2600`). church_saved slot garbage after the
    save = the known save-after-warp limit (JP garbles too), marked ok, not checked with a real save.
    2026-10-27 (9): graphics sweep done: only tile-drawn text is G6 (battle buttons), English in zoomed cold-boot
    shots `battle`, `boss00` (ATTACK blinks = selected-button flash); no chapter cards; game over has none (G12);
    credits/intro are text (verdicts r2). `bash tools/debug/shot.sh battle boss00 credits intro worldmap`.
    2026-10-27 (10): polish pass applied (`docs/polish.md`, skips noted there: width/lint limits). Info-line colon
    space: code $60 "：" (colon + word space, 7 px) written by `$01:A002/AEA5/BC6B` (shops etc.) and the equip
    template `$21:CFB8` (MVN to `$028C`); found with regwrites on `$7E028C` (bank-$00 range misses long writes).
    2026-10-27 (11): real church save/load in play (no warp) passes: Nakush church save, power cycle, file select
    clean, load back in church (`work/playtest/church-save/record1.srm` = a clean save by the priest). Fixed: yes/no
    `{f0}` (291 entries) lost the JP `{n}` before it, so the choice joined the question line and its fixed-cell cursor
    (cells 1, 5) erased glyphs; `wrap.py` now gives `{f0}` its own line (checked in play, `work/playtest/yn`).
    Warps home/ending_lab/final_boss/gameover reach their targets at 2600 frames (tour cut them short).
    2026-10-27 (12): playtest leftovers: slots "File n", church menu "Save Game / Revive Allies", Panje unquoted.
    Full EN re-tour, round r4 (verdicts `r4_chunk_000-010`, `r5_main`), `qa_gate.py check` exit 0. Fixed: shop
    Clothes description touched the box edge (shortened). Tour is not deterministic run to run (fades, blinking
    cursor/ATTACK flash change pixels), so a re-tour marks ~90% of sheets changed: re-review is the rule anyway.
  - Phase 9: `tools/release.py` (build, check, smoke, jp_left on the dialogue banks with `tools/jp_known.txt`,
    qa gate, checksum, BPS re-applied, zip; README template `docs/README.release.txt`). v1.0 published 2026-10-27
    on github.com/minhnhattonthat/dual-orb-seirei-tama-densetsu-en (user's request).
  - Issue #1 (2026-10-29, player report, 7 bugs; screenshots/videos/saves in `work/issues/1/`, Supafaust states not
    loadable in Mesen): (1) Custom controller screen kana junk -> `asm/controller.asm` (scene `controller`);
    (2) field menu left column 24 on screen after closing: the 5-item print `$21:9299` and the close clear `$21:93F7`
    still used column 25 (+ clear now 6 cells; scene `menu_close`); (3) shop greetings ran off the box: 15 EC
    phrases > 192 px shortened, `lint.py` now measures kept-JP dialogue lines; EC:87/88 got their leading space
    ("Antidote Herbis yours"); (4) party sprites vanishing during the overflowing shop text: not reproduced (talking
    to an NPC after a warp does nothing; `tools/debug/talk.sh` reaches the shop rooms), likely the overflow;
    (5) "- AUTO BATTLE -" 93 px from col 21 past the 10-cell clear -> "AUTO BATTLE" (fieldfit `PIECES`; scene
    `battle_auto`); (6) map corruption after battles: NMI upload raced the game's main-thread DMA-queue flush
    (`gdma_on/off`, `docs/re/vwf.md`); (7) flicker: idle-NMI uploads of half-redrawn cells (`!DRAWN` gate).
    Probes `tools/lua/{cellwrites,vramaddr,dmarace}.lua`. Release script default `--version 1.1`.
  - v1.1 QA (2026-10-30): re-tour r6 (153 scenes, 357 sheets) found the issue #1 `!DRAWN` gate starved idle uploads:
    shops and item/magic/equip menus showed stale pool glyphs for seconds (item list never recovered). Fixed in two
    steps (`asm/vwf.asm`, `docs/re/vwf.md` §Half cells): hold only the pairs still being drawn, send runs up to the
    held pair, walk past held ring entries, never hold a pair not yet sent (`!SENT`). Battle panel checked frame by
    frame (flicker stays fixed; `--shot-every 1` check in vwf.md). r7 re-tour left a 1-2 dim-frame stale tail at a
    shop fade-in (bandwidth limit, now a standing non-bug in the brief) and the whom_back window-close animation
    (game's own, JP too). Probe `tools/lua/vwfstate.lua`.
    r8 re-tour 153/153, 357 sheets, all 11 chunks ok (verdicts `r8_*`), `qa_gate.py check` exit 0.
  - v1.1 release built 2026-10-30: `tools/release.py --version 1.1` passes (build, check, smoke, jp_left 0 runs,
    gate, BPS re-applied). `release/DualOrb_EN_v1.1.zip` (bps + README), patch sha1 88e1898e..., result crc32
    282A56CC, playable `build/dual_orb_en_v1.1.sfc` sha1 f72b9158.... Not published (needs the user).
- **Next:** publishing v1.1 is the user's call (`gh release create` only with their say-so; close issue #1 then).
  Then player bug reports. Not checked: one-frame "Re:ord 3" flash after saving (now "File"), the one-frame
  "branc?es" redraw in menu_item_long2 (final frame clean).
- **Risks:** other `find_lists` refs may be false like `$13:E69B` (only those read by the map loader `$0C:B40A` are
  proven; probe: `work/tmp_refs.lua` idea, log reads of each ref site). Shadow `$7E:E000` is free in the scenes
  measured, not proven everywhere. A full screen of new VWF cells takes a few frames to appear; text finished just
  before a fade-in can show its last cell or two stale for 1-2 dim frames (`docs/re/vwf.md` §Limit).
  `$7F:8F00-$8FB5` (`!SENT`) assumed free like the rest of `$7F:8900-$8FFF` (measured in 9 scenes).
- **Debug-tool limits:** a record saved after a warp (`church_saved`, SRAM `tools/mesen/Saves/<rom>.srm`) garbles
  the file select when loaded, on the original ROM too (`tools/routes/load1.txt`): story-so-far not reachable yet;
  delete that .srm after such a run (`warp_all.py` does). Scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped). Final boss
  can't be won; ending reached by steps 41/42. Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Non-blocking: sound-test titles are already English in fullwidth brackets;
  default plan is to keep their wording and only restyle.)
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it. Battle text ends at FA, not FF.
