Dual Orb: Seirei Tama Densetsu (SNES) - English Translation v{VERSION}
=====================================================================

An unofficial fan translation of I'MAX's 1993 Super Famicom RPG
"Dual Orb: Seirei Tama Densetsu" into English.

Translated:
- All story dialogue, the intro crawl, the story-so-far recaps and the credits.
- Item, spell, monster and place names, descriptions, shops, menus, the church,
  save/load, battle messages and the battle command buttons (ATTACK/AUTO/FLEE).
- The name entry screen, now with an English alphabet chart.

A variable-width font replaces the Japanese text, and the ROM is expanded to
2 MiB to make room for the English.

Applying the patch
------------------
Apply DualOrb_EN_v{VERSION}.bps to an unmodified, unheadered dump with Flips,
Beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).

Base ROM: Dual Orb - Seirei Tama Densetsu (Japan).sfc (No-Intro), 1,572,864 bytes
  {BASE}
Patched ROM: 2,097,152 bytes
  {PATCHED}

If your file is 1,573,376 bytes it has a 512-byte copier header: remove it first.

Notes
-----
- Tested in Mesen 2.2.1. Start from a fresh boot: save states made with the
  Japanese game carry the old text engine. Battery saves made with the
  Japanese game are untested.

Known issues
------------
- A menu description can show one garbled letter for a single frame while it
  redraws after the cursor moves.

Credits
-------
Translation, hacking and tools: minhnhattonthat, with AI assistance (Anthropic
Claude).

Bug reports: https://github.com/minhnhattonthat/dual-orb-seirei-tama-densetsu-en/issues

This is an unofficial fan work, not affiliated with I'MAX.
Do not distribute pre-patched ROMs.
