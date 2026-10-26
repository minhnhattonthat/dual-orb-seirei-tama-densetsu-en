# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done 2026-10-27; next is phase 4 (extract). `tools/build.py` builds
  `build/dual_orb_en.sfc`, byte-identical to the original (sha1 25fe4c1a...), smoke ok.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/`, guard hook verified (blocks `sed -i`), pre-commit runs `tools/check.py`
    (a failing test was rejected), `rom.sha1` pinned, original ROM smoke-boots, Start/Lua probes work.
  - Phase 1: encoding + glyph table + all control codes (`tbl/jp.tbl`, `docs/re/text.md`); map dialogue package
    format and 379 packages found (`tools/maps.py`); 226 code text-pointer sites listed; font source (compressed,
    `$0D:BCA5`); free space; graphics survey (`docs/re/graphics.md`). No prior fan translation exists.
  - Phase 2: `tools/debug/warp.lua` + `scenes.lua` (111 scenes: opening, field menu screens, 8 shop/inn/save
    modes, battle, 17 bosses, final boss, epilogue, credits, one per place name) from a cold boot, intro skipped.
    `tools/debug/warp_all.py` = 111/111 ok, shots in `work/qa/warp_all/`, states `work/states/<scene>.mss`.
    `tools/debug/doors.py` walks the door graph. Addresses: `docs/re/debug.md`. graphics.md G6-G12 filled in:
    no name entry, no game-over screen; battle command buttons look like graphic tiles.
  - Phase 3: `tools/textmap.py` tiles the 4 text banks into 376 NPC lists / 2257 records / 2257 strings (no gaps);
    `tools/build.py` re-lays them out and rewrites map-entry pointers -> identical (`tests/test_identity.py`, also a
    reversed-layout test and the tbl roundtrip of every bank string). Reversed layout shows the same opening text
    in the emulator. Details: `docs/re/text.md` §Item model.
- **Next (phase 4, extract):** dump `script/*.json` (one file per text bank, id = `BB:AAAA`, `jp`, `en`, plus a
  `dead` flag for records past an unconditional one) from `textmap.scan`; add the other text: bank $00 name tables
  (control codes E4-F9 tables), code-pointer strings (226 `$B3` sites, banks $01 $0C $20 $21 $24), credits, intro.
  Roundtrip + coverage tests. Plan for insertion: relocate packages to banks $30-$3F (header already says 2 MB),
  rewrite map entry +10; confirm the `EXTRA` 24-bit sites are real code/data pointers first.
- **Debug-tool limits:** scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped; set with
  `flags = {n}` once known). Final boss can't be won (1 damage even at STATS=255); ending reached by steps 41/42.
  Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it.
