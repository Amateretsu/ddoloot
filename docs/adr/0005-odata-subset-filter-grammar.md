# OData `$filter` subset as the single search filter grammar

Catalog and inventory search share one filter grammar: a small subset of OData `$filter`, sent as a single `filter` string. Multi-valued fields (effects, Customisations) are filtered with explicit `any()` lambdas, so several conditions bind to one row.

## Why

- The map requires one grammar usable from a query string and a POST body, shared by `catalog/` and `inventory/`, so a hosted mode can reuse it.
- Effects (key, bonus type, nullable value) and Customisations (kind, value) are multi-valued. Filters like "Strength of at least +2 that is Insight-typed" must bind to the same row. `any()` makes that explicit instead of relying on an implicit rule.
- OData is an OASIS/ISO standard with parentheses, `and`/`or`/`not`, and lambdas. ServiceNow-style encoded queries have no grouping and no row-binding.

## Shape

- **Transport:** `GET ...?filter=<string>`, or `POST /search` with `{"filter": "<string>"}` (or a JSON AST of the same grammar). No per-field parameters.
- **Separate parameters:** `search` (keyword box, SQLite FTS5, prefix, AND across words, name-weighted, tooltip text included), `orderby`, `limit` (default 50), `offset`, `facets`, and `account`/`server` context. Responses carry `total`, `schema_version` and the catalog version.
- **Operators:** `eq ne gt ge lt le in`, `and or not`, parentheses, `contains startswith endswith`. Paths use `/`.
- **Keyword matching:** `search.ismatch('text')` inside `filter` uses the same FTS as `search`. A fuzzy variant can be added as a new function without changing the grammar.
- **Examples:**
  - `slot eq 'ring' and effects/any(e: e/key eq 'devotion' and e/type eq 'insight' and e/value ge 5)`
  - `effects/any(e: e/key eq 'cannith_combat_infusion')` (value is null, presence only)
  - `custom/any(c: c/kind eq 'mythic' and c/value eq 4)`
  - `(slot eq 'ring' and level le 10) or level ge 30`
  - Inventory reaching the Named Item: `item/level ge 5 and custom/any(...)`
- A null effect value never passes a comparison, but counts for presence.
- `GET /api/v1/catalog/fields` and `/api/v1/inventory/fields` list each filterable field: name, type, operators, multi-valued flag, option list, and dotted or lambda-path examples. The UI builds filters from them and the server validates against them. Unknown fields or operators return a 400.
- **Views:** Catalog browse works with no context. Collection and Inventory require a selected DDO Account and Server. The `owned` filter and `quantity` need that context.
- **Data:** Effect is a shared catalog entity (key, name, tooltip text). An item-effect row is (effect, bonus type, nullable value). Bonus types are a catalog lookup list.

## Considered options

- **ServiceNow-style encoded queries:** familiar, but no grouping and no row-binding.
- **Per-field query parameters:** a second surface that can't express OR, grouping or lambdas.
- **POST-only:** simplest locally, but loses GET semantics and the hosted-ready constraint.

## Consequences

- The build needs a hand-written parser (e.g. Lark) for the subset, plus a validator driven by the fields endpoint.
- Facet counts are computed with a field's own filter excluded.
- Effect keys are maintainer-curated readable slugs alongside UUIDs.
