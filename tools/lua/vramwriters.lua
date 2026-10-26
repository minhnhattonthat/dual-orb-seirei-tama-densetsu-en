-- Which DMAs hit VRAM words VLO-VHI (default: BG3 chr tiles $0A2-$0A4): on each $420B write, logs frame, scanline,
-- PC, VRAM address, source and size of every enabled VRAM channel ($2118), so a pool tile the VWF did not send can
-- be traced to the game's upload. Also prints the DMA state keys once (KEYS=true).
--   emu.py ROM --out DIR ... --var VLO=0x2510 --var VHI=0x2527 --script tools/lua/vramwriters.lua
local lo, hi = VLO or 0x2510, VHI or 0x2527
local shown = false
emu.addMemoryCallback(function(a, v)
  local s = emu.getState()
  if KEYS and not shown then
    shown = true
    local k = {}
    for n in pairs(s) do if n:find("dma") or n:find("vramAddr") then k[#k + 1] = n end end
    table.sort(k)
    L.log(table.concat(k, " "))
  end
  local va = s["ppu.vramAddress"]
  for ch = 0, 7 do
    if v & (1 << ch) ~= 0 then
      local p = "dmaController.channel[" .. ch .. "]."
      local dest = s[p .. "destAddress"] or -1
      local size = s[p .. "transferSize"] or -1
      local src = (s[p .. "srcBank"] or 0) * 0x10000 + (s[p .. "srcAddress"] or 0)
      if dest == 0x18 then
        local words = size == 0 and 0x8000 or size // 2
        if va <= hi and va + words > lo then
          L.log(string.format("frame=%d line=%d pc=%06X ch%d vram=%04X src=%06X size=%04X", s["ppu.frameCount"] or -1,
            s["ppu.scanline"] or -1, L.pc(), ch, va, src, size))
        end
      end
    end
  end
end, emu.callbackType.write, 0x420B, 0x420B, emu.cpuType.snes, emu.memType.snesMemory)
