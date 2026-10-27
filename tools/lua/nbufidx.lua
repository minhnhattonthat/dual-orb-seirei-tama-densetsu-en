-- Log insert-buffer accesses ($7F:EF00, asm/names.asm names_wby/wbx/rby) whose index is >= $100 (past the buffer):
-- frame, helper pc, index, A and the return addresses on the stack.
--   emu.py ... --script tools/lua/nbufidx.lua
local mem = emu.memType.snesMemory
local seen = {}
local function hook(pc, reg)
  L.on_exec(pc, pc, function()
    local s = emu.getState()
    local i = s["cpu." .. reg]
    if i < 0x100 then return end
    local sp, t = s["cpu.sp"], {}
    for k = 1, 9 do t[#t + 1] = string.format("%02X", emu.read((sp + k) & 0xFFFF, mem)) end
    local key = pc .. table.concat(t)
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("f%d pc=%06X idx=%04X a=%04X stack=%s", L.frame, pc, i, s["cpu.a"], table.concat(t, " ")))
  end)
end
hook(0x00D689, "y")  -- names_wby (index Y)
hook(0x00D691, "x")  -- names_wbx (index X)
