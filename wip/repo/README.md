# Federated States of Micronesia: law history in git

The law of the Federated States of Micronesia (FSM) as a git history: one file per provision, one commit per public law on the day it became law, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to a section; `tools/on.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `fm/`.

> **Unofficial base text.** The Constitution and the 2014 Code text here come from an unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication. Its disclaimer says the copies "are not to be construed as an official publication". No official consolidation of the FSM Code or Constitution is online, and none of the Code exists after the 2014 Edition. The changes made after 2014 come from the official public laws published by the FSM Congress. The Lexifina user chose to build on this basis on 29 October 2026; until then this repository was paused for that reason.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the Federated States of Micronesia (1979) | 1 | The text the FSM Legal Information System prints, with the four 1990 Constitutional Convention amendments (ratified 1991) incorporated: oldest version available, dated 8 June 2003. **The July 2023 referendum amendments are not applied:** see below |
| `title-11-crimes/` | Code of the FSM, Title 11: Crimes | 6 | The 2014 Edition (Annotated), dated 16 March 2012; then PL 18-02 (chapter 13, Chemical Weapons, 14 June 2013), PL 18-19 (chapter 14, Laser Pointers, 14 October 2013), PL 18-43 (§ 104 and subchapter III of chapter 6, Registration of Deportees, 7 March 2014), PL 21-08 (§§ 1141, 1147, 5 July 2019) and PL 21-149 (§ 803, 20 July 2020) |
| `title-07-citizenship/` | Code of the FSM, Title 7: Citizenship | 3 | The 2014 Edition (Annotated), dated 6 June 2012; then PL 19-91 (§ 203, 14 June 2016) and PL 23-140 (§§ 202, 203, 204, 206, 11 December 2024) |

Each folder's `README.md` lists every provision, how often it changed and when. Files: `constitution/art-09-sec-02.md` is Article IX, Section 2; `title-11-crimes/sec-1141.md` is 11 F.S.M.C. 1141; `ch-06-sub-03.md` is the heading of chapter 6, subchapter III.

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did 11 F.S.M.C. 803 say on 1 January 2020? | `python tools/on.py 2020-01-01 title-11-crimes sec-0803` |
| Which law gave § 203 of title 7 its wording on a date | `python tools/on.py --law 2020-01-01 title-07-citizenship sec-0203` |
| The whole of title 11 on a date | `python tools/on.py 2015-01-01 title-11-crimes` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2020-01-01T23:59:59Z" main -- title-11-crimes/sec-0803.md):title-11-crimes/sec-0803.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2020-01-01T23:59:59Z" main -- title-11-crimes/sec-0803.md; git show "$($r):title-11-crimes/sec-0803.md"` |
| Which law wrote each line of § 1141? | `git blame title-11-crimes/sec-1141.md` |
| Every change to § 203 of title 7, word by word | `git log -p --word-diff title-07-citizenship/sec-0203.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one public law changed | `git show law/pl-18-043` (tags `law/<key>` mark each law's commit) |

After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Pacific/Pohnpei, on the day the change took effect**. The in-force day is also in the `In-force:` trailer, which the tools read.
- **Public laws.** Every public law applied here ends "This act shall become law upon approval by the President of the Federated States of Micronesia or upon its becoming law without such approval" (Constitution art. IX, sec. 22). Each is dated by the day the FSM Congress public-law index gives for it, which is the approval date printed on the law, or the day it became law without signature (PL 18-43 prints no date: the index gives 7 March 2014).
- **The 2014 Edition** states no cut-off date (its Introduction is not online). Each title's first version is therefore dated by the latest public law the edition's own "Source:" notes name in that title: PL 17-38 (16 March 2012) for title 11 and PL 17-54 (6 June 2012) for title 7. The FSM Congress index shows no public law amending either title between that day and the next law applied here. The edition is older than its name suggests: it does not include PL 18-02 of June 2013.
- **The Constitution** has no dated history online. Its one version is dated 8 June 2003, the day by which the Internet Archive had captured every one of its 17 pages on fsmlaw.org; the newest captures (2023-2024) carry exactly the same words. The text was in force on that day as printed; it may have been in force from the 1991 ratification, which the source does not date.
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`. The repository is rebuilt a second time from the same data and gives identical hashes.
- Health checks: no merge commits on `main`, commit dates never go backwards, nothing dated in the future, and every commit's trailers parse with `git interpret-trailers --parse`.
- **Against a second rendering** (`tools/verify.py`, 29 October 2026): every paragraph of the 2014 Edition text of both titles (1,451 paragraphs in 246 sections), read from the title PDFs, appears word for word in the FSM Legal Information System's separate per-chapter HTML of the same edition (Internet Archive captures of July 2016). Every paragraph applied from a public law (206) appears word for word in the enrolled law's PDF read with a second extractor (PyMuPDF; parse.py reads it with pdftotext). 0 misses.
- **Constitution:** for each of its 17 pages, the newest and the oldest Internet Archive captures (2002-2003 and 2023-2024) carry identical law text; parse.py stops if they ever differ.

