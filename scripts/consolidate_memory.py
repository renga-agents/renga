#!/usr/bin/env python3
"""Consolidate per-session agent-performance and error-patterns files.

In multi-developer environments, each orchestrator session writes to
per-session files (e.g. agent-performance-<slug>.md, error-patterns-<slug>.md).
This script merges them back into the consolidated files and optionally removes
the per-session fragments.

Usage:
    python scripts/consolidate_memory.py
    python scripts/consolidate_memory.py --dry-run
    python scripts/consolidate_memory.py --keep
    python scripts/consolidate_memory.py --memory-dir .copilot/memory/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_parser import parse_markdown_table


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _is_header_row(cells: list[str], keywords: list[str]) -> bool:
    """Check if the row is a table header by matching cell values (not substrings)."""
    lowered = [c.strip().lower() for c in cells]
    return sum(1 for c in lowered if c in keywords) >= 2


# ---------------------------------------------------------------------------
# Agent-performance consolidation
# ---------------------------------------------------------------------------

_PERF_HEADER_KW = ["date", "session", "agent", "note"]
_PERF_TABLE_HEADER = "| Date | Session | Agent | Tâche | Note | Commentaire |"
_PERF_TABLE_SEP = "|---|---|---|---|---|---|"


def _perf_row_key(cells: list[str]) -> str:
    """Dedup key: (session, agent, tâche)."""
    if len(cells) >= 4:
        return f"{cells[1].strip()}||{cells[2].strip()}||{cells[3].strip()}"
    return "||".join(cells)


def _consolidate_performance(
    consolidated_path: Path,
    session_files: list[Path],
    dry_run: bool,
) -> int:
    """Merge per-session performance files into the consolidated one.

    Returns the number of new rows added.
    """
    original = consolidated_path.read_text(encoding="utf-8") if consolidated_path.exists() else ""

    # Split the file at "## Historique" — everything before is the preamble
    hist_marker = "## Historique"
    if hist_marker in original:
        marker_pos = original.index(hist_marker)
        preamble = original[: marker_pos + len(hist_marker)]
        history_section = original[marker_pos + len(hist_marker) :]
    else:
        preamble = original.rstrip()
        history_section = ""

    # Parse existing rows in the history section only
    existing_rows: dict[str, list[str]] = {}
    for row in parse_markdown_table(history_section, skip_header=False):
        if _is_header_row(row, _PERF_HEADER_KW):
            continue
        if all(c == "" for c in row):
            continue
        existing_rows[_perf_row_key(row)] = row

    # Collect rows from session files (later files win on duplicates)
    new_rows: dict[str, list[str]] = {}
    for sf in sorted(session_files):
        for row in parse_markdown_table(sf.read_text(encoding="utf-8"), skip_header=False):
            if _is_header_row(row, _PERF_HEADER_KW):
                continue
            if all(c == "" for c in row):
                continue
            new_rows[_perf_row_key(row)] = row

    # Determine truly new entries
    added = {k: v for k, v in new_rows.items() if k not in existing_rows}
    updated = {k: v for k, v in new_rows.items() if k in existing_rows and v != existing_rows[k]}

    if not added and not updated:
        return 0

    if dry_run:
        return len(added) + len(updated)

    # Merge: existing (with updates applied) + added
    merged = dict(existing_rows)
    merged.update(new_rows)

    # Rebuild: preamble + table
    out_lines = [preamble.rstrip(), "", _PERF_TABLE_HEADER, _PERF_TABLE_SEP]
    for row in merged.values():
        padded = row + [""] * (6 - len(row)) if len(row) < 6 else row[:6]
        out_lines.append("| " + " | ".join(padded) + " |")

    consolidated_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return len(added) + len(updated)


# ---------------------------------------------------------------------------
# Error-patterns consolidation
# ---------------------------------------------------------------------------

_ERR_HEADER_KW = ["id", "pattern", "agent", "occurrences"]


def _err_row_key(cells: list[str]) -> str:
    """Dedup key: (ID, Pattern, Agent(s))."""
    if len(cells) >= 3:
        return f"{cells[0].strip()}||{cells[1].strip()}||{cells[2].strip()}"
    return "||".join(cells)


_ERR_ACTIVE_HEADER = "| ID | Pattern | Agent(s) | Occurrences | Première occurrence | Dernière occurrence | Action |"
_ERR_ACTIVE_SEP = "|---|---|---|---|---|---|---|"


def _consolidate_errors(
    consolidated_path: Path,
    session_files: list[Path],
    dry_run: bool,
) -> int:
    """Merge per-session error-patterns files into the consolidated one.

    Returns the number of new/updated rows.
    """
    original = consolidated_path.read_text(encoding="utf-8") if consolidated_path.exists() else ""

    # Split at "## Patterns actifs" and "## Patterns résolus"
    active_marker = "## Patterns actifs"
    resolved_marker = "## Patterns résolus"

    if active_marker in original:
        marker_pos = original.index(active_marker)
        preamble = original[: marker_pos + len(active_marker)]
        rest = original[marker_pos + len(active_marker) :]
    else:
        preamble = original.rstrip()
        rest = ""

    # Extract resolved section if present
    resolved_section = ""
    active_section = rest
    if resolved_marker in rest:
        resolved_pos = rest.index(resolved_marker)
        active_section = rest[:resolved_pos]
        resolved_section = rest[resolved_pos:]

    existing_rows: dict[str, list[str]] = {}
    for row in parse_markdown_table(active_section, skip_header=False):
        if _is_header_row(row, _ERR_HEADER_KW):
            continue
        if all(c == "" for c in row):
            continue
        existing_rows[_err_row_key(row)] = row

    new_rows: dict[str, list[str]] = {}
    for sf in sorted(session_files):
        for row in parse_markdown_table(sf.read_text(encoding="utf-8"), skip_header=False):
            if _is_header_row(row, _ERR_HEADER_KW):
                continue
            if all(c == "" for c in row):
                continue
            key = _err_row_key(row)
            if key in new_rows or key in existing_rows:
                prev = new_rows.get(key) or existing_rows.get(key)
                if prev and len(row) >= 4 and len(prev) >= 4:
                    try:
                        if int(row[3].strip()) >= int(prev[3].strip()):
                            new_rows[key] = row
                            continue
                    except ValueError:
                        pass
            new_rows[key] = row

    added = {k: v for k, v in new_rows.items() if k not in existing_rows}
    updated = {k: v for k, v in new_rows.items() if k in existing_rows and v != existing_rows[k]}

    if not added and not updated:
        return 0

    if dry_run:
        return len(added) + len(updated)

    merged = dict(existing_rows)
    merged.update(new_rows)

    out_lines = [preamble.rstrip(), "", _ERR_ACTIVE_HEADER, _ERR_ACTIVE_SEP]
    for row in merged.values():
        padded = row + [""] * (7 - len(row)) if len(row) < 7 else row[:7]
        out_lines.append("| " + " | ".join(padded) + " |")

    content = "\n".join(out_lines) + "\n"
    if resolved_section:
        content += "\n" + resolved_section.strip() + "\n"

    consolidated_path.write_text(content, encoding="utf-8")
    return len(added) + len(updated)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolidate per-session memory files into their main counterparts.",
    )
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=Path(".copilot/memory"),
        help="Path to the memory directory (default: .copilot/memory/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Do not delete per-session files after consolidation.",
    )
    args = parser.parse_args()

    memory_dir: Path = args.memory_dir
    if not memory_dir.is_dir():
        print(f"Error: memory directory not found: {memory_dir}", file=sys.stderr)
        sys.exit(1)

    mode_label = "[DRY-RUN] " if args.dry_run else ""

    # --- agent-performance ---
    perf_consolidated = memory_dir / "agent-performance.md"
    perf_sessions = sorted(memory_dir.glob("agent-performance-*.md"))
    perf_count = 0
    if perf_sessions:
        perf_count = _consolidate_performance(perf_consolidated, perf_sessions, args.dry_run)
        print(f"{mode_label}agent-performance: {perf_count} row(s) merged from {len(perf_sessions)} session file(s)")
        for sf in perf_sessions:
            print(f"  <- {sf.name}")
        if not args.dry_run and not args.keep:
            for sf in perf_sessions:
                if sf.is_symlink():
                    print(f"  ⚠️  Skipping symlink: {sf}")
                    continue
                sf.unlink()
                print(f"  [deleted] {sf.name}")
    else:
        print(f"{mode_label}agent-performance: no session files found")

    # --- error-patterns ---
    err_consolidated = memory_dir / "error-patterns.md"
    err_sessions = sorted(memory_dir.glob("error-patterns-*.md"))
    err_count = 0
    if err_sessions:
        err_count = _consolidate_errors(err_consolidated, err_sessions, args.dry_run)
        print(f"{mode_label}error-patterns: {err_count} row(s) merged from {len(err_sessions)} session file(s)")
        for sf in err_sessions:
            print(f"  <- {sf.name}")
        if not args.dry_run and not args.keep:
            for sf in err_sessions:
                if sf.is_symlink():
                    print(f"  ⚠️  Skipping symlink: {sf}")
                    continue
                sf.unlink()
                print(f"  [deleted] {sf.name}")
    else:
        print(f"{mode_label}error-patterns: no session files found")

    # --- Summary ---
    total = perf_count + err_count
    if total == 0 and not perf_sessions and not err_sessions:
        print("\nNothing to consolidate.")
    elif args.dry_run:
        print(f"\n{mode_label}Total: {total} row(s) would be merged. Re-run without --dry-run to apply.")
    else:
        print(f"\nDone. {total} row(s) merged.")


if __name__ == "__main__":
    main()
