-- Dump PPU state plus WRAM at frame DUMP_AT (default FRAMES-1): <out>/vwf.vram.bin, vwf.wram.bin (128 KB),
-- for checking VWF pool tiles: tilemap buffer $7F:F000, shadow $7E:E000, VRAM BG3 chr. tools/vwfcheck.py reads them.
local at = DUMP_AT or (FRAMES - 1)
L.on_frame(function(f)
  if f ~= at then return end
  L.dump_ppu("vwf")
  local t = {}
  for a = 0, 0x1FFFF do t[#t + 1] = string.char(emu.read(a, emu.memType.snesWorkRam)) end
  L.write_file("vwf.wram.bin", table.concat(t))
end)
