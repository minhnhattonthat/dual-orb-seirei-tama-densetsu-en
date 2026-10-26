# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translation) done 2026-10-27; next is phase 7 (relocate names/system text, fit menus).
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
- **Next (phase 7):** relocate names/system text: 912 in-place entries are longer than the JP and are left Japanese
  by the build for now (`insert.LONG`; they show as tofu inside English text). Names need a far-pointer hook in the
  E4-F9 handler; chest messages MVN-copied with fixed length into `$1C19`; EC phrase tokens used in shops must stay
  within one line (192 px) or the line breaks. Measure menu field budgets from shots (system text widths: lint WARNs,
  e.g. intro crawl 0C:D8AE 205 px, story-so-far up to 210 px). Cap the name-entry screen at 42 px (`wrap.HERO_PX`).
  Name-entry chart (grid) is still Japanese. Then the polish pass (`docs/polish.md`).
- **Risks:** other `find_lists` refs may be false like `$13:E69B` (only those read by the map loader `$0C:B40A` are
  proven; probe: `work/tmp_refs.lua` idea, log reads of each ref site). Shadow `$7E:E000` is free in the scenes
  measured, not proven everywhere. A full screen of new VWF cells takes a few frames to appear.
- **Debug-tool limits:** scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped). Final boss
  can't be won; ending reached by steps 41/42. Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Non-blocking: sound-test titles are already English in fullwidth brackets;
  default plan is to keep their wording and only restyle.)
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it. Battle text ends at FA, not FF.
