# Dual Orb: Seirei Tama Densetsu English translation

Unofficial English fan translation of **Dual Orb: Seirei Tama Densetsu** (Super Famicom, I'MAX, 1993): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/dual-orb-seirei-tama-densetsu-en
cd dual-orb-seirei-tama-densetsu-en
# copy your dump to: rom/Dual Orb - Seirei Tama Densetsu (Japan).sfc
#   (1572864 bytes, SHA-1 25fe4c1af89a7d09ffefab7d568d15865f153467; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/dual_orb_en.sfc (VWF asm needs asar 1.91 in tools/asar/)
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is I'MAX's and is included only so
the translation can be checked against it. Dual Orb: Seirei Tama Densetsu is (c) 1993 I'MAX; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
