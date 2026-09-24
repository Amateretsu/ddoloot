# DDOLoot data bundle spec

The contract between the data repo (`ddoloot-data`, producer) and the app (consumer), per ADR 0009. The app repo owns this spec; the data repo fetches it as an immutable release asset and validates every bundle against each `format_version` that released apps still support.

**Status: v1 draft.** Field names and the constraint vocabulary are not frozen until the first spec release.

## Bundle layout

A bundle is an archive of JSON files (the data repo compiles its YAML/JSON sources into these):

| File | Content | Schema |
|---|---|---|
| `meta.json` | `format_version`, `catalog_version`, counts | `meta.schema.json` |
| `items.json` | array of Named Items | `item.schema.json` |
| `effects.json` | Effect registry (immutable slug keys) | `effect.schema.json` |
| `bonus-types.json` | Bonus Type lookup | `bonus-type.schema.json` |
| `option-lists.json` | shared Customisation option lists | `option-list.schema.json` |
| `slot-compat.json` | colour matrix and per-kind rules | `slot-compat.schema.json` |
| `servers.json` | Server list | `server.schema.json` |
| `redirects.json` | merged or removed Named Item ids | `redirect.schema.json` |

The release also carries `manifest.json` (`manifest.schema.json`) and its Ed25519 signature `manifest.json.sig` (ADR 0004).

## Rules the schemas cannot express

`validate_bundle.py` checks these; the app's loader must too:

- Ids and keys are unique within their file.
- Every item effect and bonus type key resolves; every `shared` option list resolves.
- A slot with a `colour` and no `options` needs an `augments` option list and a `colour_compat` entry for that colour; its valid options are the augments whose colour that entry accepts.
- Constraint `slots` (and `requires`' `if_slot`/`then_slot`) refer to Customisation slot ids on the same item; slot `min <= max`.
- A redirect's `from` is not a live item; a non-null `to` is.
- `meta.counts` match the files.
- Items with `slots_status: unknown` have no Customisation slots or constraints (schema-enforced).

## Versioning

- Schemas are open: consumers ignore unknown fields, so additive changes (new optional fields) never bump `format_version`. The data repo lints its own output with `validate_bundle.py --strict`. Anything non-additive bumps it, and the manifest's `min_app_version` gates older apps (ADR 0004).
- A bundle that fails to load fails closed: the app keeps its current catalog.
- Constraint types are a closed enum; adding one requires a validator release and a `min_app_version` bump (ADR 0007).

## Open points for review

- `binding` is normalised to `account | character | on_equip | unbound`; the scraper's free-text values need a mapping table.
- Bonus values are numbers (Superior Devotion VI is stored as its tier, per the current normalizer).
- Effects carry no `category`; add if search facets need it.
