# Text engine, encoding, pointers

Dump: `rom.sha1` (No-Intro, LoROM, 1.5 MB = banks $00-$2F, header says 2 MB, SRAM 8 KB, SlowROM map mode $20).

## Encoding (verified)
- 1 byte per character, table `tbl/jp.tbl`. **Verified**: `tools/fontsheet.py` renders every code from the glyph table
  against the VRAM font (sheet matched by eye), and the intro string at file 0x656CD (`ここは とおい、べつの せかい。`)
  and the first dialogue at 0x8854E (`{hero0}や、{n}ゆうべは すさまじい あらしで あったのぅ。`) decode exactly.
- Glyph table: ROM `$00:B0A2` (file 0x30A2), 4 bytes per code 00-DF: top tile word, bottom tile word (BG3, 2bpp,
  chr base VRAM word $2000). Every glyph is one 8 px column x 16 px (two 8x8 tiles), fixed advance. Dakuten are
  drawn into the top tile of the character itself.
- 00-09 digits, 0A-23 A-Z (no lowercase), 24-38 punctuation, 3D/32 both `ー` (same tiles; 3D written `―`),
  3E ヴ, 3F space, 40-8F hiragana (gojuon, small kana 6E-76, voiced 77-8F), 90-DF katakana.
- Font tiles are compressed: source ROM `$0D:BCA5` (file 0x6BCA5), unpacked to `$7E:8000` by `$00:8AE6`/`$00:8AEE`
  (writes through `$2180`), then DMA 0x1E90 bytes to VRAM word $2000 at boot (frame ~26). Format not yet decoded.

## Engine (verified by disassembly + textlog.lua)
- Main interpreter `$00:A94C`: reads `[$B3],Y` (24-bit pointer at DP $B3, Y = `$0DF9`), draws via `$00:AEB6` into the
  tilemap buffer at `[$BB]` (top row, +$40 bottom row). Cursor x `$0E0B`, y `$0E0D` (in 16 px rows).
  Box origin/size: `$0E03`/`$0E07` (x/y), `$0E05`/`$0E09` (w/h). NPC dialogue box: x=4, w=$18 (24 cols), y=$13, h=6.
- `tools/lua/textlog.lua` logs each string the engine starts (frame, pointer, caller stack).

## Control codes (argument counts verified from the handlers)
| Code | Args | Meaning |
|---|---|---|
| 39 | 0 | wait on APU port $2142 (sound sync) |
| 3A | 0 | no-op |
| 3B | 0 | clear box, cursor home |
| 3C | 2 | insert string: arg2*2 indexes table `$00:AA64` (10 sub-tables), arg1 = 1-based entry |
| E0-E3 | 0 | party member name 0-3 (WRAM `$0E3B + $40*n`) |
| E4-ED, F2, F3, F9 | 1 | insert name from table (1-based index): E4 `$00:C0DC`, E5 `$00:BF5E` (items), E6 `$00:C2BB`, E7 `$00:B422`, E8 `$00:C231`, E9 `$00:B577`, EA `$00:B4F5`, EB `$00:B5EE`, EC `$00:B651` (people), ED `$00:C438` (places), F2 `$00:C189`, F3 `$00:B619`, F9 `$00:C720` |
| EE | 2 | insert string at 16-bit pointer (bank $00), leading 00 skipped |
| EF | 2 | same, drawn right-aligned (numbers) |
| F0 | 0 | yes/no choice, ends the string (copies `$00:AA97`) |
| F1 | 0 | end and re-run the NPC's record list (`$0E39`=FFFF) |
| F4 | 2 | set cursor x, y |
| F5 / F7 | 0 | cursor x -1 / +1 |
| F6 / F8 | 1 | cursor x -n / +n |
| FA | 0 | end (credits/page end) |
| FB | 0 | cursor y +1 |
| FC | 1 | cursor y +n |
| FD | 0 | newline (x=0, y+1) |
| FE | 0 | wait for key, next page |
| FF | 0 | end |
Inserted strings go through the 32-byte buffer `$0E11` (FF-terminated): a name longer than 31 bytes overflows it.

## Map dialogue packages (verified: `tools/maps.py`, read path `$0C:BAC7` -> `$10:86B7`)
- Map entries in banks $13-$14 (variable length). Entry +10..+12 = 24-bit pointer to the map's **NPC list**.
  Loaded by `$0C:B3AE` into `$1C07/$1C09`; entry pointer comes from `$1CA1` (warp data).
- NPC list: one 16-bit pointer per NPC (same bank) to its first **record**.
- Record: `forbid1 forbid2 need1 need2` (flag words, 0 = none, >= 1000 = item/other check `$10:872D`), `text` (16-bit,
  same bank), then a set-flag list and a clear-flag list, each FFFF-terminated. The game shows the first record whose
  conditions hold; `F1` at the end of a text re-evaluates the list.
