-- Log every {jump} the interpreter takes (asm/names.asm names_glyph, code DF): frame, [$B3]+Y and 16 bytes there.
--   emu.py ... --script tools/lua/jumplog.lua [--var "AT=0x00D6xx"]   (AT = the CMP #$DF address, default below)
local mem = emu.memType.snesMemory
local at = AT or 0x00D6A2
L.on_exec(at, at, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local p = emu.read(d + 0xB3, mem) | emu.read(d + 0xB4, mem) << 8 | emu.read(d + 0xB5, mem) << 16
  local y = s["cpu.y"]
  if (s["cpu.a"] & 0xFF) ~= 0xDF then return end
  local t = {}
  for i = 0, 15 do t[#t + 1] = string.format("%02X", emu.read((p & 0xFF0000) | ((p + y + i) & 0xFFFF), mem)) end
  L.log(string.format("f%d jump at %06X+%04X: %s", L.frame, p, y, table.concat(t, " ")))
end)
