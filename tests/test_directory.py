"""Acceptance tests for the generated Oracle Skills DIRECTORY.md."""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, Final

import pytest
import yaml
from pydantic import BaseModel, ConfigDict
from scripts.generate_directory import Catalog, load_catalog

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DIRECTORY_PATH: Final[Path] = REPO_ROOT / "DIRECTORY.md"
SOURCE_COMMIT: Final[str] = "8f4a2b1c9d0e3f5a6b7c8d9e0f1a2b3c4d5e6f7a"
EXPECTED_TOTAL_SKILLS: Final[int] = 18
EXPECTED_TOTAL_MCP_SERVERS: Final[int] = 6

REQUIRED_SECTIONS: Final[frozenset[str]] = frozenset(
    {
        "Agent Navigation",
        "Category Index",
        "Product Index",
        "License Index",
        "Alphabetical Index",
        "Entries by Category",
        "Entry Details",
        "MCP Servers",
    }
)


class Frontmatter(BaseModel):
    """Typed shape of the DIRECTORY.md YAML frontmatter."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    repo: str
    source_commit: str
    total_skills: int
    total_local_mcp_servers: int
    total_repo_mcp_servers: int
    generated_at: str


@pytest.fixture(scope="session")
def catalog() -> Catalog:
    """Load the catalog once for the test session."""
    return load_catalog(REPO_ROOT / "oracle_skills_catalog.json")


@pytest.fixture(scope="session")
def directory_text() -> str:
    """Read DIRECTORY.md once for the test session."""
    if not DIRECTORY_PATH.exists():
        pytest.fail(f"{DIRECTORY_PATH.name} does not exist")
    return DIRECTORY_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def frontmatter(directory_text: str) -> Frontmatter:
    """Parse the YAML frontmatter from DIRECTORY.md."""
    match = re.match(r"^---\n(.*?)\n---\n", directory_text, re.DOTALL)
    if not match:
        pytest.fail("YAML frontmatter not found")
    return Frontmatter.model_validate(yaml.safe_load(match.group(1)))


class TestFrontmatter:
    """Acceptance tests for YAML frontmatter."""

    def test_repo_matches_catalog(
        self, frontmatter: Frontmatter, catalog: Catalog
    ) -> None:
        """Frontmatter repo matches the catalog source."""
        assert frontmatter.repo == catalog.repo

    def test_source_commit_matches_expected(self, frontmatter: Frontmatter) -> None:
        """Frontmatter source_commit is the pinned commit hash."""
        assert frontmatter.source_commit == SOURCE_COMMIT

    def test_total_skills_matches_expected(self, frontmatter: Frontmatter) -> None:
        """Frontmatter total_skills equals the expected skill count."""
        assert frontmatter.total_skills == EXPECTED_TOTAL_SKILLS

    def test_mcp_server_counts_match_expected(self, frontmatter: Frontmatter) -> None:
        """Frontmatter MCP server counts match the expected count."""
        assert frontmatter.total_local_mcp_servers == EXPECTED_TOTAL_MCP_SERVERS
        assert frontmatter.total_repo_mcp_servers == EXPECTED_TOTAL_MCP_SERVERS

    def test_generated_at_is_iso8601(self, frontmatter: Frontmatter) -> None:
        """Frontmatter generated_at is an ISO 8601 timestamp."""
        assert (
            re.match(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                frontmatter.generated_at,
            )
            is not None
        )


class TestRequiredSections:
    """Acceptance tests for required section headings."""

    @pytest.mark.parametrize("section", sorted(REQUIRED_SECTIONS))
    def test_section_exists(self, directory_text: str, section: str) -> None:
        """Each required section heading is present."""
        pattern = re.compile(rf"^## \s*{re.escape(section)}\s*$", re.MULTILINE)
        assert pattern.search(directory_text) is not None


class TestEntryAnchors:
    """Acceptance tests for per-entry anchors and links."""

    def test_every_slug_has_exactly_one_anchor(
        self, directory_text: str, catalog: Catalog
    ) -> None:
        """Every catalog slug appears exactly once as an entry anchor."""
        found: list[str] = re.findall(r"^## entry-(.+)$", directory_text, re.MULTILINE)
        assert sorted(found) == sorted(entry.slug for entry in catalog.skills)

    def test_no_duplicate_slugs(self, directory_text: str) -> None:
        """No entry slug anchor is duplicated."""
        found: list[str] = re.findall(r"^## entry-(.+)$", directory_text, re.MULTILINE)
        assert len(found) == len(set(found))

    def test_every_skill_entry_url_contains_commit_hash(
        self, directory_text: str, catalog: Catalog
    ) -> None:
        """Every skill entry URL includes the pinned commit hash."""
        skills = [entry for entry in catalog.skills if entry.type == "skill"]
        for skill in skills:
            assert SOURCE_COMMIT in skill.entry_url
            assert skill.entry_url in directory_text


class TestMcpServers:
    """Acceptance tests for the MCP server section."""

    def test_mcp_servers_section_lists_entries(
        self, directory_text: str, catalog: Catalog
    ) -> None:
        """The MCP Servers section renders actual MCP server entries."""
        mcp_servers = [entry for entry in catalog.skills if entry.type == "mcp_server"]
        assert len(mcp_servers) == EXPECTED_TOTAL_MCP_SERVERS
        for server in mcp_servers:
            assert f"## entry-{server.slug}" in directory_text
            assert server.name in directory_text
            assert server.entry_url in directory_text

    def test_mcp_servers_section_contains_count(self, directory_text: str) -> None:
        """The MCP Servers section mentions the number of entries."""
        lowered = directory_text.lower()
        assert "no local mcp servers" not in lowered
        assert "no upstream repo mcp servers" not in lowered
        assert f"{EXPECTED_TOTAL_MCP_SERVERS} oracle-themed mcp server" in lowered


class TestNoPlaceholderText:
    """Acceptance tests ensuring no placeholder text remains."""

    def test_no_tbd_or_todo_or_placeholder(self, directory_text: str) -> None:
        """No TBD/TODO/placeholder text remains in the directory."""
        lower = directory_text.lower()
        assert "tbd" not in lower
        assert "todo" not in lower
        assert "placeholder" not in lower


class TestGeneratedArtifacts:
    """Acceptance tests for generated markdown artifacts."""

    def test_catalog_markdown_exists(self) -> None:
        """oracle_skills_catalog.md is generated and non-empty."""
        path = REPO_ROOT / "oracle_skills_catalog.md"
        assert path.exists()
        assert path.stat().st_size > 0

    def test_summary_markdown_exists(self) -> None:
        """oracle_skills_summary.md is generated and non-empty."""
        path = REPO_ROOT / "oracle_skills_summary.md"
        assert path.exists()
        assert path.stat().st_size > 0

    def test_catalog_markdown_links_all_entries(self, catalog: Catalog) -> None:
        """Every catalog slug appears in the generated catalog markdown."""
        text = (REPO_ROOT / "oracle_skills_catalog.md").read_text(encoding="utf-8")
        for entry in catalog.skills:
            assert entry.slug in text
            assert entry.entry_url in text

    def test_summary_markdown_has_counts(self) -> None:
        """The summary markdown contains the expected rollup counts."""
        text = (REPO_ROOT / "oracle_skills_summary.md").read_text(encoding="utf-8")
        total_entries = EXPECTED_TOTAL_SKILLS + EXPECTED_TOTAL_MCP_SERVERS
        assert f"Total entries: {total_entries}" in text
        assert f"Skills: {EXPECTED_TOTAL_SKILLS}" in text
        assert f"MCP servers: {EXPECTED_TOTAL_MCP_SERVERS}" in text
