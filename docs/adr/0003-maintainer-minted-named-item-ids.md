# Maintainer-minted Named Item IDs, atomic catalog swap with reconcile

Every Named Item has a UUID minted once by the maintainer and kept in a registry file committed to the public repo. The wiki page ID is recorded on each item only as a source reference for normalisation and de-duplication, never as the identity.

## Why

- Identity must survive wiki renames, page moves and merges, and must not depend on a third party's ids.
- The scraper is unreliable against the wiki, so identity cannot depend on scraper runs: the registry is the source of truth and the scraper only matches pages to existing entries.
- User data references Named Items by this id across every catalog refresh, so it must never change once shipped.

## Shape

- **Registry**: maps `named_item_id` (UUID) to the item's source page ID. A scrape matches by page ID first, so a rename keeps its UUID and only the display name changes. A new page gets a new UUID.
- **Merges and removals**: a maintainer-curated redirect entry (`old_id -> new_id`, or `-> removed`) ships with the catalog. Any user Instance whose id is missing without a redirect is kept and flagged for review (ADR 0002), never deleted.
- **User reference**: an Item Instance stores `named_item_id` plus a name snapshot taken when recorded, so orphans stay readable. There is no foreign key across the two SQLite files.
- **Catalog update**: the app replaces the catalog file wholesale (atomic swap) and records a `catalog_version`. A reconcile pass then applies redirects, re-validates Customisations against the new rules, and flags failures. It is idempotent and also runs at startup. Each Instance records the `catalog_version` it was last validated against.
- **Schema version**: every catalog carries a `schema_version`. An app refuses a catalog newer than it understands, stays on its last good catalog, and tells the user to update the app.

## Considered options

- **Wiki page ID as the key**: free to capture, but ties identity to the wiki, and a deleted or merged page breaks references with no maintainer control.
- **Slug from the name**: breaks on every rename.
- **Incremental catalog merge**: more complex, and unnecessary because the catalog holds no user data.

## Consequences

- The scraper must capture page ID; the registry needs a bootstrap for the existing 80 items and the 4,993-page backlog.
- The catalog format is a versioned contract between the repo and every installed app.

> Amended by ADR 0009: catalog source files live in the separate catalog repo; the decision here is unchanged.
