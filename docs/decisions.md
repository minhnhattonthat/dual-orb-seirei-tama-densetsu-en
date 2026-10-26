# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-27 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-10-27 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-27 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-27 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default); abbreviate only as a flagged last resort. |
| D5 | 2026-10-27 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners); leave the Japanese logo only if it has no official English version. |
| D6 | 2026-10-27 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint; phase per session, commit + push to main at each phase end. Never `gh release create`, never change repo visibility. |
| D7 | 2026-10-27 | Existing saves/savestates | user saves, none | None provided; build the debug tool. |
