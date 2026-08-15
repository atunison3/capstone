# Contributor Guide

This section is for people changing the `capstone` source code.

End users who only want to install and run the tool should start with [Installation](getting-started/installation.md) instead.

## Project facts

| Item | Value |
| --- | --- |
| Package name (distribution) | `capstone-2026` |
| Import package | `capstone` |
| Python | `>= 3.13` |
| CLI entry point | `capstone` → `capstone.analysis:main` |
| Tests | `unittest` under `tests/` |
| Repo | https://github.com/atunison3/capstone |
| License | MIT (see [License](about/license.md)) |

## Workflow overview

1. Fork or branch from the repository (do not commit directly to `main`).
2. Follow [Development Setup](contributing/development-setup.md).
3. Make changes on a feature branch.
4. Run [tests and quality checks](contributing/testing.md).
5. Open a pull request. At least one reviewer approval is required.

## Docs site (Docsify)

Documentation lives in `docs/` and is rendered with Docsify.

### macOS / Linux

```bash
npx docsify-cli serve docs
```

### Windows

```powershell
npx docsify-cli serve docs
```

Then open the URL printed in the terminal (typically `http://localhost:3000`).

## AI assistance

This repository used AI tooling during development. See the [AI statement](about/ai-statement.md) for how that work was scoped, tested, and human-reviewed.

## Next

- [Development Setup](contributing/development-setup.md)
- [Testing](contributing/testing.md)
- [Meet the team](about/meet-the-team.md)
- [AI statement](about/ai-statement.md)
