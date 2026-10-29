-- Race check for the game's DMA-queue flush ($00:9795 .. $97C3, per entry: VMAIN, VRAM address, DMA) run by the main
-- thread: logs "RACE" when other code writes $2115/$2116 inside that window (an NMI upload cut in, issue #1), and
-- counts the windows seen. emu.py ... --script tools/lua/dmarace.lua
local open, windows, races = false, 0, 0
L.on_exec(0x009795, 0x009795, function()
  if emu.getState()["ppu.scanline"] < 225 then open = true; windows = windows + 1 end
end)
L.on_exec(0x0097C3, 0x0097C3, function() open = false end)
L.on_write(0x2115, 0x2116, function(addr, value)
  local pc = L.pc()
  if open and (pc >> 16) ~= 0 then
    races = races + 1
    L.log(string.format("RACE f%d %04X=%02X pc=%06X", L.frame, addr & 0xFFFF, value, pc))
  end
end)
L.on_frame(function(f)
  if f == FRAMES - 1 then L.log(string.format("dmarace: %d main-thread flush entries, %d races", windows, races)) end
end)
