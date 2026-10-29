# bash tools/debug/talk.sh NAME MAP X Y KEYS : warp to MAP at X,Y on the EN build and the original, play KEYS, one
# side-by-side sheet (EN | JP) of the final frames at work/qa/talk_NAME.png. FRAMES=N to run longer (default 1500).
#   bash tools/debug/talk.sh sell 13A4A8 F7 0B "30 -;40 up;6 a;200 -"      (shop greeting, issue #1)
cd "$(dirname "$0")/../.."
SKILL=$(python tools/skill.py)
for r in en jp; do
  rom=build/dual_orb_en.sfc
  [ $r = jp ] && rom="rom/Dual Orb - Seirei Tama Densetsu (Japan).sfc"
  python -X utf8 $SKILL/scripts/emu.py "$rom" --out work/qa/talk_$1_$r --script tools/debug/scenes.lua \
    --script tools/debug/warp.lua --var "SCENE='map'" --var "MAP=0x$2" --var "X=0x$3" --var "Y=0x$4" \
    --var "KEYS='$5'" --frames ${FRAMES:-1500} | tail -1 &
done
wait
python -X utf8 $SKILL/scripts/sheet.py work/qa/talk_$1_en/final.png --compare work/qa/talk_$1_jp/final.png --zoom 2 \
  --out work/qa/talk_$1.png | tail -1
