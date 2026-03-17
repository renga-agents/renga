"""Tests for scripts/generate_dashboard.py.

Covers:
- parse_markdown_table (shared version in agent_parser.py)
- parse_performance: PerformanceEntry extraction from Markdown
- parse_error_patterns: active / resolved error pattern extraction
- generate_dashboard: Markdown report generation

Run:
    python -m pytest tests/test_generate_dashboard.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_dashboard import (
    PerformanceEntry,
    ErrorPattern,
    generate_dashboard,
    parse_error_patterns,
    parse_performance,
)
from agent_parser import parse_markdown_table


# =========================================================================
# parse_markdown_table  (agent_parser — shared version)
# =========================================================================

class TestParseMarkdownTable:
    """Tests for parse_markdown_table() — Markdown table data-row extraction."""

    def test_empty_string(self):
        assert parse_markdown_table("") == []

    def test_text_without_table(self):
        text = "Just some text\nNo table here\n"
        assert parse_markdown_table(text) == []

    def test_single_data_row(self):
        text = (
            "| Name | Score |\n"
            "|---|---|\n"
            "| alice | 5 |\n"
        )
        result = parse_markdown_table(text)
        assert result == [["alice", "5"]]

    def test_multiple_data_rows(self):
        text = (
            "| Name | Score | Comment |\n"
            "|---|---|---|\n"
            "| alice | 5 | great |\n"
            "| bob | 3 | ok |\n"
            "| charlie | 4 | good |\n"
        )
        result = parse_markdown_table(text)
        assert len(result) == 3
        assert result[0] == ["alice", "5", "great"]
        assert result[2] == ["charlie", "4", "good"]

    def test_blank_rows_skipped(self):
        text = (
            "| H1 | H2 |\n"
            "|---|---|\n"
            "|  |  |\n"
            "| val | val2 |\n"
        )
        result = parse_markdown_table(text)
        assert result == [["val", "val2"]]

    def test_skip_header_false_includes_header(self):
        text = (
            "| Name | Score |\n"
            "|---|---|\n"
            "| alice | 5 |\n"
        )
        result = parse_markdown_table(text, skip_header=False)
        assert len(result) == 2
        assert result[0] == ["Name", "Score"]
        assert result[1] == ["alice", "5"]

    def test_separator_with_colons(self):
        """Tables with alignment markers (e.g. |:---|---:|) are still parsed."""
        text = (
            "| Left | Right |\n"
            "|:---|---:|\n"
            "| a | b |\n"
        )
        result = parse_markdown_table(text)
        assert result == [["a", "b"]]


# =========================================================================
# parse_performance
# =========================================================================

class TestParsePerformance:
    """Tests for parse_performance() — agent-performance.md parsing."""

    def test_missing_file(self, tmp_path: Path):
        result = parse_performance(tmp_path / "nonexistent.md")
        assert result == []

    def test_valid_entries(self, tmp_path: Path):
        content = (
            "# Performance\n\n"
            "## Historique\n\n"
            "| Date | Session | Agent | Tâche | Score | Commentaire |\n"
            "|---|---|---|---|---|---|\n"
            "| 2026-03-10 | S-001 | backend-dev | impl-api | 4 | Good |\n"
            "| 2026-03-11 | S-002 | frontend-dev | ui-fix | 5 | Excellent |\n"
        )
        path = tmp_path / "agent-performance.md"
        path.write_text(content, encoding="utf-8")

        entries = parse_performance(path)
        assert len(entries) == 2
        assert entries[0].agent == "backend-dev"
        assert entries[0].score == 4
        assert entries[0].comment == "Good"
        assert entries[1].score == 5

    def test_non_int_score_skipped(self, tmp_path: Path):
        content = (
            "## Historique\n\n"
            "| Date | Session | Agent | Tâche | Score |\n"
            "|---|---|---|---|---|\n"
            "| 2026-03-10 | S-001 | agent-a | task | N/A |\n"
            "| 2026-03-11 | S-002 | agent-b | task | 3 |\n"
        )
        path = tmp_path / "perf.md"
        path.write_text(content, encoding="utf-8")

        entries = parse_performance(path)
        assert len(entries) == 1
        assert entries[0].agent == "agent-b"

    def test_fewer_than_5_columns_skipped(self, tmp_path: Path):
        content = (
            "## Historique\n\n"
            "| Date | Session | Agent |\n"
            "|---|---|---|\n"
            "| 2026-03-10 | S-001 | only-three |\n"
        )
        path = tmp_path / "perf.md"
        path.write_text(content, encoding="utf-8")

        entries = parse_performance(path)
        assert entries == []

    def test_six_columns_comment_parsed(self, tmp_path: Path):
        content = (
            "## Historique\n\n"
            "| Date | Session | Agent | Tâche | Score | Commentaire |\n"
            "|---|---|---|---|---|---|\n"
            "| 2026-03-10 | S-001 | qa | review | 5 | Parfait |\n"
        )
        path = tmp_path / "perf.md"
        path.write_text(content, encoding="utf-8")

        entries = parse_performance(path)
        assert len(entries) == 1
        assert entries[0].comment == "Parfait"

    def test_five_columns_empty_comment(self, tmp_path: Path):
        content = (
            "## Historique\n\n"
            "| Date | Session | Agent | Tâche | Score |\n"
            "|---|---|---|---|---|\n"
            "| 2026-03-10 | S-001 | devops | deploy | 3 |\n"
        )
        path = tmp_path / "perf.md"
        path.write_text(content, encoding="utf-8")

        entries = parse_performance(path)
        assert len(entries) == 1
        assert entries[0].comment == ""


# =========================================================================
# parse_error_patterns
# =========================================================================

class TestParseErrorPatterns:
    """Tests for parse_error_patterns() — error-patterns.md parsing."""

    def test_missing_file(self, tmp_path: Path):
        active, resolved = parse_error_patterns(tmp_path / "nope.md")
        assert active == []
        assert resolved == []

    def test_active_and_resolved_patterns(self, tmp_path: Path):
        content = (
            "# Error Patterns\n\n"
            "## Patterns actifs\n\n"
            "| ID | Pattern | Agents | Occurrences | First | Last | Action |\n"
            "|---|---|---|---|---|---|---|\n"
            "| ERR-001 | Timeout on deploy | devops | 5 | 2026-01 | 2026-03 | retry |\n"
            "\n"
            "## Patterns résolus\n\n"
            "| ID | Pattern | Résolution | Date |\n"
            "|---|---|---|---|\n"
            "| ERR-000 | Old bug | Fixed in v2 | 2025-12 |\n"
        )
        path = tmp_path / "error-patterns.md"
        path.write_text(content, encoding="utf-8")

        active, resolved = parse_error_patterns(path)

        assert len(active) == 1
        assert active[0].pattern_id == "ERR-001"
        assert active[0].pattern == "Timeout on deploy"
        assert active[0].agents == ["devops"]
        assert active[0].occurrences == 5
        assert active[0].action == "retry"

        assert len(resolved) == 1
        assert resolved[0]["id"] == "ERR-000"
        assert resolved[0]["resolution"] == "Fixed in v2"

    def test_active_pattern_non_int_occurrences_skipped(self, tmp_path: Path):
        content = (
            "## Patterns actifs\n\n"
            "| ID | Pattern | Agents | Occurrences | First | Last | Action |\n"
            "|---|---|---|---|---|---|---|\n"
            "| ERR-X | Bad | agent | many | 2026-01 | 2026-02 | tbd |\n"
            "| ERR-Y | Good | agent | 3 | 2026-01 | 2026-02 | fix |\n"
        )
        path = tmp_path / "errors.md"
        path.write_text(content, encoding="utf-8")

        active, _ = parse_error_patterns(path)
        assert len(active) == 1
        assert active[0].pattern_id == "ERR-Y"

    def test_resolved_with_three_columns(self, tmp_path: Path):
        content = (
            "## Patterns résolus\n\n"
            "| ID | Pattern | Résolution |\n"
            "|---|---|---|\n"
            "| ERR-R1 | Stale cache | Purge script added |\n"
        )
        path = tmp_path / "errors.md"
        path.write_text(content, encoding="utf-8")

        _, resolved = parse_error_patterns(path)
        assert len(resolved) == 1
        assert resolved[0]["id"] == "ERR-R1"
        assert resolved[0]["pattern"] == "Stale cache"
        assert resolved[0]["resolution"] == "Purge script added"
        assert resolved[0]["date"] == ""

    def test_multiple_agents_comma_separated(self, tmp_path: Path):
        content = (
            "## Patterns actifs\n\n"
            "| ID | Pattern | Agents | Occ | First | Last | Action |\n"
            "|---|---|---|---|---|---|---|\n"
            "| ERR-M | Multi | frontend-dev, backend-dev | 2 | 2026-01 | 2026-02 | review |\n"
        )
        path = tmp_path / "errors.md"
        path.write_text(content, encoding="utf-8")

        active, _ = parse_error_patterns(path)
        assert len(active) == 1
        assert active[0].agents == ["frontend-dev", "backend-dev"]


# =========================================================================
# generate_dashboard
# =========================================================================

class TestGenerateDashboard:
    """Tests for generate_dashboard() — Markdown report generation."""

    def test_no_data(self):
        report = generate_dashboard([], [], [])
        assert "Pas de données" in report
        assert "KPIs globaux" not in report

    def test_with_entries_contains_kpis_and_ranking(self):
        entries = [
            PerformanceEntry("2026-03-10", "S1", "agent-a", "task1", 4, ""),
            PerformanceEntry("2026-03-11", "S2", "agent-b", "task2", 5, ""),
            PerformanceEntry("2026-03-12", "S3", "agent-a", "task3", 3, ""),
        ]
        report = generate_dashboard(entries, [], [])
        assert "KPIs globaux" in report
        assert "Classement des agents" in report
        assert "Tendance par agent" in report
        assert "agent-a" in report
        assert "agent-b" in report

    def test_with_active_errors(self):
        errors = [
            ErrorPattern("ERR-1", "timeout", ["devops"], 3, "2026-01", "2026-03", "retry"),
        ]
        report = generate_dashboard([], errors, [])
        assert "Patterns d'erreur les plus fréquents" in report
        assert "ERR-1" in report
        assert "timeout" in report

    def test_with_resolved_errors(self):
        resolved = [
            {"id": "ERR-0", "pattern": "old bug", "resolution": "fixed", "date": "2025-12"},
        ]
        entries = [
            PerformanceEntry("2026-03-10", "S1", "agent-a", "task1", 4, ""),
        ]
        report = generate_dashboard(entries, [], resolved)
        assert "Patterns résolus" in report
        assert "ERR-0" in report

    def test_retry_rate_computed(self):
        entries = [
            PerformanceEntry("d1", "s1", "a", "t1", 1, ""),
            PerformanceEntry("d2", "s2", "a", "t2", 2, ""),
            PerformanceEntry("d3", "s3", "a", "t3", 5, ""),
            PerformanceEntry("d4", "s4", "a", "t4", 4, ""),
        ]
        report = generate_dashboard(entries, [], [])
        # 2 out of 4 have score ≤ 2 → 50.0%
        assert "50.0%" in report
