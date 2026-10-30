-- Scene list for tools/debug/warp.lua: name -> where the warp puts the game. Regenerate every scene's shot and
-- savestate with tools/debug/warp_all.py. Addresses: docs/re/debug.md.
--   map    : 24-bit map entry pointer (banks $13/$14); none = the plain new-game opening
--   x, y   : spawn in 16 px tiles (door-table bytes; tools/debug/doors.py)
--   flags  : story flag numbers to set (byte per flag at $7FCF83+n)
--   pokes  : {[addr] = 16-bit value} written 120 frames after the field is up, before the keys
--   script : event script (bank $10) spawned at the same time
--   keys   : route steps played after that ("6 x;60 -"); the scene is "ready" when they are done
--   god, stats, intro, nocheck: see warp.lua
-- Passed as a --script before warp.lua (Mesen doesn't run in the repo dir, so warp.lua can't dofile it).
local function mash(n, gap) return string.rep("6 a;" .. (gap or 54) .. " -;", n) end
local HOME = { map = 0x13A3E4, x = 0x0B, y = 0x46 }  -- outside Aleitos' house (place 2)
local function at(base, more)
  local o = {}
  for k, v in pairs(base) do o[k] = v end
  for k, v in pairs(more or {}) do o[k] = v end
  return o
end
local THEO = { [0x111F] = 2, [0x0E87] = 20, [0x0E8B] = 20, [0x0EAF] = 0 }
for a = 0x0F6B, 0x0F81, 2 do THEO[a] = 0x0101 end
-- party of 4 ($111F = size-1; cursor moves to slot 3 only when it is 3, $21:9F5A), slot 3 (member base $0EFB) alive and knowing every spell ($0F9B..)
local SLOT3 = { [0x111F] = 3, [0x0F07] = 20, [0x0F0B] = 20, [0x0F2F] = 0 }
for a = 0x0F9B, 0x0FB1, 2 do SLOT3[a] = 0x0101 end
for a, v in pairs(THEO) do if a ~= 0x111F then SLOT3[a] = v end end
local TOWNS = {}
for a, v in pairs(SLOT3) do TOWNS[a] = v end
for a = 0x7FD01C, 0x7FD038, 2 do TOWNS[a] = 0x0101 end
-- Field menu (Y or B; X does nothing): magic, items, equip, status, config, direction; n = cursor row.
local function menu(n) return "6 y;40 -;" .. string.rep("6 down;14 -;", n) .. "6 a;90 -;6 a;90 -" end
-- Battles: $7FD796 = $FFFF starts one at the next field step ($0C:C018). Boss n: $7FD7B0 = $8000|n ($21:8000).
-- Normal: background $7FCE78, formation $7FCE7A ($21:80E2 rolls these for random encounters).
-- battle with Theo (all spells) and one of every item; Ralph's panel: down, A; commands cycle with right
local BPARTY = { [0x7FCE78] = 7, [0x7FCE7A] = 0, [0x7FD7B0] = 0x000E, [0x7FD796] = 0xFFFF }
for a, v in pairs(THEO) do BPARTY[a] = v end
for a = 0x0F3B, 0x0F59, 2 do BPARTY[a] = 0x0101 end
local function boss(n) return at(HOME, { pokes = { [0x7FD7B0] = 0x8000 | n, [0x7FD796] = 0xFFFF }, keys = "600 -" }) end
local function shop(mode, id) return at(HOME, { pokes = { [0x7FD7AE] = id or 0, [0x7FD7AC] = 0x8000 | mode }, keys = "300 -" }) end

