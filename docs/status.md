# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done 2026-10-27; next is phase 5 (engine spike + marker build). `tools/build.py` still
  builds the identity ROM (sha1 25fe4c1a...).
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
- **Next (phase 5, engine spike + marker build):**
  - Font/VWF decision: glyphs are 8x16 fixed (one BG3 column per byte, dakuten in the glyph). English needs
    lowercase: font is compressed at `$0D:BCA5` (format not decoded; unpacked to `$7E:8000` by `$00:8AE6`).
    Options: decode/replace the compressed font, or patch the unpack to read an uncompressed English font from an
    expanded bank. Free glyph codes: kana 40-DF all become free for English letters.
  - Insertion: dialogue banks relocate to expanded banks $30-$3F (header already 2 MB), rewrite map entry +10;
    check the `EXTRA` 24-bit sites (`tools/textmap.py`) are real pointers first. Names: re-lay `$00:B422-$D753`
    (bank $00 only; overflow needs a far-pointer hook in the E4-F9 handler). System pieces: patch `refs`; the 28
    without refs stay in place, in order. Chest messages are MVN-copied with a fixed length into `$1C19`.
  - Marker build: every entry -> `[id]` marker, every box variant's width measured in-game (the width gate).
- **Debug-tool limits:** scenes are by place, not story chapter (story flags `$7FCF83+n` not mapped). Final boss
  can't be won; ending reached by steps 41/42. Battle-time HP copy not found (GOD clears the dead flags instead).
- **Open bugs:** none.
- **Waiting on the user:** nothing. (Non-blocking: sound-test titles are already English in fullwidth brackets;
  default plan is to keep their wording and only restyle.)
- **Gotchas:** `play.py` presses: `a a a --gap N`, not `"-*120"` tokens. Mesen probe addresses print with odd bank
  bytes (`00FDFA00`) for WRAM; the low 16 bits are right. Field menu is Y or B (X does nothing). Mesen runs Lua
  outside the repo dir: pass `scenes.lua` as its own `--script`, don't `dofile` it. Battle text ends at FA, not FF.
