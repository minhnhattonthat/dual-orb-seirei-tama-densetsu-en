-- WRAM dump right after $20:8B02 unpacked $29:EE12 (battle sprites incl. the command buttons) to $7E:8000, for
-- tools/buttons.py make. On the original ROM:
--   emu.py ROM --out work/qa/g6d --frames 760 --script tools/debug/scenes.lua --script tools/debug/warp.lua
--          --var "SCENE='battle'" --script <abs>/tools/lua/btnwram.lua      -> work/qa/g6d/btn_wram.bin
L.on_exec(0x208B06, 0x208B06, function()
  L.dump_ram("btn_wram.bin")
  L.log("dumped f" .. L.frame)
end)