SCENE_LIST = {
  -- boot and story
  intro = { intro = true, keys = "60 -" },             -- title, file select, the full intro crawl (~10k frames)
  opening = { keys = mash(12, 84) },                   -- new game: the school-room opening event
  -- story-so-far screen (shown when a save loads), piece n of 18 ($0C:DCC5 table); then the plain opening
  story00 = { story = 0 }, story01 = { story = 1 }, story02 = { story = 2 }, story03 = { story = 3 },
  story04 = { story = 4 }, story05 = { story = 5 }, story06 = { story = 6 }, story07 = { story = 7 },
  story08 = { story = 8 }, story09 = { story = 9 }, story10 = { story = 10 }, story11 = { story = 11 },
  story12 = { story = 12 }, story13 = { story = 13 }, story14 = { story = 14 }, story15 = { story = 15 },
  story16 = { story = 16 }, story17 = { story = 17 },
  home = HOME,
  worldmap = { map = 0x13A371, x = 0x2E, y = 0x80 },
  -- field menu
  menu = at(HOME, { keys = "6 y;90 -" }),
  menu_close = at(HOME, { keys = "6 y;90 -;6 b;120 -" }),           -- issue #1: no letters left after closing
  controller = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 down;14 -;6 down;14 -;6 down;14 -;6 a;90 -;" ..
    "6 down;20 -;6 down;20 -;6 down;20 -;6 right;30 -;6 a;150 -" }),  -- Config > Controller > Custom (issue #1)
  controller_b = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 down;14 -;6 down;14 -;6 down;14 -;6 a;90 -;" ..
    "6 down;20 -;6 down;20 -;6 down;20 -;6 right;30 -;6 a;150 -;6 down;60 -" }),  -- O.K./CANCEL move per mode (#3)
  controller_d = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 down;14 -;6 down;14 -;6 down;14 -;6 a;90 -;" ..
    "6 down;20 -;6 down;20 -;6 down;20 -;6 right;30 -;6 a;150 -;6 down;30 -;6 right;60 -" }),
  menu_down = at(HOME, { keys = "6 y;40 -;6 down;20 -;6 down;20 -;6 down;20 -;6 up;60 -" }),  -- bracket after moving (#3)
  menu_magic = at(HOME, { keys = menu(0) }),
  menu_item = at(HOME, { keys = menu(1) }),
  -- casters are party slots 1 and 3 ($21:9F05); party size $111F. Slot 1 (Theo, table E4) knows spell n when
  -- $0F6B + n-1 is nonzero (slot 3: $0F9B, F2), listed in the order of $21:B252. Here: Theo alive, all 23 spells.
  menu_magic_list = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 right;30 -;6 a;90 -", pokes = THEO }),
  -- cursor on Theo's 10th spell (Telepia $17, longest description 120 px)
  menu_magic_long = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 right;30 -;6 a;90 -;6 down;20 -;6 right;20 -;6 right;20 -;" ..
                                      "6 right;40 -", pokes = THEO }),
  menu_magic_whom = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 right;30 -;6 a;90 -;6 a;90 -", pokes = THEO }),  -- Refi -> on whom
  menu_magic_whom_back = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 right;30 -;6 a;90 -;6 a;90 -;6 b;90 -", pokes = THEO }),
  menu_magic_slot3 = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 down;30 -;6 right;30 -;6 a;90 -", pokes = SLOT3 }),
  -- Telepiam's town list: byte per town at $7FD01C + n (n < 30, $21:AD26), all set here
  menu_magic_town = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 down;30 -;6 right;30 -;6 a;90 -;6 a;90 -", pokes = TOWNS }),
  -- same, cursor right then down twice: scrolls one row (Pegasion Castle / Gaizen Town at the top), on St. Bacchus's right
  menu_magic_town2 = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 down;30 -;6 right;30 -;6 a;90 -;6 a;90 -;6 right;30 -;" ..
                                       "6 down;30 -;6 down;90 -", pokes = TOWNS }),
  telepiam_go = at(HOME, { keys = "6 y;40 -;6 a;90 -;6 down;30 -;6 right;30 -;6 a;90 -;6 a;90 -;6 right;30 -;" ..
                                  "6 down;30 -;6 down;90 -;6 a;400 -", pokes = TOWNS, nocheck = true }),  -- -> Polydos Town
  menu_item_full = at(HOME, { keys = menu(1), pokes = { [0x0F3B] = 0x0201, [0x0F3D] = 0x0403, [0x0F3F] = 0x0605,
                                                        [0x0F41] = 0x0807 } }),
  menu_item_list = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 a;90 -", pokes = { [0x0F3B] = 0x0201, [0x0F3D] = 0x0403,
                                                        [0x0F3F] = 0x0605, [0x0F41] = 0x0807 } }),
  -- inventory = one count byte per item id at $0F3B + id-1, listed in the order of $21:BFFB.
  -- Longest item name (Mystic Mushroom $20, 88 px) and description (Remote Control $11, 136 px).
  menu_item_long = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 a;90 -",
                              pokes = { [0x0F5A] = 0x0001, [0x0F4B] = 0x0001 } }),
  menu_item_long2 = at(HOME, { keys = "6 y;40 -;6 down;14 -;6 a;90 -;6 right;40 -",
                               pokes = { [0x0F5A] = 0x0001, [0x0F4B] = 0x0001 } }),
  menu_equip =at(HOME, { keys = menu(2) }),
  menu_equip_info = at(HOME, { keys = menu(2) .. ";6 right;20 -;6 right;20 -;6 right;40 -;6 a;60 -" }),  -- pick the armour slot
  menu_status = at(HOME, { keys = menu(3) }),
  menu_config = at(HOME, { keys = menu(4) }),
  menu_direction = at(HOME, { keys = menu(5) }),
  -- field sub-modes ($7FD7AC, $10:81F6); shop id in $7FD7AE
  shop_sell = shop(1), shop_mode2 = shop(2), rename = shop(3), shop_weapon = shop(4), shop_armor = shop(5),
  shop_item = shop(6), church = shop(7), treasure_game = shop(8),
  shop_buy = at(HOME, { pokes = { [0x7FD7AE] = 0, [0x7FD7AC] = 0x8006, [0x111B] = 9999 },
                        keys = "300 -;6 a;120 -;6 a;120 -;6 a;120 -;6 a;120 -" }),  -- 9999 G, buy wares row 1
  church_save =at(shop(7), { keys = "300 -;6 a;300 -" }),           -- Save -> the record slots
  church_confirm = at(shop(7), { keys = "300 -;6 a;300 -;6 a;120 -;6 left;60 -" }),  -- "Record 1. ...?" on Yes
  church_confirm_no = at(shop(7), { keys = "300 -;6 a;300 -;6 a;180 -" }),        -- same, cursor on No (default)
  church_saved = at(shop(7), { keys = "300 -;6 a;300 -;6 a;120 -;6 left;20 -;6 a;600 -" }),  -- writes record 1 (SRAM)
  church_revive = at(shop(7), { keys = "300 -;6 down;20 -;6 a;300 -" }),
  name_entry = at(shop(3), { keys = "300 -;6 a;120 -" }),  -- rename: pick Ralph -> the character chart
  -- battles
  battle = { map = 0x13A371, x = 0x2E, y = 0x80, keys = "600 -",
             pokes = { [0x7FCE78] = 7, [0x7FCE7A] = 0, [0x7FD7B0] = 0x000E, [0x7FD796] = 0xFFFF } },
  battle_party = { map = 0x13A371, x = 0x2E, y = 0x80, keys = "600 -", pokes = BPARTY },
  battle_auto = { map = 0x13A371, x = 0x2E, y = 0x80, keys = "600 -;6 right;30 -;6 a;400 -",  -- AUTO: label fits
                  pokes = { [0x7FCE78] = 7, [0x7FCE7A] = 0, [0x7FD7B0] = 0x000E, [0x7FD796] = 0xFFFF } },
  battle_win = at(HOME, { pokes = { [0x7FD7B0] = 0x8000, [0x7FD796] = 0xFFFF }, god = true, stats = 255,
                          keys = mash(40, 114), nocheck = true }),
  gameover = at(HOME, { pokes = { [0x7FD7B0] = 0x8000, [0x7FD796] = 0xFFFF }, keys = mash(8, 114) }),
  boss00 = boss(0), boss01 = boss(1), boss02 = boss(2), boss03 = boss(3), boss04 = boss(4), boss05 = boss(5),
  boss06 = boss(6), boss07 = boss(7), boss08 = boss(8), boss09 = boss(9), boss10 = boss(10), boss11 = boss(11),
  boss12 = boss(12), boss13 = boss(13), boss14 = boss(14), boss15 = boss(15), boss16 = boss(16),
  -- ending: script $10:ED35 (world map -> shrine -> final boss ガルバ, ~2400 frames). STATS=255 still hits him
  -- for 1 (45k frames, no win), so the ending is reached by step instead:
  -- ending_lab = cutscene step 41 alone (the epilogue lab map $14:CC90), credits = step 42 (staff roll, play record)
  final_boss = at(HOME, { script = 0xED35, god = true, keys = mash(20, 144), nocheck = true }),
  ending_lab = at(HOME, { pokes = { [0x1C45] = 41 }, keys = "600 -", nocheck = true }),
  credits = at(HOME, { pokes = { [0x1C45] = 42 }, keys = "10500 -", nocheck = true }),
  village_event = at(HOME, { script = 0xEF23, keys = mash(16, 234), nocheck = true }),
  -- one per place name (doors.py --places: the map with the most doors in, at its first door's spawn)
  place01 = { map = 0x13A3A7, x = 0xE8, y = 0x4D },  -- アレイトスのやま
  place02 = { map = 0x13A3E4, x = 0x0A, y = 0x4E },  -- アレイトスのいえ
  place03 = { map = 0x13A435, x = 0x11, y = 0x1E },  -- ナクシュのむら
  place04 = { map = 0x13A529, x = 0x32, y = 0x1E },  -- マ―ゼンのむら
  place05 = { map = 0x13A65A, x = 0x51, y = 0x02 },  -- ガイゼンのまち
  place06 = { map = 0x13A7EA, x = 0x70, y = 0x1E },  -- ペガシオンのしろ
  place07 = { map = 0x13A9D2, x = 0x59, y = 0xF5 },  -- ゴブリンのねじろ
  place09 = { map = 0x13AA2A, x = 0xB8, y = 0x2E },  -- セント・バッカス
  place10 = { map = 0x13AC46, x = 0x68, y = 0x3E },  -- ようせいのもり
  place11 = { map = 0x13AD03, x = 0x1F, y = 0x1B },  -- カイザのとう
  place12 = { map = 0x13AD6F, x = 0x01, y = 0x2C },  -- ポリドスのまち
  place13 = { map = 0x13AEF1, x = 0x21, y = 0x2C },  -- ポリドスのまち
  place14 = { map = 0x13B045, x = 0x56, y = 0x3E },  -- ニュ―ポリドス
  place15 = { map = 0x13B255, x = 0x82, y = 0x16 },  -- たいようのほこら
  place17 = { map = 0x13B28B, x = 0x90, y = 0x1E },  -- デュ―サスのしろ
  place18 = { map = 0x13B442, x = 0x47, y = 0x08 },  -- さとりのとう
  place19 = { map = 0x13B50E, x = 0x8F, y = 0x2E },  -- サラディンのまち
  place20 = { map = 0x13B5E7, x = 0x0B, y = 0xBE },  -- なげきのどうくつ
  place21 = { map = 0x13B689, x = 0x91, y = 0x3E },  -- ポ―リ―のむら
  place22 = { map = 0x13B77C, x = 0x87, y = 0xA4 },  -- ちかすいどう
  place23 = { map = 0x13B81E, x = 0xB1, y = 0x3E },  -- コ―リ―のむら
  place24 = { map = 0x13B8C0, x = 0xC7, y = 0x3D },  -- サラディンのはか
  place25 = { map = 0x13B947, x = 0x20, y = 0x52 },  -- かなしみのとう
  place26 = { map = 0x13B9D5, x = 0x38, y = 0x04 },  -- セント・バッカス
  place27 = { map = 0x13BA5D, x = 0xE8, y = 0x9E },  -- あかずのほこら
  place29 = { map = 0x14C966, x = 0x55, y = 0x9D },  -- レジスティホ―ム
  place30 = { map = 0x14CA08, x = 0xE8, y = 0x5E },  -- りゅうのけっかい
  place31 = { map = 0x14CA23, x = 0x9E, y = 0x0D },  -- テュリオスのまち
  place32 = { map = 0x14CC24, x = 0x50, y = 0x6E },  -- ルネッサスのまち
  place33 = { map = 0x14CCAB, x = 0x33, y = 0x4E },  -- ゴナ―ルのまち
  place34 = { map = 0x14CDD4, x = 0x0C, y = 0x0E },  -- ギプロスのまち
  place35 = { map = 0x14CF9F, x = 0x47, y = 0x2D },  -- しんぷのまち
  place36 = { map = 0x14D20C, x = 0x41, y = 0x3F },  -- デナのさと
  place37 = { map = 0x14D31A, x = 0x08, y = 0x11 },  -- ミネアのむら
  place38 = { map = 0x13AF79, x = 0x96, y = 0x2B },  -- ポリドスのとう
  place39 = { map = 0x14D494, x = 0x10, y = 0x08 },  -- ジョシュアのしろ
  place40 = { map = 0x14D536, x = 0x70, y = 0x33 },  -- エスモのむら
  place42 = { map = 0x14D644, x = 0xB9, y = 0x4B },  -- ヴィクラムのむら
  place43 = { map = 0x14D7F4, x = 0xBF, y = 0x1B },  -- ヴィクラムのまち
  place44 = { map = 0x14D989, x = 0x88, y = 0x52 },  -- ゆうわくのたに
  place45 = { map = 0x14D9A4, x = 0xD6, y = 0x09 },  -- ゴ―ルドシティ
  place46 = { map = 0x14DB54, x = 0x6E, y = 0x2E },  -- とうぞくのやかた
  place47 = { map = 0x14DB8A, x = 0x78, y = 0x59 },  -- ファミルのむら
  place48 = { map = 0x14DC7D, x = 0x47, y = 0x06 },  -- ギプロスはいこう
  place49 = { map = 0x14DE63, x = 0x28, y = 0x04 },  -- バイロスはいこう
  place50 = { map = 0x14DF05, x = 0xCB, y = 0x4E },  -- バイロスのむら
  place51 = { map = 0x14E07F, x = 0x86, y = 0x04 },  -- ファミルはいこう
  place52 = { map = 0x14E106, x = 0x24, y = 0x52 },  -- まどいのどうくつ
  place53 = { map = 0x14E18D, x = 0x6C, y = 0x16 },  -- でんせつのとう
  place54 = { map = 0x14E1F9, x = 0xA8, y = 0x51 },  -- バスウのほらあな
  place55 = { map = 0x14E22F, x = 0x77, y = 0x2D },  -- タ―ナのしろ
  place56 = { map = 0x14E481, x = 0x47, y = 0x0F },  -- セントバディノン
  place57 = { map = 0x14E4ED, x = 0xF3, y = 0x4E },  -- ラポレのむら
  place58 = { map = 0x14E667, x = 0x84, y = 0x0C },  -- りゅうのどうくつ
  place59 = { map = 0x14E6D3, x = 0x0B, y = 0x3B },  -- さびれたやしき
  place60 = { map = 0x14E7C6, x = 0x8E, y = 0x37 },  -- デナのいせき
  place61 = { map = 0x14E8EF, x = 0x14, y = 0x6D },  -- ティジアのしろ
  place62 = { map = 0x14EB0B, x = 0x07, y = 0x7A },  -- プレシアンケ―ブ
  place64 = { map = 0x14EC85, x = 0x20, y = 0x3C },  -- トレンシアのしろ
  place65 = { map = 0x14ED78, x = 0x8C, y = 0x1A },  -- ギルディタウン
  place66 = { map = 0x14EEA1, x = 0xE8, y = 0x5E },  -- パンジェのほこら
  place67 = { map = 0x14EEBC, x = 0xC1, y = 0x56 },  -- りゅうのけっかい
  place68 = { map = 0x14EEF2, x = 0x48, y = 0x25 },  -- こうていのやかた
  place69 = { map = 0x13BA78, x = 0xE4, y = 0xBE },  -- ラ―ザのどうくつ
  place70 = { map = 0x14EF79, x = 0x9D, y = 0x3D },  -- レイデスのまち
  place71 = { map = 0x14F0BD, x = 0xAF, y = 0x11 },  -- ファミルのまち
  place72 = { map = 0x14F1E6, x = 0xD8, y = 0x09 },  -- ファミルのしろ
  place73 = { map = 0x14F3E7, x = 0x06, y = 0x59 },  -- まどいのどうくつ
}
