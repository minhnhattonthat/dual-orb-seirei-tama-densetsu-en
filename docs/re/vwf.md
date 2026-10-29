# VWF engine (phase 5)

Source: `asm/vwf.asm` (asar 1.91 in `tools/asar/`, applied by `tools/asm.py`), font `fonts/vwf.txt` ->
`tools/font.py` -> `build/vwf/*.bin`, table `tbl/en.tbl`, text insertion `tools/insert.py`.
Tests: `tests/test_vwf.py`. Verified in game: `work/qa/vwf1` (JP script through the VWF), `work/qa/mk_open`.

## Why VWF
Glyphs were 8x16 fixed cells (one tilemap column per byte). English in fixed 8 px cells fits 24 chars in the NPC
box; the VWF (about 5.5 px a letter) fits ~35, close to the JP line count (D4: engine work before abbreviation).

## Facts it relies on (verified)
- Every glyph goes through `$00:AEB6` (code in A, cell at `[$BB]` in the BG3 tilemap buffer `$7F:F000-$FFFF`,
  32x64; bottom tile at +$40). Other writers of the buffer only write blanks/frames/icons (`tools/lua/bg3writers.lua`
  over 17 scenes): `$00:B029` arrow (tiles $60/$70), `$01:80xx`/`$01:9323`/`$00:D7A3` tiles >= $16A.
- BG3 chr = VRAM word $2000, only tiles 0-511 usable (BG1/2 chr starts at word $3000); OBJ uses $0000-$1FFF.
  Font DMA'd once at boot (f26) from `$7E:8000`; a full VRAM fill from `$7F:0000` at f178 (logo), never again
  in the tour (`work/qa/dma_*`).
- Game DMA queue `$0661` (8-byte entries: vram, src, bank | flag<<8, size; FFFF ends), byte index DP `$7B`; NMI runs
  it when `$60` is set. Game peaks at $E3 bytes; region up to `$0A62` (cleared at boot by `$00:DFB0`).
- Free WRAM (never written in 11 scenes, `tools/lua/wramuse.lua` + `tools/wramfree.py`): `$7E:E000-$FFFF`,
  `$7F:E000-$EFFF`. Candidate, not proven for every screen.
- Engine column `$0E0B` only moves by the codes (F4-F8, FD, EF right-align) and per glyph; no auto-wrap.

## How it works
- Pool: every glyph-table tile below $180 except static ones = 182 pairs (t, t+1) = top/bottom of a cell.
  WRAM shadow at `$7E:E000 + t*16`. Vars `$7E:F800`, used flags `$7E:F860`. Check a screen's pool cells with
  `tools/lua/vwfdump.lua` + `tools/vwfcheck.py` (VRAM == shadow per row); `tools/lua/vramwriters.lua` logs DMAs
  that hit given VRAM words.
- Draw: if the engine asks for the cell right after the pen's open cell, continue in it (OR); else start fresh at
  `[$BB]`. A glyph allocates a fresh pair per cell it enters, renders through an 8x256 shift table, queues the
  pair for upload, then sets `$0E0B` so the engine's next cell is the one after the pen.
- Upload: own ring (`QV/QS/QN` at `$7E:FA00/FC00/FE00`, head/tail `$F820/$F822`; pending flag per pair `$F920` so a
  pair is queued once), not the game's `$0661` queue (bulk tiles there ran the NMI past vblank and the game's own
  tilemap rows were lost). `vwf_nmi` replaces the NMI's `JSL $00E388` at `$00:80A9`, after the game's DMA, and
  sends <= $40-byte chunks (<= $400 a frame) while `$4212` bit 7 (vblank) is set. It re-reads `$4212` after each
  DMA: if vblank ended during it, the tail was dropped, so the entry is kept and resent next frame.
  `vwf_idle` (hook on the NMI timer `$00:85E8`, which runs on every NMI) drains up to $1000 more: in menus the game
  readies a frame (`$60`) only every ~5 NMIs, and its DMA (`$00:942B`) runs lines 225-254, so the `$80A9` hook alone
  managed ~64 B a game frame and menus showed stale pool glyphs for ~130 frames. Probe: `tools/lua/nmiprof.lua`
  (scanline at each NMI step).
