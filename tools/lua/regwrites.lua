-- Log writes to a PPU/CPU register range (default $2111-$2112, BG3 H/V scroll): frame, register, value, PC.
-- One line per (register, value, PC) change, so a steady per-frame write logs once.
--   emu.py ... --script tools/lua/regwrites.lua [--var "LO=0x2111"] [--var "HI=0x2112"]
local last = {}
L.on_write(LO or 0x2111, HI or 0x2112, function(addr, value)
  local pc = L.pc()
  local key = string.format("%04X %02X %06X", addr & 0xFFFF, value, pc)
  if last[addr] ~= key then
    last[addr] = key
    L.log(string.format("f%d %s", L.frame, key))
  end
end)