- Layout per package: records, strings, NPC list (order varies; bank $11 starts with a package whose list is at $8000).
- `tools/maps.py`: 379 packages, 2216 strings reached by records; 31 strings in the text banks reached otherwise
  (shops, inns, event scripts; to resolve in the extractor).

## Item model and identity build (verified: `tests/test_identity.py`)
- `tools/textmap.py` splits each text bank into NPC lists, records and strings that tile it with no gap or overlap:
  $0F:8000-E532, $11:8000-F7AE, $12:8000-F22F, $15:8000-FC89 (2257 records, 2257 strings, 376 lists).
- Roots: 381 map-entry refs (+10) from `find_lists`, less 3 false hits (`FALSE_LISTS`), plus `EXTRA`: records
  $12:E11F, $15:C900 and string $12:D000, reached by 24-bit pointers outside map entries (sites in the source;
  not yet confirmed as code, check before relocating).
- The game walks an NPC's records until one matches; no terminator. Records after an unconditional one are dead but
  kept as items. Quirk: `$11:A334` (list $11:A332) is conditional and last, so on a miss the game reads its string as
  a record: a layout keeps runs of records, and the item after a conditional last record, together.
- `tools/build.py` lays every bank out again from the model and rewrites the map-entry pointers: byte-identical.
  The same banks laid out back to front (`test_reversed_layout_shows_same_text`) show the same text in the
  emulator (`opening` warp, `work/qa/rev_rev` vs `rev_orig`).

## Other text sites (verified: `tests/test_extract.py`)
- **Name tables** (`tools/names.py`): 13 code tables (E4-F9) + 10 `{dict}` sub-tables (pointer list `$00:AA64`), each
  16-bit pointers then FF strings; together they tile `$00:B422-$D753` exactly (773 strings). EC is a general
  name/phrase table (170 entries), 3C0-3C9 hold item/magic/equipment descriptions.
- **System text** (`tools/systext.py`, 30 blocks, 288 pieces): shops ($01), credits + play record ($01:F252, not
  bank $00), SRAM warning ($00:FCAE), intro crawl, story-so-far, sound test, treasure-box game ($0C), chest messages
  ($10:A15C, copied to WRAM by `LDX #src / LDY #$1C19 / MVN`), battle ($20), menus, config, rename, save ($21).
  Pointer forms found: `LDA #lo / STA $B3 / LDA #bank / STA $B5` (every target in the ROM is a piece start),
  10 pointer tables (`TABLES`), status-message word pairs at `$20:D939` (party/enemy wording, `LDA $D939`/`$D93B`),
  MVN sources, `LDA $EF9B,X` (default names). 28 pieces have no known pointer (battle messages picked by index or
  reached by stepping; party-name list `$21:C56D` indexed as `$B3 + 2n`): keep them in place and in order.
- **FA** ends a battle message (the battle printer stops there; `$20:9364-$9612` is a run of FA messages, each with
  its own immediate). In menu/credits strings the routine reads on past FA, so pieces split at FA stay in order.
  Battle text writes `00` (two 00 bytes) where the engine inserts a monster/actor/item name.
- **Default hero names** `$21:EF9B`, 4 x 8 bytes FF-padded (ラルフ テオ リズ ルミエス), copied to `$0E3B + $40n`.
- **Name-entry chart** `$21:ECD5-$ED9D` (200 glyph codes: katakana, hiragana, A-Z, digits, in screen order).
- Battle/menu strings in banks $20/$21 are space-padded fixed-width fields (`こうげき   `).
- Not text (census false hits in text banks): `$00:8FAC` (code), `$21:83B3` (flag table). Banks with no text
  pointer (02-0B, 0D, 0E, 13, 14, 16-1F, 22-2F) have only random census hits.

## Script files (phase 4, `tools/extract.py`)
`script/dialogue_{0F,11,12,15}.json` (2257 strings), `script/names.json` (773), `script/system.json` (288).
Each entry: `id`, `jp` (exact bytes through tbl), `en`; system entries also `block`, `refs`, and `kind`/`size` for
fixed/grid. Tests: every jp re-encodes to the ROM bytes, names tile their region, every pointer target is a piece
start, every census run in a text-pointer bank is inside an item. Re-running the extractor keeps `en` while `jp`
is unchanged.

## Free space (FF runs at bank ends, candidates only; trap-test before use)
$0F:E531 (6.8K), $11:F7AD (2.1K), $12:F22E (3.5K), $15:FC88 (0.9K), $0D:F279 (3.4K), $01:F746 (2.2K),
$1D:F74B (2.2K), $25:F920 (1.7K), $29:FA17 (1.5K), $20:FD5E (0.7K), $21:FCBF (0.8K), $0C:FDC5 (0.6K).
Expansion: the header already declares 2 MB, so banks $30-$3F (512 KB) can be appended (FF-filled) at no cost.
A map package can move to an expanded bank by rewriting the 24-bit pointer at its map entry +10.
