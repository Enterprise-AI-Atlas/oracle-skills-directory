# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pydantic>=2",
# ]
# ///
# ─── How to run ───
# uv run scripts/generate_directory.py
# ──────────────────
"""Generate the agentic-reader-optimized Oracle Skills DIRECTORY.md."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Final, Literal

from pydantic import BaseModel, ConfigDict, field_validator

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
CATALOG_PATH: Final[Path] = REPO_ROOT / "oracle_skills_catalog.json"
DIRECTORY_PATH: Final[Path] = REPO_ROOT / "DIRECTORY.md"
CATALOG_MD_PATH: Final[Path] = REPO_ROOT / "oracle_skills_catalog.md"
SUMMARY_MD_PATH: Final[Path] = REPO_ROOT / "oracle_skills_summary.md"
SOURCE_COMMIT: Final[str] = "8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a"


class Skill(BaseModel):
    """Typed representation of a single catalog entry (skill or MCP server)."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    slug: str
    name: str
    description: str
    type: Literal["skill", "mcp_server"]
    product: str
    marketplace_product: str
    primary_category: str
    all_categories: list[str]
    license: str
    version: str
    author: str
    tags: list[str]
    entry_url: str

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, value: str | list[str]) -> list[str]:
        """Normalize tags when the catalog stores them as a space-separated string."""
        if isinstance(value, str):
            return value.split()
        return [str(tag) for tag in value]


class Catalog(BaseModel):
    """Typed representation of the top-level catalog JSON."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    repo: str
    commit: str
    total: int
    generated_from: str
    skills: list[Skill]


class IndexEntry(BaseModel):
    """A single row in an index table."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    label: str
    count: int


def load_catalog(path: Path) -> Catalog:
    """Parse the catalog JSON into typed Pydantic models."""
    return Catalog.model_validate_json(path.read_text(encoding="utf-8"))


def _now_iso8601() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _md_table_row(cells: list[str]) -> str:
    """Build a Markdown table row, escaping pipe characters in cell text."""
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


def _truncate(text: str, max_length: int = 90) -> str:
    """Collapse whitespace and truncate text for compact tables."""
    collapsed = " ".join(text.split())
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 1] + "…"


def _render_frontmatter(
    repo: str,
    generated_at: str,
    total_skills: int,
    total_local_mcp_servers: int,
    total_repo_mcp_servers: int,
) -> str:
    """Render the YAML frontmatter block."""
    return f"""---
repo: {repo}
source_commit: {SOURCE_COMMIT}
total_skills: {total_skills}
total_local_mcp_servers: {total_local_mcp_servers}
total_repo_mcp_servers: {total_repo_mcp_servers}
generated_at: "{generated_at}"
---
"""


def _render_agent_navigation() -> str:
    """Render the Agent Navigation guidance section."""
    lines = [
        "## Agent Navigation",
        "",
        "Use this directory when you need to locate an Oracle-published skill",
        "or MCP server for a specific product, category, or task.",
        "",
        "- **Looking for an entry by name or slug?** Use the "
        + "[Alphabetical Index](#alphabetical-index).",
        "- **Browsing by domain?** Use the [Category Index](#category-index) "
        + "or [Entries by Category](#entries-by-category).",
        "- **Matching a product?** Use the [Product Index](#product-index).",
        "- **Checking license terms?** Use the [License Index](#license-index).",
        "- **Need the upstream source?** Every entry links directly to the "
        + "source file in the `oracle/skills` repository at the pinned commit.",
        "",
        "Each entry is addressable by the stable heading anchor `## entry-<slug>`.",
        "",
    ]
    return "\n".join(lines)


def _render_index_table(title: str, entries: list[IndexEntry]) -> str:
    """Render a simple two-column index table sorted by label."""
    lines = [f"## {title}", "", "| Name | Count |", "|---|---|"]
    lines.extend(
        _md_table_row([entry.label, str(entry.count)])
        for entry in sorted(entries, key=lambda e: e.label)
    )
    lines.append("")
    return "\n".join(lines)


def _render_alphabetical_index(entries: list[Skill]) -> str:
    """Render the compact alphabetical index of all entries."""
    lines = [
        "## Alphabetical Index",
        "",
        "| Slug | Name | Type | Product | Primary Category | License | Entry Link |",
        "|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        _md_table_row(
            [
                f"[{entry.slug}](#entry-{entry.slug})",
                entry.name,
                entry.type,
                entry.product,
                entry.primary_category,
                entry.license,
                f"[source]({entry.entry_url})",
            ],
        )
        for entry in sorted(entries, key=lambda s: s.slug)
    )
    lines.append("")
    return "\n".join(lines)


