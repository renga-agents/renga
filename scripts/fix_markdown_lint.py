#!/usr/bin/env python3
"""Fix mechanical markdown lint warnings in .agent.md and reference files.

Fixes: MD009, MD012, MD022, MD026, MD031, MD032, MD036, MD040, MD047, MD058, MD060
Applied in a safe order to avoid interference.
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Individual fixers — each takes a list of lines and returns a new list
# ---------------------------------------------------------------------------


def _in_frontmatter(lines: list[str], idx: int) -> bool:
    """Return True if line at idx is inside YAML frontmatter (between --- delimiters).

    Frontmatter only exists when the very first line of the file is ---.
    """
    if not lines or lines[0].rstrip() != "---":
        return False
    fence_count = 0
    for i in range(idx):
        if lines[i].rstrip() == "---":
            fence_count += 1
    return fence_count == 1  # between first and second ---


def _in_fenced_code_block(lines: list[str], idx: int) -> bool:
    """Return True if line at idx is inside a fenced code block."""
    in_code = False
    for i in range(idx):
        stripped = re.sub(r"^(\s*>\s*)*", "", lines[i]).strip()
        if stripped.startswith("```"):
            in_code = not in_code
    return in_code


def fix_md047(lines: list[str]) -> tuple[list[str], int]:
    """Ensure file ends with exactly one trailing newline."""
    count = 0
    if not lines:
        return lines, 0

    # Strip trailing empty lines
    while len(lines) > 1 and lines[-1].strip() == "":
        lines.pop()
        count += 1

    # Ensure last line ends with \n
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
        count += 1

    # Add exactly one trailing newline (empty line at end)
    if lines and lines[-1].strip() != "":
        lines.append("\n")
        count += 1

    return lines, max(count, 0)


def fix_md060(lines: list[str]) -> tuple[list[str], int]:
    """Fix table separator rows: |---|---| → | --- | --- |."""
    count = 0
    table_sep_re = re.compile(r"^(\s*(?:>\s*)*)(\|[-:|]+(?:\|[-:|]+)+\|)\s*$")

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            continue
        m = table_sep_re.match(line)
        if not m:
            continue
        prefix = m.group(1)
        sep_part = m.group(2)

        # Check if it needs fixing (no spaces around ---)
        if "| ---" in sep_part or "--- |" in sep_part:
            # Might already be partially fixed, check if all cells are spaced
            cells = sep_part.split("|")[1:-1]  # drop first/last empty
            needs_fix = any(not c.startswith(" ") or not c.endswith(" ") for c in cells)
            if not needs_fix:
                continue

        # Split by |, fix each cell
        cells = sep_part.split("|")[1:-1]
        fixed_cells = []
        for cell in cells:
            cell_stripped = cell.strip()
            if re.match(r"^:?-+:?$", cell_stripped):
                fixed_cells.append(f" {cell_stripped} ")
            else:
                fixed_cells.append(cell)

        new_sep = "|" + "|".join(fixed_cells) + "|"
        new_line = prefix + new_sep + "\n"
        if new_line != line:
            lines[i] = new_line
            count += 1

    return lines, count


def fix_md036(lines: list[str]) -> tuple[list[str], int]:
    """Convert bold-only lines to ### headings."""
    count = 0
    bold_line_re = re.compile(r"^(\s*(?:>\s*)*)\*\*(.+)\*\*\s*$")

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            continue
        m = bold_line_re.match(line)
        if not m:
            continue

        prefix = m.group(1)  # blockquote prefix if any
        content = m.group(2)

        # Only convert if the line is ONLY bold (no other text on the line)
        # Check that content doesn't contain nested bold markers
        if "**" in content:
            continue

        lines[i] = f"{prefix}### {content}\n"
        count += 1

    return lines, count


def fix_md022(lines: list[str]) -> tuple[list[str], int]:
    """Ensure blank lines around headings."""
    count = 0
    heading_re = re.compile(r"^(\s*(?:>\s*)*)(#{1,6})\s+")
    result: list[str] = []

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            result.append(line)
            continue

        m = heading_re.match(line)
        if not m:
            result.append(line)
            continue

        prefix = m.group(1)  # blockquote prefix

        # Determine the "blank" line for this context
        if prefix.rstrip():
            blank = prefix.rstrip() + "\n"
        else:
            blank = "\n"

        # Check if previous line is blank (or start of file or frontmatter end)
        if result:
            prev = result[-1]
            prev_stripped = prev.strip()
            # Previous must be empty or blockquote-empty
            is_prev_blank = prev_stripped == "" or prev_stripped == ">" or prev_stripped == prefix.rstrip()
            is_prev_frontmatter = prev_stripped == "---"
            if not is_prev_blank and not is_prev_frontmatter:
                result.append(blank)
                count += 1

        result.append(line)

        # Check if next line is blank
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            is_next_blank = next_stripped == "" or next_stripped == ">" or next_stripped == prefix.rstrip()
            if not is_next_blank and not _in_frontmatter(lines, i + 1):
                result.append(blank)
                count += 1

    return result, count


