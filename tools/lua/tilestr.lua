-- Log each call of the BG3 tile-string drawer $00:D753 (X = column, Y = row, [$B7] = codes via the $00:D7AF
-- table: underlines, frames): frame, pointer, column, row, first bytes and the stack (JSL return address).
--   emu.py ... --script tools/lua/tilestr.lua
local mem = emu.memType.snesMemory
L.on_exec(0x00D753, 0x00D753, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local p = emu.read(d + 0xB7, mem) | emu.read(d + 0xB8, mem) << 8 | emu.read(d + 0xB9, mem) << 16
  local b = {}
  for i = 0, 11 do b[#b + 1] = string.format("%02X", emu.read((p & 0xFF0000) | ((p + i) & 0xFFFF), mem)) end
  local sp, t = s["cpu.sp"], {}
  for i = 1, 6 do t[#t + 1] = string.format("%02X", emu.read((sp + i) & 0xFFFF, mem)) end
  L.log(string.format("f%d ptr=%06X x=%d y=%d %s stack=%s", L.frame, p, s["cpu.x"], s["cpu.y"],
    table.concat(b, " "), table.concat(t, " ")))
end)
