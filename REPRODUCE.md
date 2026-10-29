# How this repository was made (Micronesia)

This file is written by the build on 2026-10-29, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| FSM Legal Information System: Constitution pages and Code of the FSM 2014 Edition (Annotated) title PDFs | <https://www.fsmlaw.org/fsm/code/indexcode2014.html> | 2026-10-29 | 52 | no licence stated; unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication |
| Congress of the Federated States of Micronesia: public laws (17th-24th Congress indexes and enrolled PDFs) | <https://www.cfsm.gov.fm/fsm-congress-public-laws/> | 2026-10-29 | 24 | official public laws of the FSM; no licence stated |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `title-11-crimes` | Code of the Federated States of Micronesia, Title 11: Crimes | 6 | 2012-03-16 to 2020-07-20 |
| `title-07-citizenship` | Code of the Federated States of Micronesia, Title 7: Citizenship | 3 | 2012-06-06 to 2024-12-11 |
| `constitution` | Constitution of the Federated States of Micronesia | 1 | 2003-06-08 to 2003-06-08 |

The build made 10 commits:

| Commits | Kind |
| ---: | --- |
| 3 | first version of an act |
| 7 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-29.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 16 laws in the record.
- 17 tags.

## Dates

Each commit is dated at noon (Pacific/Pohnpei) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Every public law applied here ends "This act shall become law upon approval by the President of the Federated States of Micronesia or upon its becoming law without such approval" (Constitution art. IX, sec. 22); it is dated by the day the FSM Congress public-law index gives for it, which is the approval day printed on the law, or the day it became law without signature. https://www.cfsm.gov.fm/fsm-congress-public-laws/

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-29
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-29 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/micronesia-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `400721dc89c53748323aec228501fc33b4518b1413b4403bf09bf5b48f24f229` (432002 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `2bfc4ac9df193a7be844556d7f69cdb9d93ec3f2` |
| check.py | `cd346c7ff9996d450240e3bab52bcae03b2bc865` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `6363317b359f9910c5ea9cca4a816feaaa8ad556` |
| parse.py | `0a98d03de3aec05e440fa5bb0b859e2bfe7067d7` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

9 versions of 2 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

A second build from the same corpus into an empty folder gave identical hashes for all 10 history commits and 17 tags (history tip `f32e4e6a6308681b903904e8b68e2ceb06ce8f2c`).

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- English is the language of the FSM Code and Constitution; the text is built in English.
- Code of the FSM 2014 Edition: the edition sets statutory text in 12 pt and every annotation (Source notes, editor's notes, cross references, case annotations) in 10 pt; only 12 pt text is kept (PyMuPDF). The Source notes are used only to date the first version and to list earlier laws.
- Unit files: one per section (sec-NNNN, the code section number), one per chapter, subchapter and part heading; text is one paragraph per line, with quotes, dashes and spaces normalised.
- Public laws are read with pdftotext 4.00 (poppler) -layout; printed line numbers, page headers and bill draft marks are removed, and the quoted text after "to read as follows:" becomes the section, whole. Their "Section N." headings are written in the Code's "§ N." form.
- PL 18-43 section 3 says it inserts "a new section 631" but quotes "Section 632. Definition."; it is applied as section 632, as quoted. Its section 6 rewrites section 104 without repeating the catchline, so the catchline "Definitions." is kept.
- PL 18-43 prints no approval date (it became law without the President's signature); its date, 7 March 2014, is the FSM Congress index's.
- PL 21-08 section 2 quotes a new section 1141 that ends at the closing quotation mark after subsection (2)(d); a further paragraph "(1) Notwithstanding subsection (2)(c) ..." printed after the closing quotation mark is not applied, and the duplicated sentence and stray quotation mark inside the quoted text are kept as printed.
- PL 19-91 rewrites section 203 of title 7 as "Section 203. A citizen ..." with no catchline, so the file heading reads "§ 203." with no catchline until PL 23-140 gives it one.
- Unnumbered paragraphs inside a public law's quoted section are joined into one line: the enrolled PDFs do not mark paragraph breaks other than by enumerators.
- Constitution: one version, the oldest available (first_law null), credited to the FSM Legal Information System: unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication. It is the text the LIS prints with the four amendments of the 1990 Constitutional Convention (Proposals 90-13, 90-19, 90-23 and 90-25, ratified by the voters in 1991) incorporated, as the LIS index page says. The LIS gives no ratification date, so the version is dated 2003-06-08: by that day the Internet Archive had captured every page of it, and the newest captures (2023-2024) carry the same words.
- Constitution: the amendments put to the July 2023 referendum (eight from the 4th Constitutional Convention and one from the 22nd Congress, among them dual citizenship in Article III) are NOT applied. The LIS pages captured up to 2024 do not incorporate them, the convention site (constitution.gov.fm) no longer serves its adopted proposals, and no official certified text with its ratification date was found. Public Law 23-140 (2024) refers to "the dual citizenship constitutional amendment", so Article III as built is out of date after 2023.
- Constitution: case annotations and cross references (set in a smaller font by the LIS) are left out; one file per section, plus one per article heading and the preamble.
- Title 11: the first version is the 2014 Edition text (unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication), first_law null. The edition states no cut-off date, so it is dated 2012-03-16, the day PL 17-38 became law (FSM Congress index), PL 17-38 being the latest public law named in the edition's Source notes for this title; no public law amending the title between that day and the next one applied here appears in the Congress index.
- Title 7: the first version is the 2014 Edition text (unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication), first_law null. The edition states no cut-off date, so it is dated 2012-06-06, the day PL 17-54 became law (FSM Congress index), PL 17-54 being the latest public law named in the edition's Source notes for this title; no public law amending the title between that day and the next one applied here appears in the Congress index.
- The Constitution is kept in corpus.d/10-constitution.json without a .PUBLISH file, so it builds to preview only: the July 2023 referendum amendments (at least Article III, dual citizenship) are known to be missing from its text, and no official text of them has been found. It moves to main once they are applied and verified.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code with Claude Opus 5.5 (claude-opus-5-5) wrote discover.py, fetch.py, layout.py and parse.py and chose the sources and acts; it did not write or alter any legal text. parse.py is deterministic and runs no model; every line of law comes from a cached source file.