def fix_md031(lines: list[str]) -> tuple[list[str], int]:
    """Ensure blank lines around fenced code blocks."""
    count = 0
    result: list[str] = []

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i):
            result.append(line)
            continue

        # Detect code fence (possibly inside blockquote or list indent)
        stripped_for_fence = re.sub(r"^(\s*>\s*)*", "", line).strip()
        bq_match = re.match(r"^(\s*(?:>\s*)*)", line)
        prefix = bq_match.group(1) if bq_match else ""

        if stripped_for_fence.startswith("```"):
            # Determine blank line for this context
            if prefix.rstrip():
                blank = prefix.rstrip() + "\n"
            else:
                blank = "\n"

            # Check if previous line needs a blank
            if result:
                prev = result[-1]
                prev_stripped = prev.strip()
                is_prev_blank = prev_stripped == "" or prev_stripped == ">" or prev_stripped == prefix.rstrip()
                is_prev_frontmatter = prev_stripped == "---"
                if not is_prev_blank and not is_prev_frontmatter:
                    result.append(blank)
                    count += 1

            result.append(line)

            # Check if next line needs a blank
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                is_next_blank = next_stripped == "" or next_stripped == ">" or next_stripped == prefix.rstrip()
                if not is_next_blank and not _in_frontmatter(lines, i + 1):
                    result.append(blank)
                    count += 1
        else:
            result.append(line)

    return result, count


def fix_md032(lines: list[str]) -> tuple[list[str], int]:
    """Ensure blank lines around lists."""
    count = 0
    result: list[str] = []
    list_item_re = re.compile(r"^(\s*(?:>\s*)*)[-*+]\s+")
    ordered_re = re.compile(r"^(\s*(?:>\s*)*)\d+[.)]\s+")

    def is_list_line(line: str) -> bool:
        return bool(list_item_re.match(line)) or bool(ordered_re.match(line))

    def get_prefix(line: str) -> str:
        m = re.match(r"^(\s*(?:>\s*)*)", line)
        return m.group(1) if m else ""

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            result.append(line)
            continue

        if is_list_line(line):
            prefix = get_prefix(line)
            if prefix.rstrip():
                blank = prefix.rstrip() + "\n"
            else:
                blank = "\n"

            # First item of a list: need blank before
            prev_is_list = i > 0 and is_list_line(lines[i - 1])
            # Also check if prev is a continuation (indented under list)
            if not prev_is_list and result:
                prev = result[-1]
                prev_stripped = prev.strip()
                is_prev_blank = prev_stripped == "" or prev_stripped == ">" or prev_stripped == prefix.rstrip()
                is_prev_frontmatter = prev_stripped == "---"
                if not is_prev_blank and not is_prev_frontmatter:
                    result.append(blank)
                    count += 1

            result.append(line)

            # Last item of a list: need blank after
            next_is_list = i + 1 < len(lines) and is_list_line(lines[i + 1])
            # Also consider continuation lines (indented under list item)
            if not next_is_list and i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                is_next_blank = next_stripped == "" or next_stripped == ">" or next_stripped == prefix.rstrip()
                # Check if next is a continuation line (indented more than the list marker)
                is_continuation = next_line.startswith("  ") and not next_stripped.startswith("#")
                if not is_next_blank and not is_continuation and not _in_frontmatter(lines, i + 1):
                    result.append(blank)
                    count += 1
        else:
            result.append(line)

    return result, count


def fix_md009(lines: list[str]) -> tuple[list[str], int]:
    """Remove trailing whitespace from lines (excluding blank lines and frontmatter)."""
    count = 0
    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i):
            continue
        # Strip trailing whitespace while preserving the newline
        if line.endswith("\n"):
            stripped = line.rstrip() + "\n"
        else:
            stripped = line.rstrip()
        if stripped != line:
            lines[i] = stripped
            count += 1
    return lines, count


def fix_md026(lines: list[str]) -> tuple[list[str], int]:
    """Remove trailing punctuation (.,;:!?) from headings."""
    count = 0
    heading_re = re.compile(r"^(\s*(?:>\s*)*#{1,6}\s+.+?)([.,;:!?]+)(\s*)$")
    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            continue
        m = heading_re.match(line.rstrip("\n"))
        if m:
            lines[i] = m.group(1) + "\n"
            count += 1
    return lines, count


def fix_md040(lines: list[str]) -> tuple[list[str], int]:
    """Add 'text' language specifier to opening fenced code blocks that have none."""
    count = 0
    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i):
            continue
        # Strip blockquote/indent prefix to check the fence itself
        stripped = re.sub(r"^(\s*>\s*)*", "", line).strip()
        # Opening fence = exactly ``` with no language, and not already inside a block
        if stripped == "```" and not _in_fenced_code_block(lines, i):
            bq_match = re.match(r"^(\s*(?:>\s*)*)", line)
            prefix = bq_match.group(1) if bq_match else ""
            lines[i] = prefix + "```text\n"
            count += 1
    return lines, count


