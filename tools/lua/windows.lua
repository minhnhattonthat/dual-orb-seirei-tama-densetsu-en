-- Log each window record the window drawer reads ($00:F1E7 LDA [$08]; records are opened by JSL $00F151 with the
-- record pointer in $00/$02): frame, record address, x y w h. Per frame while the window animates.
--   emu.py ... --script tools/lua/windows.lua
local mem = emu.memType.snesMemory
local last = {}
L.on_exec(0x00F1E7, 0x00F1E7, function()
  local d = emu.getState()["cpu.d"]
  local p = emu.read(d + 8, mem) | emu.read(d + 9, mem) << 8 | emu.read(d + 10, mem) << 16
  if last[p] == L.frame - 1 or last[p] == L.frame then last[p] = L.frame return end
  last[p] = L.frame
  local function w(i) return emu.read(p + i, mem) | emu.read(p + i + 1, mem) << 8 end
  L.log(string.format("f%d window %06X x=%d y=%d w=%d h=%d", L.frame, p, w(0), w(2), w(4), w(6)))
end)
