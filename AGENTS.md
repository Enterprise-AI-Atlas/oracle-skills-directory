# Agent Notes — Oracle Skills Directory

## Project type
Documentation/generator repo. The only source of truth for skill data is `oracle_skills_catalog.json`; `DIRECTORY.md`, `oracle_skills_catalog.md`, and `oracle_skills_summary.md` are generated or derived artifacts.

## Key files
- `oracle_skills_catalog.json` — source-of-truth extract from `oracle/skills@8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a`. Do not hand-edit.
- `scripts/generate_directory.py` — regenerates `DIRECTORY.md` from the JSON catalog.
- `tests/test_directory.py` — acceptance tests for `DIRECTORY.md` structure and completeness.
- `DIRECTORY.md` — generated canonical catalog (this repo's `readme` in `pyproject.toml`).

## Commands
```bash
# Regenerate the directory
uv run scripts/generate_directory.py

# Run tests
uv run pytest tests/test_directory.py -v

# Quality gates (must all pass before pushing)
uv run ruff check scripts tests
uv run ruff format --check scripts tests
uv run basedpyright
```

## Tooling quirks
- `uv` is required. The generator script uses PEP 723 inline metadata, so `uv run scripts/generate_directory.py` works without a manual venv.
- `basedpyright` only includes `scripts` and `tests`; generated markdown files are not type-checked.
- `pytest` `pythonpath = ["."]` lets tests import `scripts.generate_directory`. Do not move `scripts/` without updating `pyproject.toml`.
- `ruff` `src = ["scripts", "tests"]`; treat both as first-class source.

## Editing rules
- Never edit `DIRECTORY.md` by hand. Change `scripts/generate_directory.py` and rerun.
- The pinned commit hash `8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a` is hardcoded in both the generator and tests. If you update the catalog source, update both.
- The catalog JSON is an external snapshot. Refresh it by re-running the extraction logic (not stored in this repo) or by replacing the file and regenerating.

## MCP servers
This repo catalogs both Oracle skills and Oracle-themed MCP servers. The JSON catalog marks each entry with `type: "skill"` or `type: "mcp_server"`. MCP server entry URLs are representative links where a verified public repository is not known; descriptions note "(URL not verified — representative link.)"
