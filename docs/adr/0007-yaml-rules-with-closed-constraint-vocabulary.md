# YAML rules with overrides, a closed constraint vocabulary, and CI golden fixtures

Hand-curated Customisation rules live in the public repo as schema-validated YAML, separate from scraped item JSON. Constraints use a small closed vocabulary. CI proves the rules and the shipped validator agree.

## Why

- The scraper rewrites per-item JSON on every refresh, so curated data must live elsewhere or it is clobbered.
- The maintainer edits these files by hand and reviews them as diffs; they need comments for wiki citations and edge cases.
- ADR 0002 promises that invalid Instances cannot be submitted. That promise holds only if the rules data and the validator cannot drift apart.

## Shape

- **Format**: YAML, validated by JSON Schema. Scraped per-item data stays JSON (ADR 0006).
- **Layout** under `catalog/rules/`:
  - `option-lists/`: shared lists (Mythic bonuses, Reaper options, general crafting, augment catalogue by colour and level).
  - `slot-compat.yaml`: the colour-compatibility matrix and per-kind slot rules (for example Mythic +2/+4 on weapons, shields and armor, +1/+3 elsewhere).
  - `overrides/<named_item_id>.yaml`: item-unique systems and manual gap-fills of scraped slot colours, with a `# name:` comment for humans.
- **Merge**: the catalog compiler merges scraped slots with overrides at build time. An override replaces the item's scraped slots wholesale; there is no partial merge.
- **Constraints**: a closed vocabulary of about four declarative types (for example `mutually_exclusive`, `max_selected`, `requires`), enforced as a schema enum. A new type needs a validator release and a `min_app_version` bump (ADR 0004).
- **Unknown slot data**: an item without curated or scraped slot data carries `slots_status: unknown`. The backend allows no Customisations on it and the UI says the data is not yet available. Later fill-in does not flag existing Instances.
- **CI gates** (block a catalog release): JSON Schema validity; referential integrity (every `shared:` reference resolves, every override UUID is in the registry, redirects do not dangle); golden-fixture tests running valid and invalid Instances through the real backend validator. A coverage report of items lacking slot data is a warning only.

## Considered options

- **JSON or TOML for rules**: JSON has no comments; TOML is awkward for nested option lists.
- **Expression language for constraints** (reusing the ADR 0005 `$filter` subset): more expressive, but harder to validate in CI and easier for a curator to get wrong.
- **Curated data inside scraped item files**: clobbered by every scrape.
- **Partial merge of overrides**: ambiguous when the scrape and the override disagree.

## Consequences

- A constraint the vocabulary cannot express forces a validator change, not just a data edit.
- Golden fixtures are a required maintenance cost whenever rules change.
- Who curates item-unique data is deferred to a research ticket.

> Amended by ADR 0009: catalog source files live in the separate catalog repo; the decision here is unchanged.

> Further amended by ADR 0009: the rules validator lives in the app repo; the data repo checks the bundle against the app's published spec, and semantic golden-fixture checks run in the app repo.