def _render_entry_detail(entry: Skill) -> str:
    """Render the detailed block for a single entry with a stable anchor."""
    lines = [
        f"## entry-{entry.slug}",
        "",
        "| Field | Value |",
        "|---|---|",
        _md_table_row(["Slug", entry.slug]),
        _md_table_row(["Name", entry.name]),
        _md_table_row(["Type", entry.type]),
        _md_table_row(["Product", entry.product]),
        _md_table_row(["Marketplace Product", entry.marketplace_product]),
        _md_table_row(["Primary Category", entry.primary_category]),
        _md_table_row(["All Categories", ", ".join(entry.all_categories)]),
        _md_table_row(["License", entry.license]),
    ]
    if entry.version:
        lines.append(_md_table_row(["Version", entry.version]))
    if entry.author:
        lines.append(_md_table_row(["Author", entry.author]))
    lines.extend(
        [
            _md_table_row(["Description", " ".join(entry.description.split())]),
            _md_table_row(["Tags", ", ".join(entry.tags)]),
            _md_table_row(["Entry", f"[source]({entry.entry_url})"]),
            "",
        ],
    )
    return "\n".join(lines)


def _render_entry_details(entries: list[Skill]) -> str:
    """Render a stable anchored detail block for every entry."""
    lines = ["## Entry Details", ""]
    lines.extend(
        _render_entry_detail(entry) for entry in sorted(entries, key=lambda s: s.slug)
    )
    return "\n".join(lines)


def _render_entries_by_category(entries: list[Skill]) -> str:
    """Render entries grouped into subsections by primary category."""
    grouped: dict[str, list[Skill]] = {}
    for entry in entries:
        grouped.setdefault(entry.primary_category, []).append(entry)

    lines = ["## Entries by Category", ""]
    for category in sorted(grouped):
        lines.append(f"### {category}")
        lines.append("")
        lines.append(
            "| Slug | Name | Type | Product | License | Entry Link |",
        )
        lines.append("|---|---|---|---|---|---|")
        lines.extend(
            _md_table_row(
                [
                    f"[{entry.slug}](#entry-{entry.slug})",
                    entry.name,
                    entry.type,
                    entry.product,
                    entry.license,
                    f"[source]({entry.entry_url})",
                ],
            )
            for entry in sorted(grouped[category], key=lambda s: s.slug)
        )
        lines.append("")
    return "\n".join(lines)


def _render_mcp_servers(mcp_servers: list[Skill]) -> str:
    """Render the MCP Servers section with actual entries or a zero-state note."""
    lines = ["## MCP Servers", ""]
    if not mcp_servers:
        lines.append("There are no local MCP servers and no upstream repo MCP servers.")
        lines.append("")
        return "\n".join(lines)

    lines.append(
        f"This directory includes {len(mcp_servers)} Oracle-themed MCP server entries."
    )
    lines.append(
        "URLs marked as unverified have not been confirmed against a public repository.",  # noqa: E501
    )
    lines.append("")
    lines.append(
        "| Slug | Name | Product | Primary Category | License | Entry Link |",
    )
    lines.append("|---|---|---|---|---|---|")
    lines.extend(
        _md_table_row(
            [
                f"[{server.slug}](#entry-{server.slug})",
                server.name,
                server.product,
                server.primary_category,
                server.license,
                f"[source]({server.entry_url})",
            ],
        )
        for server in sorted(mcp_servers, key=lambda s: s.slug)
    )
    lines.append("")
    return "\n".join(lines)


IndexTriple = tuple[list[IndexEntry], list[IndexEntry], list[IndexEntry]]


def _build_indexes(entries: list[Skill]) -> IndexTriple:
    """Compute category, product, and license index entries."""
    categories = Counter(entry.primary_category for entry in entries)
    products = Counter(entry.product for entry in entries)
    licenses = Counter(entry.license for entry in entries)
    return (
        [IndexEntry(label=name, count=count) for name, count in categories.items()],
        [IndexEntry(label=name, count=count) for name, count in products.items()],
        [IndexEntry(label=name, count=count) for name, count in licenses.items()],
    )


