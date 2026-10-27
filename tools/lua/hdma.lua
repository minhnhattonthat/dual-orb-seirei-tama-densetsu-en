-- At frame AT (default 2040) log each DMA channel's registers ($43x0-$43x7: mode, B-bus target, table address/bank)
-- and the first 32 bytes of its HDMA table, plus the word at WATCH (default $0D9C, BG3 V-scroll shadow).
--   emu.py ... --script tools/lua/hdma.lua [--var AT=2040] [--var WATCH=0x0D9C]
local mem = emu.memType.snesMemory
L.on_frame(function()
  if L.frame ~= (AT or 2040) then return end
  local w = WATCH or 0x0D9C
  L.log(string.format("f%d watch %04X = %04X", L.frame, w, emu.read(w, mem) | emu.read(w + 1, mem) << 8))
  for c = 0, 7 do
    local b = 0x4300 + c * 16
    local r = {}
    for i = 0, 7 do r[#r + 1] = string.format("%02X", emu.read(b + i, mem)) end
    local a = emu.read(b + 2, mem) | emu.read(b + 3, mem) << 8 | emu.read(b + 4, mem) << 16
    local t = {}
    for i = 0, 31 do t[#t + 1] = string.format("%02X", emu.read(a + i, mem)) end
    L.log(string.format("ch%d %s table %06X: %s", c, table.concat(r, " "), a, table.concat(t, " ")))
  end
end)
