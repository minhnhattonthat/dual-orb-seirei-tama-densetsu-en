-- Where is the CPU stuck? Logs the PC at NMI-free points: one line per distinct PC seen in frames FROM..TO
-- (sampled every 7 frames).   emu.py ... --script tools/lua/pcsample.lua --var FROM=1800 --var TO=2400
local from, to, seen = FROM or 0, TO or math.huge, {}
L.on_frame(function()
  if L.frame < from or L.frame > to or L.frame % 7 ~= 0 then return end
  local pc = L.pc()
  if not seen[pc] then
    seen[pc] = true
    L.log(string.format("f%d pc=%06X", L.frame, pc & 0xFFFFFF))
  end
end)
