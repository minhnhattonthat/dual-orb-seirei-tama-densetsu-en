-- Log each time the CPU reaches ADDR (24-bit, e.g. --var "ADDR=0x01808A"): frame, A X Y, direct page $00-$07
-- and the stack (JSL/JSR return address).
--   emu.py ... --script tools/lua/calls.lua --var "ADDR=0x01808A"
local mem = emu.memType.snesMemory
L.on_exec(ADDR, ADDR, function()
  local s = emu.getState()
  local d, sp = s["cpu.d"], s["cpu.sp"]
  local dp, t = {}, {}
  for i = 0, 7 do dp[#dp + 1] = string.format("%02X", emu.read(d + i, mem)) end
  for i = 1, 6 do t[#t + 1] = string.format("%02X", emu.read((sp + i) & 0xFFFF, mem)) end
  L.log(string.format("f%d a=%04X x=%04X y=%04X dp=%s stack=%s", L.frame, s["cpu.a"], s["cpu.x"], s["cpu.y"],
    table.concat(dp, " "), table.concat(t, " ")))
end)
