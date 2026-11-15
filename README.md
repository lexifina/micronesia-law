# Micronesia: law history in git


The law of the Federated States of Micronesia as a git history: one file per section of the Code (and one per public law), one commit per version on the day it took effect, and the public law that made each change to the Code as the commit's author. `git blame` names the law behind every line; `git log` lists every change to a section; picking a date gives the text in force that day.

Part of [lexifina/global-law](https://github.com/lexifina/global-law), one git history for every country's law: this is Micronesia's national law, which global-law reads at `micronesia/national/acts/`.

**What is in it now:** two titles of the Code of the Federated States of Micronesia, title 7 (Citizenship, 3 versions from 2012 to 2024) and title 11 (Crimes, 6 versions from 2012 to 2020); and 321 public laws of the 10th to the 24th Congress (1997 to 2026), each as enrolled, in one version. [`REPRODUCE.md`](REPRODUCE.md) lists every act with its versions; [`data/laws.csv`](data/laws.csv) lists the public laws in the two titles' histories, with the day each change took effect.

Each Code title is a folder with one file per section and per chapter heading (`title-07-citizenship/sec-0203.md` is section 203 of title 7); each public law is a folder holding one file, `whole-act.md` (`public-law-23-140/whole-act.md` is Public Law No. 23-140, which rewrote section 203 in 2024). Each folder's `README.md` lists its provisions and their changes.

The text is in English, as the Code's 2014 Edition and the Congress's enrolled PDFs print it: the Edition's annotations are left out, and each enrolled law keeps its printed lines, with their line numbers, running headers and signature blocks.

## Questions as git commands

| Question | Command |
| --- | --- |
| Every change to section 203 of title 7 (Citizenship) | `git log -p --word-diff -- title-07-citizenship/sec-0203.md` |
| Which law wrote each line of section 203? | `git blame title-07-citizenship/sec-0203.md` |
| Every version of title 7, with the day each took effect | `git log --format="%h %(trailers:key=In-force,valueonly,separator=) %an" -- title-07-citizenship ':!*/README.md'` |
| Section 203 as in force on 1 January 2020 | `python tools/on.py 2020-01-01 title-07-citizenship 203` |

**Outside git**, we also host this record publicly, for free:

- **[Ask Claude about Micronesian law](https://global-law.lexifina.com/v1/try_claude?country=micronesia)**: opens Claude with a first question ready.
- **[Ask ChatGPT](https://global-law.lexifina.com/v1/try_chatgpt?country=micronesia)**: the same question in ChatGPT.
- **[Call the API in your browser](https://global-law.lexifina.com/v1/search_law?query=citizenship&jurisdictions=micronesia)**: a search of Micronesian law for "citizenship", returned as JSON. See the [documentation here](https://lexifina.com/api/global-law).

Both assistants read the record through the free Global law connector (MCP, `https://global-law.lexifina.com/mcp`); the first time, the chat gives you the link that adds it. Ask in English.

**Host it yourself easily.** All it takes is git and Python, and the tools run on your machine:

```sh
git clone --depth 1 https://github.com/lexifina/global-law && cd global-law
python3 tools/countries.py add micronesia/national/acts
python3 tools/law.py show 2026-01-01 micronesia/national/acts/title-07-citizenship/sec-0203.md
```

Opened in Claude Code, Cursor, VS Code or Codex, the clone also starts a local MCP server with the same tools ([MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md)).

## Dates

Each commit is dated at noon, Pacific/Pohnpei, on the day the version took effect, and carries it in its `In-force:` trailer:

- for a public law, the day it became law on the President's approval, or without it (Constitution art. IX, sec. 22), as the enrolled PDF or the Congress's listing gives it; two are dated by the day Congress overrode a veto;
- the 2014 Edition states no cut-off date, so each title's first version is dated by the latest public law its source notes name: 16 March 2012 (PL 17-38) for title 11 and 6 June 2012 (PL 17-54) for title 7;
- 23 public laws of the 10th, 12th, 13th and 14th Congress, whose day the sources do not establish, are dated 3 November 2026, the day they were retrieved, and their commit messages say so; a session's date range is never used;
- the public laws were added in batches, so `main` is not in date order: ask for a date with `tools/on.py`, which reads `In-force:`, not with `git log --before`.

Each change to a Code title is credited to the public law that made it (`PL 23-140`), and the 2014 Edition text to `FSM Legal Information System (unofficial)`. Each enrolled public law is the oldest version available, credited to its publisher, `Congress of the Federated States of Micronesia`.

## How it is checked

- `tools/check_repo.py` reads every version back from git on the day it took effect, and on the day before, and compares it file by file with the corpus it was built from; it also checks that every commit's trailers parse and that `main` has no merge commits.
- Each enrolled law's words, in order, are compared with a second reading of the official PDF by a separate extraction engine, after whitespace is normalised.
- [`REPRODUCE.md`](REPRODUCE.md) gives the corpus and builder hashes; its Checks section reads "Not yet run for this build".
- History is append-only: `tools/append.py` adds new acts and versions on top, and no published commit is rewritten.

## What it does not show

- **The Constitution.** The text available lacks the amendments put to the July 2023 referendum, so it is held on the `preview` branch, not on `main`.
- **Most of the law.** Only titles 7 and 11 of the Code; no other title, no state law, no regulations and no case law.
- **Public laws applied to the Code.** The 321 public laws are as enacted; what they change in other titles or in earlier public laws is not consolidated.
- **Every public law.** Laws the Congress's listing marks as later amended, laws with an uncertain or conflicting day or a conditional effect, and laws whose two PDF readings differ are left out; none of the 11th Congress is here.
- **The official text of the Code.** The 2014 Edition is an unofficial consolidation; its disclaimer says the copies "are not to be construed as an official publication".

## Sources

| Source | Kind | Past versions | Notes |
| --- | --- | --- | --- |
| [FSM Legal Information System](https://www.fsmlaw.org/fsm/code/indexcode2014.html) (under the FSM Supreme Court) | Unofficial consolidation: Code of the FSM, 2014 Edition (Annotated) | no, one edition | Titles 7 and 11, read from Internet Archive captures; statutory text only |
| [Congress of the Federated States of Micronesia](https://www.cfsm.gov.fm/fsm-congress-public-laws/) | Official enrolled public laws (PDF) and their listings | no, each law as enacted | The public laws, the amendments applied to titles 7 and 11, and the day each became law |

## Licence

See [`LICENSE`](LICENSE). Neither source states a licence; the texts are reproduced with attribution, and their copyright status is not confirmed. Lexifina's own contributions (the history, commit messages, tables and tools) are CC0 1.0.

No AI model wrote or changed legal text; the scripts were written by AI models (see [`REPRODUCE.md`](REPRODUCE.md)).

## More

From [lexifina/global-law](https://github.com/lexifina/global-law):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): every feature, and what every corpus must support (`git blame`, `law.py`, the MCP tools)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): questions and answers · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): proposing changes · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): the MCP server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): how it was built · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): how current each corpus is · [Monitoring](https://github.com/lexifina/global-law/tree/main/monitoring): whether updates are running · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): how each official source is watched for changes
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): how fast the tools are, measured
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): charts and bridges across the world's law
- [Vulnerabilities](https://github.com/lexifina/global-law/tree/main/vulnerabilities): mistakes in legislation as published