- Wrong (fixed for issue #1): "only NMI code sets `$2116`". The game's DMA-queue flush (`$00:9784..97DE`) also runs
  from the main thread (field loads, after every battle: ~280 entries a battle, `tools/lua/vramaddr.lua`). An NMI
  upload between an entry's VMAIN/`$2116` writes and its `$420B` sent the game's map tiles to our address (random
  map corruption after battles). `gdma_on`/`gdma_off` (hooks `$00:9795`/`$97C3`) flag that window and `upload` skips
  while it is set (`tools/lua/dmarace.lua` counts races).
- Half cells (issue #1): a redrawn cell's pair is cleared and re-rendered glyph by glyph, and an idle upload mid-redraw
  showed half cells for a frame (battle panel every 3 frames: "It m", "H^+30"). `vwf_idle` holds back only the pairs
  still in progress (`!SKIPOPEN`): when `vwf_draw` ran since the last NMI (`!DRAWN`), the pen's open pair; when the NMI
  hit inside `vwf_draw` (`!INDRAW`), also `!TILE`/`!TL`/`!TR`. A ring run is sent up to the first held pair
  (`holds` -> `!LIMIT`): runs merge, so holding the whole run held a shop's whole description. `vwf_nmi` (game frame
  ready = drawing done) sends everything. First try skipped the whole idle upload while `!DRAWN`: menus and shops draw
  for ~5 NMIs a frame, so they showed stale pool glyphs for seconds (r6 tour). Check: battle_party with KEYS
  `600 -;6 down;40 -;6 a;60 -;6 right;40 -;6 a;90 -;6 b;90 -;6 b;90 -`, `--shot-every 1`: v1.0 alternates 2-frame
  variants at f1250-1350, the fix holds each screen.
- Findings: the hook starts at scanline ~236-261 (menus ~254-257, a few lines before vblank ends), so chunks must be
  small and checked. Reading `$2137`/`$213D`/`$213F` (H/V counter latch) in the NMI hung the game at file select
  (the wait on `$60` at `$00:897B`). `enqueue` sets `$F82E` (busy) so the NMI never retires an entry mid-merge.
- Static codes (28 ・, 2F ▲, 30 ▼, 38 ▶, 3F cell space `_`) keep their original tiles, snap to the next cell,
  advance 8. `40` word space (4 px) draws nothing and blanks cells it enters.
- A cell that shows no pool pair (its row was blanked) takes back the pair it showed last if no other cell got it
  since (`!MEMO` byte per cell of the top screen `$7F:F000-$F7FF` at `$7F:8900`, `!OWNER` word per pair at
  `$7F:8D00`; `$7F:8900-$8FFF` is never written in 9 scenes, `tools/lua/wramuse.lua`): the battle panel blanks and
  redraws its row every 3 frames, and fresh pairs each time left the VRAM uploads behind (stale text, phase 7).
  A cell below the top screen (`.plain`) also records itself as the pair's owner, else a top-screen cell's memo took
  back a pair a bottom-half cell still showed (intro crawl, page 4 over page 3).
- Allocation is round-robin; when no pair is free, a sweep of `$7F:F000-$FFFF` frees pairs no cell shows.
- FastROM: code in `$B0`, writes `$420D = 1` on entry (the game's own banks are $00-$3F, unaffected).
- Unknown codes (kana) render as a hollow box (tofu), so leftover Japanese is visible.

## Limits (shortcuts in the asm)
- A screen needing more than 182 VWF cells at once garbles one cell per extra cell (forced reuse).
- Upload rate: a full screen of new cells (~130 pairs, 4 KB) needs one or two idle NMIs; a screen that readies a
  game frame on every NMI only gets the ~2-line tail of each vblank.
- Pool tiles copied by code to other WRAM and restored later would show whatever the pool holds then.

## Not pointers (guess, phase 5)
The textmap `EXTRA` 24-bit "sites" for `$12:D000`, `$12:E11F`, `$15:C900` look coincidental (`0x842E3` is
`AND #$0080; BNE`), so those items are treated as orphans and move freely with the layout.
