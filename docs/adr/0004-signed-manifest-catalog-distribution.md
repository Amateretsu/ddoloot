# Signed-manifest catalog distribution via GitHub Releases

The catalog is built by CI from source files in the public repo and published as a GitHub Release containing a SQLite artifact and an Ed25519-signed manifest. Installed apps poll the manifest, verify it, and swap the catalog in (ADR 0003).

## Why

- The catalog is data shared by every player and must update without an app release.
- End users never scrape the wiki; the maintainer is the single publisher.
- Signing is cheap and protects against a tampered release or hosting account.

## Shape

- **Source and build**: the repo holds diffable source (items, UUID registry, redirects, Customisation rules). CI compiles it to `catalog.sqlite`. The artifact is never hand-edited; the scraper only writes source files.
- **Release**: tagged `catalog-*`, carrying `catalog.sqlite`, `manifest.json` and `manifest.json.sig`. Releases are triggered manually; a scheduled scrape is a later addition.
- **Versions**: `catalog_version` is `YYYY.MM.DD.NNNN`, NNNN being the zero-padded GitHub Actions run number, so it is strictly increasing and string-sortable. `schema_version` is a separate integer.
- **Manifest**: `catalog_version`, `schema_version`, `min_app_version`, artifact URL, artifact `sha256`, signing key id. Fetched from `releases/latest/download/manifest.json`, avoiding the GitHub API rate limit.
- **Signature**: Ed25519 over the manifest; the manifest's `sha256` chains to the artifact. The private key is a CI secret. The app embeds a list of public keys with ids, so rotation is an app update that adds a key before signing switches.
- **App behaviour**: every installer bundles a snapshot. Downloaded catalogs live in app-data and the highest compatible `catalog_version` wins. The app checks at startup (at most daily) and on demand, downloads in the background, and applies at next launch. It keeps the previous validated catalog for rollback, with the bundled snapshot as the floor. If the reconcile pass flags Instances, the user gets a notice.
- **Schema policy**: additive changes by default. On a breaking bump, `min_app_version` makes older apps show "update the app" and skip the download; parallel schemas are not maintained.
- **Attribution**: each Named Item carries its source URL, and the app shows a notice naming the wiki and its licence.

## Considered options

- **GitHub Releases API for "latest"**: 60 requests/hour unauthenticated and coupled to GitHub's API shape.
- **Hash only, no signature**: guards corruption but not a compromised release.
- **Parallel schema builds**: too much upkeep for a solo maintainer.
- **Prompt before applying updates**: extra friction; the revert path makes auto-apply safe.

## Consequences

- Losing or leaking the signing key requires an app update carrying a new public key.
- `catalog-*` tags must coexist with app releases and the Tauri updater feed (packaging is unresolved).
- The wiki's licence terms must be confirmed before the first public catalog release.

> Amended by ADR 0009: catalog source files live in the separate catalog repo; the decision here is unchanged.

> Amended by ADR 0009: the manifest is fetched from the catalog repo's own `releases/latest`, so it no longer coexists with app releases.

> Further amended by ADR 0009: the signed artifact is now the data bundle (not a prebuilt SQLite) which the app compiles into its own database; `schema_version` becomes the bundle `format_version` range. Manifest, signature, versions, rollback and bundled snapshot are otherwise unchanged.
