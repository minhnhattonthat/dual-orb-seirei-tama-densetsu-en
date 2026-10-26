-- Log each distinct tilemap target [$BB] (with its bank $BD) the glyph drawer $00:AEB6 writes to: frame and address.
--   emu.py ... --script tools/lua/bblog.lua
local mem = emu.memType.snesMemory
local seen = {}
L.on_exec(0x00AEB6, 0x00AEB6, function()
  local d = emu.getState()["cpu.d"]
  local p = emu.read(d + 0xBB, mem) | emu.read(d + 0xBC, mem) << 8 | emu.read(d + 0xBD, mem) << 16
  local k = p & 0xFFFFC0
  if seen[k] then return end
  seen[k] = true
  L.log(string.format("f%d bb=%06X", L.frame, p))
end)
