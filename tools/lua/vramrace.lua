-- Race check for any main-thread VRAM write (not just the fenced queue flush): logs "RACE" when the VWF upload
-- (code in bank $B0) set $2115/$2116 after other code set the VRAM address and before that code's next data write
-- ($2118/$2119) or DMA ($420B), i.e. the game's write went to our address (issue #1/#4 map corruption).
-- emu.py ... --script tools/lua/vramrace.lua (after warp.lua's scripts)
local pending, dirty, races, sets = false, false, 0, 0
local seen, writers = {}, {}  -- writers: PC of every other $2115-$2117 write -> count, scanline range
L.on_write(0x2115, 0x2117, function(addr, value)
  local pc = L.pc()
  if (pc >> 16) & 0x7F == 0x30 then
    if pending and (addr & 0xFFFF) ~= 0x2115 then dirty = true end  -- gdma_off's $2115 = $80 is the game's own
  else
    pending, dirty = true, false
    sets = sets + 1
    local k = string.format("%06X", pc & 0xFFFFFF)
    local line = emu.getState()["ppu.scanline"]
    local w = writers[k] or { n = 0, lo = 999, hi = -1 }
    w.n, w.lo, w.hi = w.n + 1, math.min(w.lo, line), math.max(w.hi, line)
    writers[k] = w
  end
end)
local function use(addr, value)
  local pc = L.pc()
  if (pc >> 16) & 0x7F == 0x30 then return end
  if dirty then
    races = races + 1
    local key = string.format("%06X", pc)
    seen[key] = (seen[key] or 0) + 1
    if seen[key] <= 3 then
      L.log(string.format("RACE f%d %04X=%02X pc=%06X line=%d", L.frame, addr & 0xFFFF, value, pc,
        emu.getState()["ppu.scanline"]))
    end
  end
  dirty = false
end
L.on_write(0x2118, 0x2119, use)
L.on_write(0x420B, 0x420B, function(addr, value)
  for ch = 0, 7 do  -- only a DMA to VRAM ($2118/$2119) uses the address
    if value & (1 << ch) ~= 0 and emu.read(0x4301 + ch * 0x10, emu.memType.snesMemory) & 0xFE == 0x18 then
      return use(addr, value)
    end
  end
end)
L.on_frame(function(f)
  if f == FRAMES - 1 then
    for k, w in pairs(writers) do L.log(string.format("writer %s n=%d lines %d-%d", k, w.n, w.lo, w.hi)) end
    L.log(string.format("vramrace: %d address sets, %d races", sets, races))
  end
end)
