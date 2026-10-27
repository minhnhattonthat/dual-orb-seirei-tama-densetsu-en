# bash tools/debug/shot.sh SCENE... : warp to each scene on build/dual_orb_en.sfc (cold boot), one zoomed sheet of the
# final frames at work/qa/shot.png. FRAMES=N to run longer (default 1400; long key routes need ~1600).
cd "$(dirname "$0")/../.."
SKILL=$(python tools/skill.py)
outs=()
for s in "$@"; do
  python -X utf8 $SKILL/scripts/emu.py "${ROM:-build/dual_orb_en.sfc}" --out work/qa/s_$s --script tools/debug/scenes.lua \
    --script tools/debug/warp.lua --var "SCENE='$s'" --frames ${FRAMES:-1400} | tail -1
  outs+=(work/qa/s_$s/final.png)
done
python -X utf8 $SKILL/scripts/sheet.py "${outs[@]}" --zoom 2 --out work/qa/shot.png | tail -1
