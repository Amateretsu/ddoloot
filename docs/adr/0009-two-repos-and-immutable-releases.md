# Separate catalog repo and immutable releases

The catalog lives in its own public repo (working name `ddoloot-catalog`); the app lives here. Each repo publishes ordinary GitHub Releases that are never edited after publishing. App and catalog versions are independent.

## Why

- Both ADR 0004's manifest fetch (`releases/latest/download/manifest.json`) and the Tauri updater feed rely on "latest". In one repo an app release would displace a catalog release as latest and vice versa. Two repos give each its own unambiguous `releases/latest`.
- Moving "pointer" releases were rejected: they duplicate state and mutate published releases, which invites drift.
- The catalog (wiki-derived, CC BY-SA) is kept apart from the GPL-3.0 code, which settles the licence-mismatch finding.

## Shape

- **Data repo** (working name `ddoloot-data`) owns the scraper and `ddo_sync`, item JSON, UUID registry, redirects, `catalog/rules/`, `catalog/effects/`, the review gate, and the bundle build and manifest signing. It publishes a signed, versioned **data bundle** (validated JSON/YAML plus a `format_version`), not a database. Releases are manual and immutable.
- **App repo** owns the DB schema, FTS5 index, sidecar, user-data store, UI and Tauri shell. It downloads the bundle, verifies it with the embedded public keys, compiles it into its local SQLite, then does the atomic swap and reconcile pass (ADR 0003). A bundle that fails to load fails closed: the current catalog is kept.
- **The app repo owns the data spec.** It publishes a versioned spec (JSON Schema for the bundle, `format_version`) as an immutable release asset. The data repo's CI fetches the spec and validates every bundle against each spec version that released apps still support, not only the newest. When the spec changes, a data-repo run validates existing data; on failure it opens an issue with the failure report and a fix branch. The branch is auto-migrated only where the spec ships a declared migration, otherwise it holds the failing-fixture scaffold for a human or agent. Semantic checks (rule and effect golden fixtures) run in the app repo against the newest published bundle, on a schedule and before app releases.
- **No cross-repo dispatch.** When cutting an app release, the build fetches the newest validated catalog release as the bundled snapshot and records its `catalog_version` in the app release notes. A published app release is never changed afterwards. Installed apps pick up newer catalogs through ADR 0004.
- **App release**: tag `v*` builds installers on one runner per OS into a draft Release, `latest.json` included as an asset of that same release; the maintainer smoke-tests then publishes. The updater endpoint is the app repo's `releases/latest/download/latest.json`. Semver from one source file that CI checks against the Tauri, Python and package manifests. The Tauri updater key is a CI secret; the public key is embedded.
- **Signing v1**: Windows unsigned (README walkthrough for SmartScreen), macOS unsigned (README walkthrough for Gatekeeper). Azure Trusted Signing and Apple notarization are added on demand.
- **Linux**: AppImage only, built on ubuntu-22.04 for glibc compatibility, tested on CachyOS (FUSE required, documented).
- **Windows sidecar**: assign the sidecar to a Job Object with kill-on-close, in addition to the stdin-EOF watchdog used on every OS. Onedir packaging per ADR 0001's spike.

## Considered options

- **One repo, `catalog-latest` and `app-latest` pointer releases**: workable but mutates published releases and has several drift windows (manifest/signature, pointer ordering, pre-publish 404s).
- **Prerelease flag to hide one series from "latest"**: fragile and easy to break.
- **Prebuilt `catalog.sqlite` from the data repo (ADR 0004 as first written)**: couples the repos through a SQL schema and puts FTS5 and schema ownership on the wrong side.
- **Catalog release triggers an app release**: rejected; it would force a three-OS build and restart per data change and defeat ADR 0004.
- **Dispatch that bumps a pinned snapshot**: rejected; fetching at release time needs no cross-repo credential.

## Consequences

- Catalog source, rules and effects paths in ADRs 0003, 0004, 0007 and 0008 now refer to the catalog repo; their decisions are unchanged.
- The app's item model must not import from the scraper; the bundle spec is defined in the app repo and consumed by the data repo as a release asset.
- A spec change can break data-repo builds until data is migrated; the failure-issue flow and multi-version validation contain this.
- Ingest cost (compiling the bundle) is paid on the user's machine, in the background.
- Two repos to maintain; issues and the map stay in this repo.
- Unsigned v1 installers will show OS warnings.
