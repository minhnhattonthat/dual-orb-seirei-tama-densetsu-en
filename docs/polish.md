# Polish pass: deferred Minor review findings

Collected from reviewer reports (Critical/Important are fixed per batch). Apply line by line in one pass at the end.

## in-game layout
- Info line (shops, equip) is built as `{name}:{desc}` with no space after the colon ("Hat:Protects you..."); a
  space needs the builder that writes `$0200` changed (the colon is a code-inserted byte), and 232 px rechecked.
  (done: glyph $60 "：" = colon + space at the 3 bank-$01 builders and the equip template `$21:CFBA`; 5 descriptions
  trimmed to fit 232 px)

## names (b001-b006)
- E6:1A ためらいのつえ "Falter Staff": odd; maybe "Hesitation Staff". (skipped: info line 236 px > 232 in fieldfit)
- 3C6:03 says "gauntlet" for こて (glossary こて = Bracer); item is Gauntlet, fine either way. (skipped: fine as is)
- EC:28 こうりゅうかい "Koryukai": 交流会 = exchange society? check dialogue context. (skipped: no {tEC:28} use in any script, no context)
- EC:56 "Aww, mister customer!" clunky -> "Aww, customer~!". (done)
- EC:35 "Galba's minions" vs F9:61 "Peo's Minion": capitalisation. (skipped: EC:35 is a prose phrase, F9:61 a monster name; both right)
- F9:0F "Byakuoh", F9:24 "Wonoh": -oh spelling -> Byakuo / Wono. (done)
- 3C3:04 "Stops a foe's breath" -> "Finishes off a foe". (done)
- 3C4:04 "Escape for sure" -> "Always escapes". (done)
- 3C7:03 / 3C8:04 "with silk's mystic power" stiff -> "imbued with silk's mystic power". (skipped: info lines 234/253 px > 232)

## b012-b013
- 0F:AF71, 0F:B034 stiff "is needed to build" -> "People must look upon their own true selves. That is necessary to build a new world."; vocative "Great adventurers," with comma (also 0F:C00E). (done; comma also on 0F:97C8/9886/A41F/BC7A, 15:9EB3, 11:822C)
- 0F:B2FF join fragment "..., though {tEC:2E} doesn't have a single piece of them now." (done)
- 0F:B599 "If you want a cheap stay, come to this inn." (done)
- 0F:C00E "{tEC:2D} is hard to forgive, but I shall return him to you." (done)
- 0F:CB16, 0F:D4AB "wanna" -> "want to". 0F:CDFF "MY" caps. 0F:CEBB "live my youth again". (done)

## b014-b015
- 11:822C tenses -> present. 11:8A73 "doggy-chan" -> "Poor little doggy." 11:83FE "{tED:03}'s school". (done; 822C/8A73 already fixed)
- 11:8775 "Dragon Larzes is the Dragon who" -> write out "the dragon who". 11:E14D "good kid". (done: already fixed; E14D is 0F:E14D)
- 11:96BA "You can pay for your purchases here. Shall I ring you up?" 11:9AAC "the dragon's". 11:A887 "No, no, no! You're alive!" (done)

## b016-b024 (minors not sent with the fix round)
- 11:AE51 "let alone meeting {tEC:A7}"; 11:BED6 "flowing toward"; 11:D8FD "Stay safe."; 11:B101 "the bridge at {tED:05}". (done)
- 11:F17B "They attacked right in the middle of a party."; 12:91BC "You're from {tED:09}, aren't you?"; 12:8E30 kid joke. (done)
- 12:B233 Prince {tEC:1C} sentence; 12:CBA4 "yielded"; 12:EAE8 double "after all"; 12:E54F drop "together";
  12:E2C5 "summoned"; 15:8A56 "blood sacrifice"; 15:8FF8 "change any names?"; 15:9C92 "put up to it by"; 15:8DAD "almost always". (done)
- 12:C152 / C1A3 Basu's ice-melting thing is the Medal ({tE5:27} くんしょう): verify in game.

## system b007-b009
- ひっさつわざ: "Skill" (menu) vs "Deadly strike! 00!!" (battle): unify. 10:A15C/A168 optionally `Got "00"!`. (skipped: battle line is already "Ha! 00!!"; `Got "00"!` fails lint, 00 must stay at byte 1)
- 0C:E0F3 "planned to storm". 20:BD1A "The poison spread through 00!". 21:DD24 "(Gear)" vs "Equip". (done: 20:BD1A as "00 feels the poison spread!" (00 must lead), DD24 "(Equip)"; skipped E0F3: story page 188 cells > 180)
- Shop lines {tEC:6C}+{tEC:93} (11:96DF, 11:9F83, 11:D232): add "before you go" like 12:9373. (done; also 11:E294, same JP)

## b025-b028
- 15:AFF8 "Not yet.... I think not yet." 15:9EB3 "Trust between people - that is what a new world needs." (done)
- 15:BBFC "There's a rich town to the south, {tED:22}." 15:CAA6 no stutter. 15:BC5F silk-white pun. 15:BB39 "sell our local silk". (done; CAA6 fix on all 6 same-JP lines)
- 15:CB81 おやぶんさん -san dropped. 15:F7D5 "Good, an obedient one." 15:ED82 "Got it." (done; CB81 also 15:CBAD; skipped ED82: dropping the {tE5:0B} name token fails lint)
- {tEC:03} inserts "Dragon" (capital) vs "dragon" in prose: accept or write out. (skipped: accepted, reads as a title)
