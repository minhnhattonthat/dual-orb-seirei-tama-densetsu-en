# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | encoding, glyph table, control codes, map dialogue packages, text sites, ranges, free space | verified (encoding, codes, records, text sites by `tests/test_extract.py`); refs of 28 battle/menu pieces unknown |
| graphics.md | graphics-text survey | rows confirmed with warp shots; "font" rows not yet traced to strings |
| vwf.md | VWF engine: pool tiles, NMI upload ring, vblank findings | verified in game (marker tour 111/111, `tools/vwfcheck.py`) |
| windows.md | text box geometry and width budgets (width gate) | dialogue measured in px; menus by geometry, per-field shots pending |
| debug.md | boot, field, door, script, cutscene-step and battle addresses the warp uses | verified unless marked guess |

Prior work: no earlier fan translation of this game found (searched 2026-10-27; only Dual Orb II has English patches).
Helpers: `tools/peek.py` (decode at offset; `--split` one string per line), `tools/extract.py` (script JSON),
`tools/names.py` / `tools/systext.py` (name tables / system text model), `tools/census.py` (text-like runs), `tools/maps.py` (packages),
`tools/fontsheet.py` (code -> glyph sheet), `tools/lua/textlog.lua` (engine string log).
