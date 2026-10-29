-- Who writes given columns of the BG3 tilemap buffer $7F:F000-$7F:FFFF (32 cells a row, row stride $40):
-- logs "f<frame> r<row> c<col> <tile word> pc" per (row, col, value, PC), from frame FROM on.
--   emu.py ... --script tools/lua/cellwrites.lua --var "CLO=24" --var "CHI=25" [--var "FROM=1300"]
local lo, hi, from = CLO or 0, CHI or 31, FROM or 0
local last = {}
emu.addMemoryCallback(function(a, v)
  if L.frame < from or a < 0x7FF000 or (a & 1) == 0 then return end  -- the high byte lands last
  local o = a - 1 - 0x7E0000
  local col, row = (o & 0x3F) >> 1, (o - 0x1F000) >> 6
  if col < lo or col > hi then return end
  local w = emu.read(o, emu.memType.snesWorkRam) | (v << 8)
  local key = string.format("r%d c%d %04X %06X", row, col, w, L.pc())
  if last[o] ~= key then
    last[o] = key
    L.log(string.format("f%d %s", L.frame, key))
  end
end, emu.callbackType.write, 0x1F000, 0x1FFFF, emu.cpuType.snes, emu.memType.snesWorkRam)