def _render_catalog_markdown(catalog: Catalog, generated_at: str) -> str:
    """Render the full catalog as a markdown table."""
    lines = [
        "# Oracle/skills Catalog",
        "",
        f"- Repository: [{catalog.generated_from}]({catalog.generated_from})",
        f"- Commit: `{catalog.commit}`",
        f"- Total entries: {catalog.total}",
        f"- Generated: {generated_at}",
        "",
        "| # | Slug | Name | Type | Product | Primary Category | Description | License | Author | Version | Entry |",  # noqa: E501
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for idx, entry in enumerate(sorted(catalog.skills, key=lambda s: s.slug), start=1):
        lines.append(
            _md_table_row(
                [
                    str(idx),
                    f"`{entry.slug}`",
                    entry.name,
                    entry.type,
                    entry.product,
                    entry.primary_category,
                    _truncate(entry.description),
                    entry.license,
                    entry.author,
                    entry.version,
                    f"[source]({entry.entry_url})",
                ],
            ),
        )
    lines.append("")
    return "\n".join(lines)


def _render_summary_markdown(catalog: Catalog) -> str:
    """Render rollup counts by category, product, and license."""
    categories, products, licenses = _build_indexes(catalog.skills)
    lines = [
        "# Oracle/skills Summary",
        "",
        f"- Total entries: {catalog.total}",
        f"- Skills: {sum(1 for s in catalog.skills if s.type == 'skill')}",
        f"- MCP servers: {sum(1 for s in catalog.skills if s.type == 'mcp_server')}",
        f"- Commit: `{catalog.commit}`",
        "",
        "## By Primary Category",
        "",
    ]
    lines.extend(
        f"- {entry.label}: {entry.count}"
        for entry in sorted(categories, key=lambda e: -e.count)
    )
    lines.extend(["", "## By Product", ""])
    lines.extend(
        f"- {entry.label}: {entry.count}"
        for entry in sorted(products, key=lambda e: (-e.count, e.label))
    )
    lines.extend(["", "## License Distribution", ""])
    lines.extend(
        f"- {entry.label}: {entry.count}"
        for entry in sorted(licenses, key=lambda e: (-e.count, e.label))
    )
    lines.append("")
    return "\n".join(lines)


def generate_directory(catalog_path: Path, output_path: Path) -> None:
    """Read the catalog and write the rendered DIRECTORY.md."""
    catalog = load_catalog(catalog_path)
    if len(catalog.skills) != catalog.total:
        msg = (
            f"catalog total ({catalog.total}) does not match "
            f"entry count ({len(catalog.skills)})"
        )
        raise ValueError(msg)

    categories, products, licenses = _build_indexes(catalog.skills)
    generated_at = _now_iso8601()
    skills = [entry for entry in catalog.skills if entry.type == "skill"]
    mcp_servers = [entry for entry in catalog.skills if entry.type == "mcp_server"]

    parts = [
        _render_frontmatter(
            catalog.repo,
            generated_at,
            total_skills=len(skills),
            total_local_mcp_servers=len(mcp_servers),
            total_repo_mcp_servers=len(mcp_servers),
        ),
        "# Oracle Skills & MCP Server Directory\n",
        _render_agent_navigation(),
        _render_index_table("Category Index", categories),
        _render_index_table("Product Index", products),
        _render_index_table("License Index", licenses),
        _render_alphabetical_index(catalog.skills),
        _render_entries_by_category(catalog.skills),
        _render_entry_details(catalog.skills),
        _render_mcp_servers(mcp_servers),
    ]
    _ = output_path.write_text("\n".join(parts), encoding="utf-8")


def generate_artifacts(catalog_path: Path) -> None:
    """Generate DIRECTORY.md, oracle_skills_catalog.md, and oracle_skills_summary.md."""
    catalog = load_catalog(catalog_path)
    generated_at = _now_iso8601()
    _ = CATALOG_MD_PATH.write_text(
        _render_catalog_markdown(catalog, generated_at),
        encoding="utf-8",
    )
    _ = SUMMARY_MD_PATH.write_text(
        _render_summary_markdown(catalog),
        encoding="utf-8",
    )


def main() -> None:
    """CLI entry point for the generator."""
    generate_directory(CATALOG_PATH, DIRECTORY_PATH)
    generate_artifacts(CATALOG_PATH)
    print(f"Generated {DIRECTORY_PATH}")
    print(f"Generated {CATALOG_MD_PATH}")
    print(f"Generated {SUMMARY_MD_PATH}")


if __name__ == "__main__":
    main()
