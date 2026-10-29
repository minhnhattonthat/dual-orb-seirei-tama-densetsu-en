-- VWF upload state each NMI: "f<frame> v<scanline> idle|nmi H T Q.. D I P OPENT TL TR TILE G" from frame FROM to TO.
-- Ring head/tail, queued runs (vram:bytes), DRAWN, INDRAW, PENSUB, pairs in progress, GDMA (docs/re/vwf.md).
--   emu.py ... --script tools/lua/vwfstate.lua --var "FROM=640" --var "TO=662" --var "IDLE=0xB0xxxx" --var "NMI=0xB0xxxx"
-- IDLE/NMI = vwf_idle/vwf_nmi: the JSL targets at ROM offsets $5E8 / $A9 of the build.
local from, to = FROM or 0, TO or 1e9
local function w(a) return emu.read16(a, emu.memType.snesWorkRam) end
local function dump(tag)
  if L.frame < from or L.frame > to then return end
  local h, t, q = w(0xF820), w(0xF822), {}
  local i = h
  while i ~= t and #q < 12 do
    q[#q + 1] = string.format("%04X:%X", w(0xFA00 + i), w(0xFE00 + i))
    i = (i + 2) & 0x1FE
  end
  L.log(string.format("f%d v%d %s H%03X T%03X [%s] D%X I%X P%X O%04X L%04X R%04X X%04X G%X", L.frame,
    emu.getState()["snes.ppu.scanline"] or -1, tag, h, t, table.concat(q, " "), w(0xF830), w(0xF834), w(0xF804),
    w(0xF806), w(0xF810), w(0xF812), w(0xF82A), emu.read(0xF832, emu.memType.snesWorkRam)))
end
emu.addMemoryCallback(function() dump("idle") end, emu.callbackType.exec, IDLE, IDLE, emu.cpuType.snes)
emu.addMemoryCallback(function() dump("nmi") end, emu.callbackType.exec, NMI, NMI, emu.cpuType.snes)
