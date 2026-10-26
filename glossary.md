# Glossary - Dual Orb: Seirei Tama Densetsu (SNES, I'MAX 1993)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces every row with katakana/kanji JP (whole-run match) and the Avoid column.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ralph-san, Larzes-sama). Name order: Western (D1).
- Romanisation source: no official English release and no earlier patch, so katakana names get the natural English
  or Latin-looking spelling the katakana suggests (ラルフ -> Ralph); Japanese words in Hepburn without macrons (D2).
- Credits: English (D3).
- Register: plain modern English fantasy, light; old men and royalty a bit formal; no Ye Olde, no modern slang.
- Abbreviations: none. Full names and terms; engine work before shortening (D4).

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...', ・・・ / … -> `...`, ！？ -> `!?`, ～/~ (drawn-out) -> repeat letters or `~`.
- Dialogue is wrapped to the box by `tools/wrap.py`; write each page as running text, `{fe}` between pages.
- Name tokens (`{hero0}`, `{tEC:0C}`) insert a name the game draws: keep them, never write the name instead; no a/an
  or plural/possessive tricks that break if the name changes (`{hero0}'s` is fine).
- `{hero0}たち` = "{hero0} and the others" / "{hero0}'s party" / "you all", whatever reads best.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ラルフ | Ralph | | hero, default name (party slot 0, `{hero0}`) | |
| テオ | Theo | | party slot 1 (`{hero1}`) | |
| リズ | Liz | | party slot 2 (`{hero2}`) | |
| ルミエス | Lumies | | party slot 3 (`{hero3}`) | |
| ラ―ゼス | Larzes | | legendary dragon, gives the mission | |
| ガルバ | Galba | | underground ruler; spoiler: really Larza | |
| ラ―ザ | Larza | | father of Ralph and Liz (late reveal) | |
| ゴ―リア | Goria | | destroyed St. Bacchus | |
| ギ―タ― | Gieter | | one of the Six Generals | |
| ガッシュ | Gash | | one of the Six Generals | |
| バディッシュ | Badish | | Dish brothers | |
| ラディッシュ | Radish | | Dish brothers | |
| エイゼル | Eizel | | one of the Six Generals | |
| ソ―ン・ジ―ナ | Thorn Gina | | one of the Six Generals | |
| サラディン | Saladin | | legendary hero of the past | |
| ディグバディノン | Digbadinon | | dragon of the underground | |
| バディノン | Badinon | | | |
| マテスン | Matteson | | resistance member | |
| ゴ―レムしんぷ | Father Golem | | priest | |
| リンダ | Linda | | | |
| テレサ | Teresa | | | |
| コスタリアン | Costarian | | | |
| アルペジ―ノ | Arpeggino | | | |
| サラ | Sara | | | |
| ゴブリン | goblin | | | |
| ペオ | Peo | | thief who stole the Fairy Key | |
| マリ | Mari | | | |
| リサ | Lisa | | | |
| ポンタ | Ponta | | dog | |
| ブルモア | Brumore | | ブルモア1せい = Brumore I | |
| フェニックス | Phoenix | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| アレイトス | Aleitos | | Mount Aleitos, Aleitos's house | |
| ポリドス | Polydos | | | |
| セント・バッカス | St. Bacchus | | | |
| デュ―サス | Dusas | | | |
| ペガシオン | Pegasion | | | |
| ガイゼン | Gaizen | | | |
| ジョシュア | Joshua | | | |
| ナクシュ | Nakush | | village | |
| マ―ゼン | Marzen | | village | |
| カイザ | Kaiza | | Kaiza Tower | |
| ニュ―ポリドス | New Polydos | | | |
| ポ―リ― | Polly | | village | |
| コ―リ― | Colly | | village | |
| レジスティホ―ム | Resisty Home | | resistance hideout | |
| テュリオス | Tyrios | | town | |
| ルネッサス | Renessas | | town | |
| ゴナ―ル | Gonar | | | |
| ギプロス | Gipros | | | |
| デナ | Dena | | | |
| ミネア | Minea | | | |
| エスモ | Esmo | | | |
| ヴィクラム | Vikram | | | |
| ゴ―ルドシティ | Gold City | | | |
| ファミル | Famil | | | |
| バイロス | Byros | | | |
| バスウ | Basu | | | |
| タ―ナ | Tarna | | | |
| セントバディノン | St. Badinon | | | |
| ラポレ | Rapole | | | |
| ティジア | Tizia | | | |
| プレシアンケ―ブ | Precian Cave | | | |
| トレンシア | Trencia | | | |
| ギルディタウン | Gildy Town | | | |
| レイデス | Reides | | | |
| こうていのやかた | Emperor's Mansion | | | |
| パンジェのほこら | Panje Shrine | | | |
| place suffixes | のむら Village, のまち Town, のしろ Castle, のとう Tower, のどうくつ Cave, ちほう Region, はいこう Old X Mine, のさと Hamlet, のほこら Shrine, のやかた Mansion | | in prose free ("the town of Gaizen") | |
| ちかせかい | underground world | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| パンジェ | Panje | | the source of evil (several to seal) | |
| ろくましょう | Six Generals | | | |
| オ―ブ | Orb | | | |
| ドラゴン | dragon | | "Dragon Larzes" when a title (ドラゴン・ラーゼス) | |
| ラ―ゼスのひかり | Light of Larzes | | key item | |
| スチ―ムマシン | Steam Machine | | | |
| トロッコ | Trolley | | | |
| リモコン | Remote Control | | | |
| セラミック | Ceramic | | | |
| いのりのしょ | Book of Prayer | | | |
| ようせい | fairy | | ようせいのX = Fairy X | |
| ラッキ―ラッキ― | Lucky Lucky | | Gold City gambling hall | |
| シャッフルゲ―ム | Shuffle Game | | | |
| ちていじん | underground folk | | ちじょう = surface world | |
| しっと / よくぼう / きょえい | Jealousy / Greed / Vanity | | Panje types | |
| spell families | heal Refi/-a/-zia/-am/-ziam; fire Flame/Flama/Flamazia/Flamam/Flamaziam; Sadre..; Brez..; Verifi..; Shield/Deshield, Saraud/Desaraud, Nimble/Denimble, Sleep, Confuse, Telepia | | names.json E4/F2 | |
| equipment | かわ/レザー Leather, てつ Iron, きぬ Silk, ダイヤの Diamond, ましょうの Demon, ドラゴン/りゅうの Dragon; ふく Garb, よろい Armor, かぶと Helm, たて Shield, こて Bracer | | names.json E6-EA | |

## Decisions from earlier batches
- `{tEC:13}・{tEC:14}` -> "{tEC:13} and {tEC:14}" (Dish brothers).
- Knights as a group: "the knights of Joshua" written out ({tEC:4B} is the singular "Knight of Joshua").
- サラディンゆかりのしなじな -> Saladin's relics. ジョシュアのきしだん -> Knights of Joshua. しさい high priest, しんぷ priest.
- ブタ・ブタ・ブタ / トラ・トラ・トラ password: b027 "Pig, pig, pig" / "Tiger, tiger, tiger"; b010-b014 used
  "Tora, Tora, Tora" -> unify in polish.
- さいだいTP -> max TP.
- Item names never possessive (they follow "the"): Sword / Garb / Shield of Saladin, Light of Larzes.
- Passwords: ブタ・ブタ・ブタ "Pig, pig, pig", トラ・トラ・トラ "Tiger, tiger, tiger" (must match everywhere).
- "Dragon Larzes" is a title: no article ({tEC:03} {tEC:01}, never "the {tEC:03} {tEC:01}").
