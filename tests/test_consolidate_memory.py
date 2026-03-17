"""Tests for scripts/consolidate_memory.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from consolidate_memory import (
    _is_header_row,
    _perf_row_key,
    _consolidate_performance,
    _err_row_key,
    _consolidate_errors,
)


# =========================================================================
# _is_header_row
# =========================================================================


class TestIsHeaderRow:
    """Tests for _is_header_row()."""

    def test_two_keywords_match(self):
        cells = ["Date", "Session", "some-value"]
        assert _is_header_row(cells, ["date", "session", "agent"]) is True

    def test_all_keywords_match(self):
        cells = ["Date", "Session", "Agent", "Note"]
        assert _is_header_row(cells, ["date", "session", "agent", "note"]) is True

    def test_one_keyword_not_enough(self):
        cells = ["Date", "foo", "bar"]
        assert _is_header_row(cells, ["date", "session", "agent"]) is False

    def test_zero_keywords(self):
        cells = ["foo", "bar", "baz"]
        assert _is_header_row(cells, ["date", "session", "agent"]) is False

    def test_case_insensitive(self):
        cells = ["DATE", "session", "AGENT"]
        assert _is_header_row(cells, ["date", "session", "agent"]) is True

    def test_empty_cells(self):
        assert _is_header_row([], ["date", "session"]) is False

    def test_whitespace_in_cells(self):
        cells = ["  Date  ", " Session "]
        assert _is_header_row(cells, ["date", "session"]) is True


# =========================================================================
# _perf_row_key
# =========================================================================


class TestPerfRowKey:
    """Tests for _perf_row_key()."""

    def test_four_or_more_cells(self):
        cells = ["2025-01-01", "sess-1", "backend-dev", "refactor", "8/10", "OK"]
        assert _perf_row_key(cells) == "sess-1||backend-dev||refactor"

    def test_exactly_four_cells(self):
        cells = ["2025-01-01", "sess-2", "qa-engineer", "test"]
        assert _perf_row_key(cells) == "sess-2||qa-engineer||test"

    def test_fewer_than_four_cells(self):
        cells = ["a", "b"]
        assert _perf_row_key(cells) == "a||b"

    def test_empty_list(self):
        assert _perf_row_key([]) == ""

    def test_strips_whitespace(self):
        cells = ["2025-01-01", "  sess-1  ", " agent ", " task "]
        assert _perf_row_key(cells) == "sess-1||agent||task"


# =========================================================================
# _consolidate_performance
# =========================================================================

_PERF_TABLE_HEADER = "| Date | Session | Agent | Tâche | Note | Commentaire |"
_PERF_TABLE_SEP = "|---|---|---|---|---|---|"


def _make_perf_session(path: Path, rows: list[list[str]]) -> Path:
    """Helper: write a markdown performance session file."""
    lines = [_PERF_TABLE_HEADER, _PERF_TABLE_SEP]
    for row in rows:
        padded = row + [""] * (6 - len(row)) if len(row) < 6 else row[:6]
        lines.append("| " + " | ".join(padded) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _make_perf_consolidated(path: Path, rows: list[list[str]], preamble: str = "") -> Path:
    """Helper: write a consolidated performance file with ## Historique section."""
    header = preamble or "# Agent Performance"
    lines = [header, "", "## Historique", "", _PERF_TABLE_HEADER, _PERF_TABLE_SEP]
    for row in rows:
        padded = row + [""] * (6 - len(row)) if len(row) < 6 else row[:6]
        lines.append("| " + " | ".join(padded) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class TestConsolidatePerformance:
    """Tests for _consolidate_performance()."""

    def test_no_session_files(self, tmp_path: Path):
        consolidated = tmp_path / "agent-performance.md"
        assert _consolidate_performance(consolidated, [], dry_run=False) == 0

    def test_one_new_row(self, tmp_path: Path):
        consolidated = tmp_path / "agent-performance.md"
        _make_perf_consolidated(consolidated, [])

        session = _make_perf_session(
            tmp_path / "agent-performance-s1.md",
            [["2025-03-01", "s1", "backend-dev", "create API", "9/10", "bien"]],
        )
        count = _consolidate_performance(consolidated, [session], dry_run=False)
        assert count == 1

        content = consolidated.read_text(encoding="utf-8")
        assert "backend-dev" in content
        assert "create API" in content

    def test_duplicate_row_ignored(self, tmp_path: Path):
        row = ["2025-03-01", "s1", "backend-dev", "create API", "9/10", "bien"]
        consolidated = tmp_path / "agent-performance.md"
        _make_perf_consolidated(consolidated, [row])

        session = _make_perf_session(tmp_path / "agent-performance-s1.md", [row])
        count = _consolidate_performance(consolidated, [session], dry_run=False)
        assert count == 0

    def test_updated_row_counts(self, tmp_path: Path):
        original_row = ["2025-03-01", "s1", "backend-dev", "create API", "7/10", "moyen"]
        updated_row = ["2025-03-01", "s1", "backend-dev", "create API", "9/10", "bien"]

        consolidated = tmp_path / "agent-performance.md"
        _make_perf_consolidated(consolidated, [original_row])

        session = _make_perf_session(tmp_path / "agent-performance-s1.md", [updated_row])
        count = _consolidate_performance(consolidated, [session], dry_run=False)
        assert count == 1

        content = consolidated.read_text(encoding="utf-8")
        assert "9/10" in content

    def test_dry_run_does_not_modify(self, tmp_path: Path):
        consolidated = tmp_path / "agent-performance.md"
        _make_perf_consolidated(consolidated, [])
        original_content = consolidated.read_text(encoding="utf-8")

        session = _make_perf_session(
            tmp_path / "agent-performance-s1.md",
            [["2025-03-01", "s1", "backend-dev", "task", "8/10", "ok"]],
        )
        count = _consolidate_performance(consolidated, [session], dry_run=True)
        assert count == 1
        assert consolidated.read_text(encoding="utf-8") == original_content

    def test_consolidated_file_created_from_scratch(self, tmp_path: Path):
        consolidated = tmp_path / "agent-performance.md"
        assert not consolidated.exists()

        session = _make_perf_session(
            tmp_path / "agent-performance-s1.md",
            [["2025-03-01", "s1", "qa-engineer", "tests", "10/10", "parfait"]],
        )
        count = _consolidate_performance(consolidated, [session], dry_run=False)
        assert count == 1
        assert consolidated.exists()
        assert "qa-engineer" in consolidated.read_text(encoding="utf-8")

    def test_multiple_session_files(self, tmp_path: Path):
        consolidated = tmp_path / "agent-performance.md"
        _make_perf_consolidated(consolidated, [])

        s1 = _make_perf_session(
            tmp_path / "agent-performance-s1.md",
            [["2025-03-01", "s1", "backend-dev", "api", "8/10", ""]],
        )
        s2 = _make_perf_session(
            tmp_path / "agent-performance-s2.md",
            [["2025-03-02", "s2", "frontend-dev", "ui", "7/10", ""]],
        )
        count = _consolidate_performance(consolidated, [s1, s2], dry_run=False)
        assert count == 2


# =========================================================================
# _err_row_key
# =========================================================================


class TestErrRowKey:
    """Tests for _err_row_key()."""

    def test_three_or_more_cells(self):
        cells = ["ERR-001", "Missing null check", "backend-dev", "3", "2025-01-01", "2025-03-01", "Fix"]
        assert _err_row_key(cells) == "ERR-001||Missing null check||backend-dev"

    def test_exactly_three_cells(self):
        cells = ["ERR-002", "Type mismatch", "frontend-dev"]
        assert _err_row_key(cells) == "ERR-002||Type mismatch||frontend-dev"

    def test_fewer_than_three_cells(self):
        cells = ["ERR-003", "Timeout"]
        assert _err_row_key(cells) == "ERR-003||Timeout"

    def test_empty_list(self):
        assert _err_row_key([]) == ""

    def test_strips_whitespace(self):
        cells = ["  ERR-004 ", " Pattern ", "  agent  "]
        assert _err_row_key(cells) == "ERR-004||Pattern||agent"


# =========================================================================
# _consolidate_errors
# =========================================================================

_ERR_ACTIVE_HEADER = "| ID | Pattern | Agent(s) | Occurrences | Première occurrence | Dernière occurrence | Action |"
_ERR_ACTIVE_SEP = "|---|---|---|---|---|---|---|"


def _make_err_session(path: Path, rows: list[list[str]]) -> Path:
    """Helper: write a markdown error-patterns session file."""
    lines = [_ERR_ACTIVE_HEADER, _ERR_ACTIVE_SEP]
    for row in rows:
        padded = row + [""] * (7 - len(row)) if len(row) < 7 else row[:7]
        lines.append("| " + " | ".join(padded) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _make_err_consolidated(
    path: Path,
    active_rows: list[list[str]],
    resolved_section: str = "",
) -> Path:
    """Helper: write a consolidated error-patterns file."""
    lines = ["# Error Patterns", "", "## Patterns actifs", "", _ERR_ACTIVE_HEADER, _ERR_ACTIVE_SEP]
    for row in active_rows:
        padded = row + [""] * (7 - len(row)) if len(row) < 7 else row[:7]
        lines.append("| " + " | ".join(padded) + " |")
    content = "\n".join(lines) + "\n"
    if resolved_section:
        content += "\n" + resolved_section + "\n"
    path.write_text(content, encoding="utf-8")
    return path


class TestConsolidateErrors:
    """Tests for _consolidate_errors()."""

    def test_no_session_files(self, tmp_path: Path):
        consolidated = tmp_path / "error-patterns.md"
        assert _consolidate_errors(consolidated, [], dry_run=False) == 0

    def test_new_error_rows_merged(self, tmp_path: Path):
        consolidated = tmp_path / "error-patterns.md"
        _make_err_consolidated(consolidated, [])

        session = _make_err_session(
            tmp_path / "error-patterns-s1.md",
            [["ERR-010", "NPE in handler", "backend-dev", "2", "2025-01-01", "2025-03-01", "investigate"]],
        )
        count = _consolidate_errors(consolidated, [session], dry_run=False)
        assert count == 1

        content = consolidated.read_text(encoding="utf-8")
        assert "ERR-010" in content
        assert "NPE in handler" in content

    def test_duplicate_higher_occurrence_wins(self, tmp_path: Path):
        existing = ["ERR-010", "NPE in handler", "backend-dev", "2", "2025-01-01", "2025-02-01", "investigate"]
        consolidated = tmp_path / "error-patterns.md"
        _make_err_consolidated(consolidated, [existing])

        higher_occ = ["ERR-010", "NPE in handler", "backend-dev", "5", "2025-01-01", "2025-03-01", "fix"]
        session = _make_err_session(tmp_path / "error-patterns-s1.md", [higher_occ])

        count = _consolidate_errors(consolidated, [session], dry_run=False)
        assert count == 1

        content = consolidated.read_text(encoding="utf-8")
        assert "5" in content

    def test_duplicate_lower_occurrence_still_updates(self, tmp_path: Path):
        existing = ["ERR-010", "NPE in handler", "backend-dev", "5", "2025-01-01", "2025-03-01", "fix"]
        consolidated = tmp_path / "error-patterns.md"
        _make_err_consolidated(consolidated, [existing])

        lower_occ = ["ERR-010", "NPE in handler", "backend-dev", "2", "2025-01-01", "2025-02-01", "investigate"]
        session = _make_err_session(tmp_path / "error-patterns-s1.md", [lower_occ])

        count = _consolidate_errors(consolidated, [session], dry_run=False)
        # The row differs from existing (different values) but occurrence is lower,
        # so new_rows still gets the row — it counts as updated if values differ
        assert count == 1

    def test_dry_run_does_not_modify(self, tmp_path: Path):
        consolidated = tmp_path / "error-patterns.md"
        _make_err_consolidated(consolidated, [])
        original_content = consolidated.read_text(encoding="utf-8")

        session = _make_err_session(
            tmp_path / "error-patterns-s1.md",
            [["ERR-020", "Timeout", "api-gateway", "1", "2025-03-01", "2025-03-01", "monitor"]],
        )
        count = _consolidate_errors(consolidated, [session], dry_run=True)
        assert count == 1
        assert consolidated.read_text(encoding="utf-8") == original_content

    def test_resolved_section_preserved(self, tmp_path: Path):
        resolved = "## Patterns résolus\n\n| ID | Pattern | Résolution |\n|---|---|---|\n| ERR-001 | Old bug | Fixed in v2 |"
        consolidated = tmp_path / "error-patterns.md"
        _make_err_consolidated(consolidated, [], resolved_section=resolved)

        session = _make_err_session(
            tmp_path / "error-patterns-s1.md",
            [["ERR-030", "New issue", "frontend-dev", "1", "2025-03-15", "2025-03-15", "triage"]],
        )
        count = _consolidate_errors(consolidated, [session], dry_run=False)
        assert count == 1

        content = consolidated.read_text(encoding="utf-8")
        assert "## Patterns résolus" in content
        assert "Old bug" in content
        assert "ERR-030" in content

    def test_consolidated_created_from_scratch(self, tmp_path: Path):
        consolidated = tmp_path / "error-patterns.md"
        assert not consolidated.exists()

        session = _make_err_session(
            tmp_path / "error-patterns-s1.md",
            [["ERR-040", "Race condition", "debugger", "3", "2025-02-01", "2025-03-01", "fix"]],
        )
        count = _consolidate_errors(consolidated, [session], dry_run=False)
        assert count == 1
        assert consolidated.exists()
        assert "Race condition" in consolidated.read_text(encoding="utf-8")
