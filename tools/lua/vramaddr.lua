-- Log writes to $2115/$2116/$2117 (VMAIN, VRAM address) made outside vblank (scanline < 225), i.e. by the main
-- thread, where an NMI's own VRAM upload could cut in: frame, scanline, register, value, PC. One line per
-- (register, PC). Also counts every writer PC once at the end.
--   emu.py ... --script tools/lua/vramaddr.lua
local seen = {}
L.on_write(0x2115, 0x2117, function(addr, value)
  local sl = emu.getState()["ppu.scanline"]
  local pc = L.pc()
  local key = string.format("%04X %06X %s", addr & 0xFFFF, pc, sl < 225 and "main" or "vbl")
  if sl < 225 and sl > 0 and addr == 0x2116 then key = key .. " f" .. L.frame end  -- every frame of a main-thread one
  if not seen[key] then
    seen[key] = true
    L.log(string.format("f%d sl%d %s v=%02X", L.frame, sl, key, value))
  end
end)
