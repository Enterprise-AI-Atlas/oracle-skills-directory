# Oracle Skills Directory

A complete, agentic-reader-optimized directory of Oracle skills and MCP servers.

## What's here

- **`DIRECTORY.md`** — the canonical catalog. 24 Oracle skills and MCP servers with stable anchors, category/product/license indexes, deep links to each entry, and explicit notes on MCP server coverage.
- **`oracle_skills_catalog.json`** — structured JSON extract of all 24 skills and MCP servers.
- **`oracle_skills_catalog.md`** — full markdown table of all 24 entries.
- **`oracle_skills_summary.md`** — rollup counts by category, product, and license.
- **`scripts/generate_directory.py`** — generator that reads the JSON catalog and emits `DIRECTORY.md`.
- **`tests/test_directory.py`** — acceptance tests locking the directory contract.

## Source

Data was extracted from:

- Repository: [`https://github.com/oracle/skills`](https://github.com/oracle/skills)
- Commit: [`8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a`](https://github.com/oracle/skills/tree/8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a)
- Total skills cataloged: **18**
- MCP servers cataloged: **6** (representative URLs where a verified public repo is not known)

## Regenerate the directory

```bash
uv run scripts/generate_directory.py
```

## Run the tests

```bash
uv run pytest tests/test_directory.py -v
```

## Other quality checks

```bash
uv run ruff check scripts tests
uv run ruff format --check scripts tests
uv run basedpyright
```

## License

The directory contents reflect the licenses declared in each upstream entry (mostly Apache-2.0). This repository's tooling is provided under the same permissive terms; see individual files for details.

## Need implementation help?

Enterprise AI Atlas is maintained by [Vibe Coding Agency](https://vibecodingagency.com). If your team needs support designing, building, or deploying production AI systems covered in this atlas, [get in touch](https://vibecodingagency.com).
