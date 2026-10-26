-- Log each string the main text engine ($00:A94C) starts: frame, D, the 24-bit pointer at [D+$B3] and the caller.
--   emu.py ... --script tools/lua/textlog.lua
local mem = emu.memType.snesMemory
local last = -1
L.on_exec(0x00A96D, 0x00A96D, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local p = emu.read(d + 0xB3, mem) | emu.read(d + 0xB4, mem) << 8 | emu.read(d + 0xB5, mem) << 16
  local y = emu.read(0x0DF9, mem) | emu.read(0x0DFA, mem) << 8
  if p ~= last then
    last = p
    local sp = s["cpu.sp"]
    local t = {}
    for i = 1, 12 do t[#t + 1] = string.format("%02X", emu.read(0x000100 + ((sp + i) & 0xFFFF) - 0x100, mem)) end
    L.log(string.format("f%d D=%04X ptr=%06X y=%04X stack=%s", L.frame, d, p, y, table.concat(t, " ")))
  end
end)
