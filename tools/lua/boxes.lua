-- Text box geometries in use: at each glyph draw ($00:AEB6), logs box x/w ($0E03/$0E05), y/h ($0E07/$0E09) and the
-- pen column ($0E0B) once per distinct box, with the furthest column reached. Run over warp scenes for the width gate.
--   emu.py ROM --out DIR ... --script tools/lua/boxes.lua --frames N
local seen = {}
local function w(a) return emu.read16(a, emu.memType.snesWorkRam, false) end
L.on_exec(0x00AEB6, 0x00AEB6, function()
  local k = string.format("x=%d w=%d y=%d h=%d", w(0x0E03), w(0x0E05), w(0x0E07), w(0x0E09))
  local c = w(0x0E0B)
  local s = seen[k] or { n = 0, max = 0 }
  seen[k] = s
  s.n = s.n + 1
  if c > s.max then s.max = c end
end)
L.on_frame(function(f)
  if f ~= FRAMES - 1 then return end
  for k, s in pairs(seen) do L.log(string.format("box %s glyphs=%d maxcol=%d", k, s.n, s.max)) end
end)
