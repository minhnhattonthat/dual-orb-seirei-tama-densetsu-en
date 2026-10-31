-- Who writes WRAM LO..HI (default $7E:E000-$7E:FFFF): logs each writer PC once with its first address and frame,
-- and counts writes per PC (code in bank $B0 = the VWF). Same callback form as wramuse.lua.
--   emu.py ROM --out DIR ... --script tools/lua/wramwho.lua --var LO=0x7EE000 --var HI=0x7EFFFF
local lo, hi = LO or 0x7EE000, HI or 0x7EFFFF
local who = {}
emu.addMemoryCallback(function(a)
  local o = 0x7E0000 + (a >= 0x7E0000 and a - 0x7E0000 or (a & 0x1FFF))
  local k = string.format("%06X", L.pc() & 0xFFFFFF)
  local w = who[k]
  if not w then
    w = { n = 0, lo = o, hi = o }
    who[k] = w
    L.log(string.format("first f%d pc=%s addr=%06X", L.frame, k, o))
  end
  w.n, w.lo, w.hi = w.n + 1, math.min(w.lo, o), math.max(w.hi, o)
end, emu.callbackType.write, lo - 0x7E0000, hi - 0x7E0000, emu.cpuType.snes, emu.memType.snesWorkRam)
L.on_frame(function(f)
  if f ~= FRAMES - 1 then return end
  for k, w in pairs(who) do L.log(string.format("writer %s n=%d %06X-%06X", k, w.n, w.lo, w.hi)) end
end)