def fix_md012(lines: list[str]) -> tuple[list[str], int]:
    """Remove multiple consecutive blank lines, keeping at most one."""
    count = 0
    result: list[str] = []
    for line in lines:
        if line.strip() == "" or line.strip() == ">":
            if result and (result[-1].strip() == "" or result[-1].strip() == ">"):
                if result[-1].strip() == line.strip():
                    count += 1
                    continue
        result.append(line)
    return result, count


def fix_md058(lines: list[str]) -> tuple[list[str], int]:
    """Ensure blank lines around tables."""
    count = 0
    result: list[str] = []
    table_line_re = re.compile(r"^(\s*(?:>\s*)*)\|.+\|")

    def is_table_line(line: str) -> bool:
        return bool(table_line_re.match(line))

    for i, line in enumerate(lines):
        if _in_frontmatter(lines, i) or _in_fenced_code_block(lines, i):
            result.append(line)
            continue

        if is_table_line(line):
            bq_match = re.match(r"^(\s*(?:>\s*)*)", line)
            prefix = bq_match.group(1) if bq_match else ""

            if prefix.rstrip():
                blank = prefix.rstrip() + "\n"
            else:
                blank = "\n"

            # First row of table: need blank before
            prev_is_table = i > 0 and is_table_line(lines[i - 1])
            if not prev_is_table and result:
                prev = result[-1]
                prev_stripped = prev.strip()
                is_prev_blank = prev_stripped == "" or prev_stripped == ">" or prev_stripped == prefix.rstrip()
                is_prev_frontmatter = prev_stripped == "---"
                if not is_prev_blank and not is_prev_frontmatter:
                    result.append(blank)
                    count += 1

            result.append(line)

            # Last row of table: need blank after
            next_is_table = i + 1 < len(lines) and is_table_line(lines[i + 1])
            if not next_is_table and i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                is_next_blank = next_stripped == "" or next_stripped == ">" or next_stripped == prefix.rstrip()
                if not is_next_blank and not _in_frontmatter(lines, i + 1):
                    result.append(blank)
                    count += 1
        else:
            result.append(line)

    return result, count


def _remove_double_blanks(lines: list[str]) -> list[str]:
    """Remove consecutive blank lines, keeping at most one."""
    result: list[str] = []
    for line in lines:
        if line.strip() == "" or line.strip() == ">":
            if result and (result[-1].strip() == "" or result[-1].strip() == ">"):
                # Check if both are the same type of blank (both empty or both >)
                if result[-1].strip() == line.strip():
                    continue
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

FIXERS = [
    ("MD009", fix_md009),   # trailing spaces — independent, run first
    ("MD026", fix_md026),   # trailing heading punctuation — independent
    ("MD040", fix_md040),   # fenced code language — independent
    ("MD047", fix_md047),   # trailing newline
    ("MD060", fix_md060),   # table separator spacing
    ("MD036", fix_md036),   # bold-only lines → headings
    ("MD022", fix_md022),   # blank lines around headings (may add blanks)
    ("MD031", fix_md031),   # blank lines around code blocks (may add blanks)
    ("MD032", fix_md032),   # blank lines around lists (may add blanks)
    ("MD058", fix_md058),   # blank lines around tables (may add blanks)
    ("MD012", fix_md012),   # consecutive blank lines — must run last
]


def process_file(filepath: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Apply all fixes to a single file. Returns dict of rule -> count."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Handle empty files
    if not lines:
        return {}

    stats: dict[str, int] = {}
    for rule_name, fixer in FIXERS:
        lines, n = fixer(lines)
        if n > 0:
            stats[rule_name] = n

    # Final MD047: ensure exactly one trailing newline
    while len(lines) > 1 and lines[-1].strip() == "":
        lines.pop()
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    new_content = "".join(lines)

    if new_content != content:
        if not dry_run:
            filepath.write_text(new_content, encoding="utf-8")
        return stats
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix markdown lint warnings in agent files")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".github/agents",
        help="Directory to process (default: .github/agents)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files")
    args = parser.parse_args()

    target = Path(args.directory)
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(target.rglob("*.md"))
    if not md_files:
        print(f"No .md files found in {target}")
        return

    total_fixes: dict[str, int] = {}
    modified_files: list[str] = []

    mode = "DRY RUN" if args.dry_run else "FIXING"
    print(f"[{mode}] Processing {len(md_files)} markdown files in {target}/\n")

    for filepath in md_files:
        stats = process_file(filepath, dry_run=args.dry_run)
        if stats:
            modified_files.append(str(filepath))
            detail = ", ".join(f"{k}: {v}" for k, v in stats.items())
            print(f"  ✓ {filepath.relative_to(target)} — {detail}")
            for k, v in stats.items():
                total_fixes[k] = total_fixes.get(k, 0) + v

    print(f"\n{'=' * 60}")
    print(f"Files modified: {len(modified_files)}/{len(md_files)}")
    if total_fixes:
        print("Fixes applied:")
        for rule, n in sorted(total_fixes.items()):
            print(f"  {rule}: {n}")
        print(f"  TOTAL: {sum(total_fixes.values())}")
    else:
        print("No fixes needed.")


if __name__ == "__main__":
    main()
