# 24 - Who curates item-unique crafting data (research for #24, parent #6)

Question: who can curate item-unique data (unique augment systems, multi-slot items, double-Mythic ToEE items, 4-option ring Reaper) that the wiki holds only as prose, and how do comparable projects take contributions? Feeds a maintainer-only vs community-contributed decision (ADR 0007 deferred it). Method: MediaWiki API on ddocompendium.com and the GitHub API/raw files of Maetrim/DDOBuilderV2, run 2026-09-23. ddowiki.com was not fetched (WAF, ADR 0006).

## 1. Is there a structured or community-maintained source?

| # | Finding | Source | Confidence |
|---|---|---|---|
| 1 | DDO Compendium is MediaWiki 1.43.5, licence CC BY-SA 4.0, ~32k articles, 9 admins, 2 active users. Search for "Mythic Reaper ring" returns only update notes, so unique-item crafting data is not evidently in a structured form there. Item pages were not sampled. | https://ddocompendium.com/api.php?action=query&meta=siteinfo&siprop=statistics\|rightsinfo | High on licence/size; low on item coverage |
| 2 | Maetrim DDOBuilderV2 is the only structured source found: 8,779 `.item` XML files. Its own maintainer generates them by parsing ddowiki pages, and keeps an `Issues.txt` of items whose parse failed (Abyssal Arbalest, Band of the Imprisoned One, and others). That is direct evidence that these items are prose-only on the wiki. | https://github.com/Maetrim/DDOBuilderV2 (`Issues.txt`, tree via GitHub API) | High |
| 3 | The same repo has no licence (GitHub API `license: null`), so the data cannot be imported without written permission. Already recorded in docs/research/19-alternative-sources.md. | GitHub API | High |
| 4 | Its XML encodes exactly the shape we need: `ItemAugment` slot lists, per-item `Augment` definitions with `GrantAugment` colour, and `Requirement` blocks of type `Exclusive`. Useful as a design cross-check and as a completeness checklist, not as data to copy. | Raw `.item` files, e.g. `CannithCraftedTowerShield.item` (10 slots) | High |
| 5 | Community spreadsheets or other databases: none found by search; only builders (LittleTealeaf/ddo-build-planner, Maetrim). Not exhaustive. | Web search | Low |

## 2. How comparable projects take corrections

| # | Finding | Source | Confidence |
|---|---|---|---|
| 6 | DDOBuilderV2: 4 contributors on the default branch, Maetrim has 96 commits, the others 1-2 each. PRs total 7 merged, 3 closed unmerged, all small data fixes (add missing stats to Bracers of the Claw; fix an augment). No CONTRIBUTING file, no issue templates, no `.github` directory. Roughly 31 open issues. | GitHub API: contributors, pulls, contents | High |
| 7 | Its predecessor DDOBuilder shows the other channel: the community posts correction lists as issues (e.g. #301, "LIST OF UNUPDATED ITEMS/ARTIFACTS/AUGMENTS", a long list of stale numbers) and the maintainer applies them. | https://github.com/Maetrim/DDOBuilder/issues/301 | High |
| 8 | Pattern: in this niche the workable model is "many reporters, one committer". Reports arrive as issues or small PRs, unsolicited PRs are rare and mostly data typos, and merge authority stays with one person. | Derived from 6-7 | Medium (one project family) |

Not investigated: other games' catalog projects (for example Path of Exile or WoW databases). The DDO-specific evidence is enough for the decision but is a single project family.

## 3. Size of the curation job (rough, from DDOBuilderV2 data)

| Measure | Count |
|---|---|
| Item files | 8,779 |
| Files with 0 augment slots listed | 1,670 |
| Files with 1-2 slots | 5,815 |
| Files with 3-4 slots | 940 |
| Files with 5+ slots (dinosaur bone, Cannith crafted, other) | 354 |
| Files with 8+ slots | 8 (all Cannith-crafted armour/shield templates) |
| Files defining their own `Augment` options (unique systems) | 1,092, of which 58 are Dinosaur or Cannith, the rest mostly templated weapon families (for example "+3 Combustion Scorched <weapon>") |
| Files with `Exclusive` requirements | 0 |
| Files flagged `NoAutoUpdate` (hand-maintained) | 3,123 |

Reading: the 1,092 is a file count, not a system count. Many files are the same system repeated per weapon type, so distinct systems are likely dozens to low hundreds. That collapse was not measured. Mythic/Reaper strings appear in only 26 files, so that bookkeeping lives in shared option lists (ADR 0007), and the double-Mythic ToEE and 4-option Reaper ring cases are a handful of items. Confidence medium: counts are exact, interpretation is not.

## Recommendation for the decision (inputs, not a ruling)

1. Curate maintainer-only at first. The volume of genuinely distinct systems is small, and the shape (override file per Named Item, ADR 0007) suits one committer.
2. Accept corrections through structured GitHub issues (item, wiki link, expected slots/options), not PRs. The comparable project gets few external PRs, and a PR would also need golden-fixture updates (ADR 0007).
3. Template the repeated families: one shared option list and a family override instead of hundreds of per-weapon files.
4. Ask Maetrim for a written licence, or independently re-derive from the wiki. Do not copy the XML.
5. Revisit trusted curators only if issue volume becomes the bottleneck.

## Open gaps
- Sample Compendium item pages for unique-system coverage.
- Collapse the 1,092 files into distinct systems.
- Survey non-DDO catalog projects for contribution models.
