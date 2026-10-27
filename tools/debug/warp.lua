-- Cold-boot warp: title -> New Game (forced) -> intro skipped -> field start overridden with a scene from scenes.lua.
--   emu.py ROM --out DIR --script tools/debug/scenes.lua --script tools/debug/warp.lua --var "SCENE='place03'"
--          --frames 1500 --sheet
-- Ad hoc, on top of any scene (or SCENE='map' with MAP/X/Y; doors.py lists every map with a door spawn):
--   KEYS='6 x;60 -'  replace the keys    STEP=42   cutscene step ($1C45)   SCRIPT=0xED35  spawn an event script
--   MODE=4 SHOP=2    field sub-mode       GOD=1     party never wipes       STATS=255      set the combat stats
--   WARP_STOP=1      stop at "ready": shot warp.png, WARP_STATE=[[abs path]] saves a state there first
-- Logs "warp: ready" once the scene's keys are done, then "warp: check ok|FAIL" (field map pointer $E3 == scene
-- map). Addresses and how they were found: docs/re/debug.md.
local mem = emu.memType.snesMemory
local sc = assert(SCENE_LIST, "pass --script tools/debug/scenes.lua first")[SCENE]
if SCENE == "map" then sc = { map = MAP, x = X, y = Y } end
assert(sc, "unknown SCENE " .. tostring(SCENE))
if KEYS then sc.keys = KEYS end
if STEP then sc.pokes = { [0x1C45] = STEP } end
if SCRIPT then sc.script = SCRIPT end
if MODE then sc.pokes = { [0x7FD7AE] = SHOP or 0, [0x7FD7AC] = 0x8000 | MODE } end
local god, stats = GOD or sc.god, STATS or sc.stats
local function w16(a, v) emu.write(a, v & 0xFF, mem); emu.write(a + 1, (v >> 8) & 0xFF, mem) end
local function r24(a) return emu.read(a, mem) | emu.read(a + 1, mem) << 8 | emu.read(a + 2, mem) << 16 end

local stage = "title"
-- Title/file select: tap Start and A until the new-game/load branch runs.
L.on_frame(function(f)
  if stage == "title" and f > 60 and f % 20 == 0 then L.press(f % 40 == 0 and "start" or "a", 4) end
end)
-- $21:EE69 picks new game ($1C87 = 0) or a save slot: always new game.
L.on_exec(0x21EE69, 0x21EE69, function()
  if stage == "title" then w16(0x1C87, 0); stage = "intro"; L.log("warp: new game f" .. L.frame) end
end)
-- Intro crawl loop ($0C:D3E9..D413) ends when DP $20 == $FF (sc.intro keeps the crawl).
L.on_exec(0x0CD40E, 0x0CD40E, function()
  if stage == "intro" and not sc.intro then w16(0x0020, 0x00FF) end
end)
-- Field start from the saved position ($10:C5C0 reads $1C9D/$1C9F/$1CA1/$1CA3; $0C:C71D first swaps $1CA1 for
-- the save room of place $1CA5, so $1CA5 = 0 keeps the map we set). No sc.map: the plain new-game opening.
L.on_exec(0x10C5C0, 0x10C5C0, function()
  if stage ~= "intro" then return end
  stage = "field"
  if not sc.map then return end
  w16(0x1C9D, sc.x * 16)
  w16(0x1C9F, sc.y * 16)
  w16(0x1CA1, sc.map & 0xFFFF)
  w16(0x1CA3, sc.map >> 16)
  w16(0x1CA5, 0)
  for _, n in ipairs(sc.flags or {}) do emu.write(0x7FCF83 + n, 1, mem) end
  L.log(string.format("warp: field %s map=%06X f%d", SCENE, sc.map, L.frame))
end)
-- Field main loop ($10:8139) running = the map is up.
local up
L.on_exec(0x108139, 0x108139, function()
  if stage ~= "field" then return end
  stage, up = "fadein", L.frame
  L.log("warp: field up f" .. L.frame)
end)
-- sc.script: spawn an event script (bank $10) the way the game does ($10:ED26: LDA #ptr; STA $0000; JSL $0C:8BEB;
-- the callee uses A as well). At the field loop's JSR $8162 ($10:8148: 16-bit A/X, D = 0, DB = $10) push that
-- JSR's return and enter $10:ED2D (STA $0000) with A = ptr. Writing $0000 from Lua instead didn't take.
local spawn
L.on_exec(0x108148, 0x108148, function()
  if not spawn then return end
  local sp = emu.getState()["cpu.sp"]
  w16(sp - 1, 0x814A)
  emu.setState({ ["cpu.pc"] = 0xED2D, ["cpu.sp"] = sp - 2, ["cpu.a"] = spawn })
  L.log(string.format("warp: script %04X f%d", spawn, L.frame))
  spawn = nil
end)
-- Saving ($21:F7E4) waits for APU port $2142 to change after the save sound; after a warp it never does (same on
-- the original ROM), so make the compare fail: DP $B1 = port value + 1.
L.on_exec(0x21F7E4, 0x21F7E4, function()
  emu.write(0x00B1, (emu.read(0x2142, mem) + 1) & 0xFF, mem)
end)
-- GOD: clear every party member's dead flag (+$34; $0C:A05B wipes the party when all are set) each frame.
-- STATS=v sets the words +$1A..+$28 (combat stats: 255 wins boss fights at level 1).
L.on_frame(function()
  if not god or stage == "title" or stage == "intro" then return end
  for n = 0, 3 do
    local b = 0x0E3B + 0x40 * n
    w16(b + 0x34, 0)
    if stats then for o = 0x1A, 0x28, 2 do w16(b + o, stats) end end
  end
end)
-- 120 frames after the field is up (60 was too early for SCRIPT 0xED35: it stayed black), apply the pokes
-- ({[addr] = 16-bit value}) and the script, then play the keys ("30 -;6 x;60 -").
L.on_frame(function(f)
  if stage == "fadein" and f >= up + 120 then
    for a, v in pairs(sc.pokes or {}) do w16(a, v) end
    spawn = sc.script
    for step in (sc.keys or ""):gmatch("[^;]+") do
      local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
      L.press(spec, tonumber(n))
    end
    L.press("-", 30)
    stage = "keys"
  elseif stage == "keys" and L.route_done() then
    stage = "ready"
    L.log("warp: ready f" .. f)
    if sc.map and not sc.nocheck then
      local m = r24(0x00E3)
      L.log(string.format("warp: check %s map %06X", m == sc.map and "ok" or "FAIL", m))
    else
      L.log("warp: check ok (no map check)")
    end
    if WARP_STOP then
      L.shot("warp.png")
      if WARP_STATE then L.save_state(WARP_STATE, function() L.finish(0) end) else L.finish(0) end
    end
  end
end)
