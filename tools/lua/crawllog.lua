-- Log each intro-crawl line print (asm/crawl.asm): frame, BG3 scroll $0D9C, box row $0E07 and the line in !LBUF.
--   emu.py ... --script tools/lua/crawllog.lua --var "ADDR=0xB0D4C7"   (the crawl_line JSL $00A89E; find it in the build)
local mem = emu.memType.snesMemory
local function w(a) return emu.read(a, mem) | emu.read(a + 1, mem) << 8 end
L.on_exec(ADDR, ADDR, function()
  local t = {}
  for i = 0, 63 do
    local b = emu.read(0x7FEE80 + i, mem)
    if b == 0xFF then break end
    t[#t + 1] = string.format("%02X", b)
  end
  L.log(string.format("f%d scroll=%04X row=%d n=%d %s", L.frame, w(0x0D9C), w(0x0E07), #t, table.concat(t, "")))
end)
