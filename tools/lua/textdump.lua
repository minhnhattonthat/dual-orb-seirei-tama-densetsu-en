-- Like textlog.lua, plus the first 24 bytes of each string the engine starts (for strings built in WRAM).
--   emu.py ... --script tools/lua/textdump.lua
local mem = emu.memType.snesMemory
local last = -1
L.on_exec(0x00A96D, 0x00A96D, function()
  local d = emu.getState()["cpu.d"]
  local p = emu.read(d + 0xB3, mem) | emu.read(d + 0xB4, mem) << 8 | emu.read(d + 0xB5, mem) << 16
  if p == last then return end
  last = p
  local t = {}
  for i = 0, 23 do t[#t + 1] = string.format("%02X", emu.read((p & 0xFF0000) | ((p + i) & 0xFFFF), mem)) end
  L.log(string.format("f%d ptr=%06X %s", L.frame, p, table.concat(t, " ")))
end)
