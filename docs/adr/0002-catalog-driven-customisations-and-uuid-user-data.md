# Catalog-driven Customisations, UUID identifiers, separate user-data store

Customisation rules are data in the catalog, not code. User data lives in its own SQLite file, keyed by UUIDs, and references the catalog by stable Named Item ID.

## Why

- Named Items carry item-specific Customisation systems (augment colours, Mythic, Reaper, crafting such as Nearly Finished). The set of kinds is open-ended and changes with the game, so hardcoding them would mean an app release for every change.
- All catalog data, including rules, options and the Server list, syncs live from the public repo. User data must never live inside a file the sync replaces.
- Every user-data entity gets a client-generated UUID so backup, import/export and a future hosted mode can merge without id collisions. Retrofitting this later is costly.

## Shape

- Each Named Item lists its **customisation slots**: a kind, a cardinality, and an **option source**. The source is `shared:<option-list-id>` (augment catalogue, Mythic bonus table, general crafting) or `inline:[...]` (values unique to that item).
- Cross-slot constraints (mutual exclusion, one Reaper option per item) are declared in the same data.
- One generic backend validator and one dropdown-only form. Customisation values are always a selection from an option list, never typed.
- The backend rejects every invalid write, and only offers valid options to the UI.
- When a rules or catalog change makes a stored Instance invalid, or removes its Named Item, the Instance is kept and flagged for review. It is never silently deleted.

## Considered options

- **Rules in Python code**: simpler, but every game change needs an app release and conflicts with live catalog sync.
- **Auto-increment integer ids**: fine locally, but collide on merge and force a migration when hosted mode arrives.
- **Combined catalog and user-data file**: a catalog swap could touch user data.

## Consequences

- The catalog schema must carry slot and option data; the augment catalogue and per-item slot colours become v1 scrape requirements.
- User-data schema migrations are versioned.
- The exact rule notation is left to the build.
