# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done 2026-10-27; next is phase 3 (identity build). No build yet.
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
- **Next (phase 3, identity build):** unpack then repack with no edits, byte-identical as a test
  (`references/pipeline.md` §Identity). Sources: map packages (`tools/maps.py`), code text sites (`docs/re/text.md`).
- **Debug-tool limits:** scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped; set with
  `flags = {n}` once known). Final boss can't be won (1 damage even at STATS=255); ending reached by steps 41/42.
  Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it.
