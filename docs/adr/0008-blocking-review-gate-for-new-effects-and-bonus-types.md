# Blocking review gate for newly discovered effects and bonus types

The catalog build discovers new Effects and Bonus Types from scraped data, proposes registry entries, and blocks the release until the maintainer decides each one in a CI-driven review PR. Effect keys are immutable once shipped (ADR 0005), so nothing enters the registry unreviewed.

## Why

- The effect list is large and grows with each game update; a hand-maintained alias list alone cannot keep up.
- Keys are immutable, so a wrong auto-match or an unreviewed mint is expensive to undo.
- The maintainer does not want to edit files locally or in a codespace to approve changes.

## Shape

- **Registry**: `catalog/effects/*.yaml` (slug key, display name, nullable tooltip, `aliases`) and `catalog/bonus-types.yaml` (key, name, nullable `stacks_with_self`). Tooltips are scraped, with a hand-written override that wins.
- **Discovery**: a raw string with no exact alias hit becomes a pending entry. Fuzzy matching only fills a `suggested` key (null below the threshold); it never aliases automatically. A string matching no existing bonus type (for example a new type such as Celestial) is proposed as a new bonus type.
- **Review file**: a single `catalog/review/pending.yaml`, grouped into `new_bonus_types`, `new_effects` and `fuzzy_matches`. Each entry carries the raw string, the proposed slug, `suggested` and one decision: `approved: true`, `merge_into: <key>` or `ignore: true`.
- **Review PR**: CI opens (or updates the one open) `review/...` PR containing `pending.yaml`. The maintainer edits flags in GitHub's web editor. On an approving review, an apply job validates the file (exactly one decision per entry, every `merge_into` key exists), commits registry and alias changes to the PR branch and deletes `pending.yaml`. An invalid file gets a PR comment and no commit.
- **Gate**: the manual release workflow refuses to run while `pending.yaml` exists on main. There is no raw-text fallback for unmapped effects.
- **Bootstrap**: a one-time `--bootstrap` import auto-approves all discovered entries and marks them `verified: false`, so the initial 4,993-page backlog is not hand-reviewed. The gate applies normally afterwards.

## Considered options

- **Ship unmapped effects as raw text, non-blocking**: keeps releases flowing but leaves a permanently unfilterable tail.
- **Auto-alias on fuzzy match**: a wrong match silently merges distinct effects under an immutable key.
- **Review issue with checklists**: `merge_into` values are fragile in checkbox text.
- **Local apply command**: rejected; the maintainer wants no local or codespace editing.

## Consequences

- A release can stall until the maintainer reviews the PR; the bootstrap exception is the only bulk path.
- CI needs write access to open PRs and commit to review branches.
- The fuzzy threshold needs tuning against existing effect names.

> Amended by ADR 0009: catalog source files live in the separate catalog repo; the decision here is unchanged.
