# Debug warp: addresses

What `tools/debug/warp.lua` relies on. All found with exec/write hooks in MesenCE on the original ROM
(`work/tmp/hits.lua`, `pclog.lua`); runs named are under `work/qa/`.

## Boot

| Address | What | State |
|---|---|---|
| `$21:EE40` | title / file-select loop; buttons in `$0DC1` | verified (hits) |
| `$21:EE69` | new game vs load branch: `$1C87 = 0` = new game | verified: warp forces it, `warp1` |
| `$21:F041` | new-game init | verified (hits) |
| `$0C:D685`, loop `$0C:D3E9..D413` | intro crawl; ends when DP `$20 == $FF` (warp writes it at `$0C:D40E`) | verified: `ng4`, field at f408 instead of ~11000 |
| `$10:80A1` | field start; `$10:C5C0` reads `$1C9D/$1C9F` (x, y in px = tile*16), `$1CA1/$1CA3` (map entry, 24-bit) | verified: every place scene |
| `$0C:C71D` | swaps `$1CA1` for the save room of place `$1CA5` (save table `$0C:C752`); warp sets `$1CA5 = 0` | verified |
| `$21:FA7B` | load routine: map entry -> `$1CA1/$1CA3/$1CA5/$1CA9`, party `$0E3B..` | verified (hits) |
| `$10:8139` | field main loop (= map is up) | verified |

## Field

| Address | What | State |
|---|---|---|
| DP `$E3` (24-bit) | current map entry pointer (written `$10:AFBF/AFC2`); warp's "check ok" compares it | verified |
| `$10:AFBD` -> `$10:C55F` | walk-into door: sets `$7FD7B6/B8/BA/BC`, `$1C0F = $FFFF`; `$10:8148` -> `8162` -> `81A1` does the warp | verified (`door1..6`) |
| Map entry (banks $13/$14) | +0 place index (bit 7 = no banner), +10 NPCs, +20 objects, +23 doors (24-bit ptrs). Door: x, y, size, dest (24), dx, dy; list ends `FFFF` | verified: `tools/debug/doors.py` walks 103 maps from home |
| `$7FCF83+n` | story flag n, one byte each (`$10:86D8`) | verified (reads); which flag means what: not mapped |
| `$7FD7AC = $8000|n` | field sub-mode n=1..8 (`$10:8203`, dispatch `$10:8228`): 1 sell, 2 ?, 3 rename (`$21:E2AD`; was listed as save), 4 weapons, 5 armour, 6 items, 7 church (save/revive, `$20:F8D7`), 8 treasure-box game (`$0C:F130`); shop id `$7FD7AE` | verified: `mode1..8` shots; names of 1/2/8 from the screens |
| `$01:9B10`, `$01:9B60` | shop dispatcher | guess (hits only) |
| `$10:D200` | event-script interpreter (bank $10). Spawn: `LDA #ptr; STA $0000; JSL $0C:8BEB` (84 sites `$10:E820..F138`) | verified: warp enters `$10:ED2D` with A = ptr (`sED35`, `sEF23`) |
| `$1C45` | cutscene step (table `$0C:A230`, 64 entries, `$FFFF` none); bytecode `14 45 1C nn 00` sets it. 41 = epilogue lab `$14:CC90`, 42 = credits | verified: `cr1` (staff roll, play record) |
| `$10:ED35` | script: world map -> shrine -> final boss ガルバ | verified: `fin2` (boss at ~f3000) |

## Battle

| Address | What | State |
|---|---|---|
| `$7FD796 = $FFFF` | start a battle at the next field step (`$0C:C018`) | verified: `battle` |
| `$7FD7B0 = $8000|n` | boss n (0..16) via `$21:8000`, formations `$21:8062` | verified: `boss00` |
| `$7FCE78`, `$7FCE7A` | normal battle background, formation (`$21:80E2` rolls them) | verified: `battle` |
| `$10:CA0A` | encounter roll (skipped when `$7FD7C0` or `$7FD7B4` != 0) | guess (hits) |
| `$0C:C06D` | post-battle check | guess (hits) |
| `$0C:A05B` | party wipe: all members' `+$34 == 1` (dead). Wipe = battle message, respawn at home, no game-over screen | verified: `go1` |
| `$0E3B + $40n` | party member n: max HP `+$0A`, HP `+$0C`, combat stats words `+$1A..+$28`, dead `+$34` | verified for `+$34` and stats (`god1` wins boss00 at level 1); battle-time HP copy not found |

Final boss: STATS=255 still does 1 damage a hit (`fin2`, 45k frames); the ending is reached with steps 41/42.
