-- Which 256-byte WRAM pages the game writes, for picking free RAM. Writes <out>/wramuse.txt at the end:
-- one line per 4 KB, a char per page ("#" written, "." never). Union several runs with tools/wramfree.py.
--   emu.py ROM --out DIR --script tools/debug/scenes.lua --script tools/debug/warp.lua --var "SCENE='x'"
--          --script tools/lua/wramuse.lua --frames N
-- Not L.on_write: on a snesWorkRam callback MesenCE 2.2.1 passes the CPU address ($7FF000, or $0000-$1FFF for the
-- low mirror), and the lib adds $7E0000 again.
local pages = {}
emu.addMemoryCallback(function(a)
  local o = a >= 0x7E0000 and a - 0x7E0000 or (a & 0x1FFF)
  pages[o >> 8] = true
end, emu.callbackType.write, 0, 0x1FFFF, emu.cpuType.snes, emu.memType.snesWorkRam)
L.on_frame(function(f)
  if f ~= FRAMES - 1 then return end
  local t = {}
  for blk = 0, 31 do
    local s = {}
    for p = 0, 15 do s[#s + 1] = pages[blk * 16 + p] and "#" or "." end
    t[#t + 1] = string.format("%06X %s", 0x7E0000 + blk * 0x1000, table.concat(s))
  end
  L.write_file("wramuse.txt", table.concat(t, "\n") .. "\n")
end)
