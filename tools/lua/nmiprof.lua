-- Scanline at each step of the game's NMI ($00:8077), frames F0..F1 (logged on NMIs that ready a game frame).
--   emu.py ... --script tools/lua/nmiprof.lua --var "F0=760" --var "F1=800"
local pts = {0x008077,0x008095,0x008099,0x00809D,0x0080A0,0x0080A3,0x0080A6,0x0080A9,0x0080AD}
local row = {}
for _, a in ipairs(pts) do
  L.on_exec(a, a, function()
    if L.frame < F0 or L.frame > F1 then return end
    local s = emu.getState()
    if a == 0x008077 then row = {} end
    row[#row+1] = string.format("%X:%d", a & 0xFFF, s["ppu.scanline"])
    if a == 0x0080AD then L.log("f"..L.frame.." "..table.concat(row," ")) end
  end)
end
