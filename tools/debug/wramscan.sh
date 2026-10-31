# bash tools/debug/wramscan.sh [SCENE...] : WRAM pages the game writes, over many scenes on the original ROM
# (tools/lua/wramuse.lua per scene, 4 at a time), union by tools/wramfree.py -> work/qa/wram/free.txt.
# Default scenes: every place, battles, bosses, menus, shops, world map, credits. FRAMES=N (default 2600).
# Issue #4: a map's tile staging buffer ($7E:9000 up, $01:E140) reached the VWF shadow at $7E:E000 in the waterway.
cd "$(dirname "$0")/../.."
SKILL=$(python tools/skill.py)
ROM=${ROM:-"rom/Dual Orb - Seirei Tama Densetsu (Japan).sfc"}
mkdir -p work/qa/wram
scenes="$*"
[ -z "$scenes" ] && scenes="$(grep -o '^  place[0-9]* = ' tools/debug/scenes.lua | tr -d ' =') worldmap home battle battle_win
  waterway_battle boss00 boss06 boss12 menu_item_list menu_magic_list menu_equip_info menu_status shop_buy church_saved
  name_entry credits ending_lab village_event opening"
export SKILL ROM
printf '%s\n' $scenes | xargs -P 4 -I{} sh -c 'python -X utf8 "$SKILL/scripts/emu.py" "$ROM" --out work/qa/wram/{} \
  --script tools/debug/scenes.lua --script tools/debug/warp.lua --script tools/lua/wramuse.lua --var "SCENE='"'"'{}'"'"'" \
  --frames ${FRAMES:-2600} --timeout 900 > /dev/null 2>&1; echo {} $?'
python tools/wramfree.py work/qa/wram/*/wramuse.txt | tee work/qa/wram/free.txt