## What "author" means

The author of a commit is the public law that made the change, with an e-mail address that cannot exist (`pl-18-043@fsmlaw.org.invalid`), so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- **The first commit of each act** is the oldest text available, credited to the publisher, the FSM Legal Information System (marked unofficial), and names the public laws the edition's Source notes list.
- **Credits come only from the sources.** Each later public law is credited with exactly the sections it enacts or rewrites "to read as follows".
- Blame credits whole lines (one paragraph per line). Use `git log -p --word-diff` to see which words each change made.

## What it does not show

- **The Constitution's 2023 amendments.** In July 2023 the voters were asked to approve nine amendments (eight from the 4th FSM Constitutional Convention and one from the 22nd Congress), among them dual citizenship (Article III, sections 3, 4 and 6). PL 23-140 of 2024 refers to "the dual citizenship constitutional amendment", so at least that one passed. The FSM Legal Information System's pages do not incorporate any of them, the convention's site (constitution.gov.fm) no longer serves its adopted proposals, and no official text with a certified result and date was found. They are **not applied**: `constitution/` is the pre-2023 text, and Article III and any other amended provisions are **not the law in force** after July 2023.
- **The Constitution before the LIS text.** The 1979 text as ratified and the four 1990 Convention proposals' effect cannot be shown as separate versions: the LIS prints only the amended text.
- **Annotations.** Source notes, editor's notes, cross references and case annotations are left out (they are not law text). The tables of contents of each chapter are left out.
- **PL 21-08, § 1141.** The enrolled law quotes the new section up to a closing quotation mark after subsection (2)(d) and then prints a further paragraph, "(1) Notwithstanding subsection (2)(c) ...", outside the quotation. Only the quoted text is applied, so `sec-1141.md` has no subsection (3) from 5 July 2019; the quoted text's duplicated sentence and stray quotation mark are kept as printed.
- **PL 19-91** rewrote § 203 of title 7 with no catchline, so from 14 June 2016 the file heading reads "§ 203." until PL 23-140 gives it one. PL 18-43 says "section 631" twice; the second quotes "Section 632" and is applied as § 632.
- **Other titles.** Only titles 7 and 11 of the Code's 58 are here so far. The same method (2014 Edition plus Congress public laws) applies to the others.
- **State law** (Chuuk, Kosrae, Pohnpei, Yap) is not included.

## How it is built

`tools/discover.py` pins the Internet Archive captures and the Congress URLs in `sources.json`. `tools/fetch.py` downloads each source once with curl into a cache named by the sha256 of the URL: fsmlaw.org only through archive.org (its robots.txt sets a 30-second crawl delay, and the site itself was never requested), cfsm.gov.fm directly at no more than 3 requests a second. `tools/layout.py` reads the 2014 Edition PDFs with PyMuPDF (statutory text is set in 12 pt, annotations in 10 pt), the Constitution pages by their font sizes, and the public laws with pdftotext; `tools/parse.py` writes `corpus.json`; the shared builder `tools/build.py` turns that into the commits. `REPRODUCE.md` lists every source, command, tool version and decision, and the result of the hash-for-hash rebuild.

## Sources

| Source | What | Dated versions | Names the amending law | Licence | Notes |
| --- | --- | --- | --- | --- | --- |
| [FSM Legal Information System](https://www.fsmlaw.org/fsm/code/indexcode2014.html) | Code of the FSM 2014 Edition (Annotated), per title PDF and per chapter HTML; Constitution pages | no | yes ("Source:" notes) | none stated | Unofficial consolidation published by the FSM Legal Information System under the FSM Supreme Court; not an official publication. Read through Internet Archive captures |
| [Congress of the FSM](https://www.cfsm.gov.fm/fsm-congress-public-laws/) | Public laws, 10th-24th Congress, as enrolled PDFs with a text layer; index with dates | yes (one per law) | yes | none stated | Official. Its code index page is empty |

See `LICENSE` for the attribution.
