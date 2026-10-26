# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (recon) done 2026-10-27; next is phase 2 (debug tool). No build yet.
- **Done:**
  - Step 0: MesenCE 2.2.1 in `tools/mesen/`, guard hook verified (blocks `sed -i`), pre-commit runs `tools/check.py`
    (a failing test was rejected), `rom.sha1` pinned, original ROM smoke-boots, Start/Lua probes work.
  - Phase 1: encoding + glyph table + all control codes (`tbl/jp.tbl`, `docs/re/text.md`); map dialogue package
    format and 379 packages found (`tools/maps.py`); 226 code text-pointer sites listed; font source (compressed,
    `$0D:BCA5`); free space; graphics survey (`docs/re/graphics.md`). No prior fan translation exists.
- **Next (phase 2, debug tool):** `tools/debug/warp.lua` + `scenes.lua`. Leads: map entry pointer `$1CA1` (bank $13/$14
  entries), flags at `$7FCF83+n` (byte per flag, `$10:86D8`), party names `$0E3B+$40n`. Find the map-load trigger
  (warp data -> `$1CA1`), story flags, battle start, menu open (X/Y did nothing during the opening cutscene).
  Use warps to confirm graphics.md rows G6-G12 (battle, menus, shop, name entry, world map, ending, game over).
  Game boot: intro crawl ~11000 frames unskippable after New Game (title -> Start -> はじめから).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right.
