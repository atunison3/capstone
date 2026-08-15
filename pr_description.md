# Docsify documentation, MIT license, and config module migration

## Summary

This PR expands the project into a proper Docsify documentation site, adds an MIT license, and moves runtime configuration from `config.toml` into `capstone/config.py`. It also wires the `capstone` CLI entry point and updates helper/tests to match the new config path.

## Motivation

- Make the project easy to discover and use (install → run → deeper docs).
- Ship clear licensing and an honest AI-use statement.
- Keep configuration inside the installable package instead of a repo-root TOML file.
- Improve the Docsify UX (sidebar navigation, UMich theme, cover page).

## What changed

### Documentation (Docsify)

- Built out `docs/` as a full site:
  - Cover page, sidebar, home page
  - Getting started: installation + usage
  - Package/module reference under `documentation/`
  - Contributor guide, development setup, testing
- Home page prioritizes the **data story** (placeholder + figures), then **install and run**:
  ```bash
  pip install git+https://github.com/atunison3/capstone.git
  capstone
  ```
- Added **License (MIT)** and **AI statement** pages.
- Polished UMich theme (`theme-umich.css`):
  - Navy sidebar, readable light nav text
  - Maize cover title (`#capstone`)
  - Search input/results contrast fixes
  - Stable sidebar (no page-heading injection; root-relative links)
- Fixed Docsify nav issues (Home 404 under nested routes, section header colors, relative path resolution).

### Licensing

- Added root `LICENSE` (MIT) — Copyright 2026 Andy Tunison, Melody Ren, and Sahana Sundar.
- Documented MIT in docs + README; clarified that third-party datasets keep their own terms.
- Registered license in `pyproject.toml` (`license = "MIT"`, `license-files`).

### Configuration

- Removed root `config.toml`.
- Added `capstone/config.py` with UPPERCASE constants (`DATA_PATH`, feature lists, column maps, value maps).
- `load_model_config()` now loads from `capstone.config` (lowercased keys) instead of TOML.
- `data_cleaning` stringifies mapping keys so int/float map keys match `.astype(str)` columns.
- Updated tests in `tests/test_helper_functions.py` for the new loader.

### CLI / packaging

- Renamed entry module to `capstone/analysis.py`.
- Added console script:
  ```toml
  [project.scripts]
  capstone = "capstone.analysis:main"
  ```
- Added project URLs (repo + documentation site).
- Tightened Ruff `extend-exclude` (dropped obsolete `notes` / notebook exclusions as applicable).

### Cleanup / other

- Removed obsolete notes and helper scripts no longer needed on this branch (e.g. `get_dependencies.py`, old `requirements-dev.txt` snapshot where replaced by branch history).
- Workflow/README touch-ups aligned with the new docs and install path.

## AI statement (process)

AI assisted scaffolding and drafting (including much of the Docsify site). Architecture, domain detail, review, and revisions were human-led. Tests were added/updated to check intended behavior. See `docs/ai-statement.md`.

## How to review

1. Skim `docs/` structure and sidebar order (AI statement above License).
2. Spot-check module docs against `capstone/*.py` and `capstone/config.py`.
3. Confirm `load_model_config()` + `TestLoadConfig` match `config.py`.
4. Confirm `pyproject.toml` license/script/urls parse cleanly.
5. Optional: `npx docsify-cli serve docs` and click through Home → install → docs → AI → License.

## Test plan

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -c "from capstone.helper_functions import load_model_config; print(sorted(load_model_config()))"`
- [ ] `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"`
- [ ] Docsify local preview: Home, nested pages, search, cover title color, sidebar Navigation header
- [ ] (If data present) `capstone` CLI runs end-to-end or fails only on expected missing CES download step

## Notes / follow-ups

- Data story content on the home page is still a placeholder for later narrative writing.
- CES install remains a guided manual download (Dataverse WAF).
- Confirm GitHub Pages is publishing from `docs/` if using the Documentation URL in `pyproject.toml`.
