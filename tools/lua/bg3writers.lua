-- Which code writes which tiles into the BG3 tilemap buffer $7F:F000-$7F:FFFF. Logs "pc=... tiles=lo-hi n=count"
-- per writer at the end, so text drawn outside $00:AEB6 shows up.
--   emu.py ROM --out DIR ... --script tools/lua/bg3writers.lua --frames N
local seen = {}
emu.addMemoryCallback(function(a, v)
  if a < 0x7FF000 or (a & 1) == 0 then return end  -- the high byte lands last; read the word then
  local pc = L.pc()
  local o = a - 1 - 0x7E0000
  local w = emu.read(o, emu.memType.snesWorkRam) | (v << 8)
  local t = w & 0x3FF
  local s = seen[pc] or { n = 0, lo = 0x3FF, hi = 0, tiles = {} }
  seen[pc] = s
  s.n = s.n + 1
  s.lo = math.min(s.lo, t); s.hi = math.max(s.hi, t)
  s.tiles[t] = true
end, emu.callbackType.write, 0x1F000, 0x1FFFF, emu.cpuType.snes, emu.memType.snesWorkRam)
L.on_frame(function(f)
  if f ~= FRAMES - 1 then return end
  for pc, s in pairs(seen) do
    local k = {}
    for t in pairs(s.tiles) do k[#k + 1] = t end
    table.sort(k)
    local few = {}
    for i = 1, math.min(#k, 24) do few[#few + 1] = string.format("%X", k[i]) end
    L.log(string.format("pc=%06X n=%d tiles=%X-%X distinct=%d [%s]", pc, s.n, s.lo, s.hi, #k, table.concat(few, " ")))
  end
end)
