#!/usr/bin/env python3
"""Validate SKILL.md files in the renga framework.

Standalone wrapper that applies validate_skill_file() from validate_agents.py
to all SKILL.md files in a skills directory.

Usage:
    python3 scripts/validate_skills.py [--skills-dir PATH]

Exit codes:
    0 — all skills valid
    1 — warnings only
    2 — errors
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root or from scripts/
sys.path.insert(0, str(Path(__file__).parent))

from validate_agents import Severity, validate_skill_file  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md files")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(".github/skills"),
        help="Path to the skills directory (default: .github/skills)",
    )
    args = parser.parse_args()

    skills_dir: Path = args.skills_dir
    if not skills_dir.is_dir():
        print(f"❌ Skills directory not found: {skills_dir}", file=sys.stderr)
        return 2

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        print(f"⚠️  No SKILL.md files found in {skills_dir}", file=sys.stderr)
        return 1

    max_severity = Severity.OK
    errors = 0
    warnings = 0

    for sf in skill_files:
        result = validate_skill_file(sf)
        if result.severity > Severity.OK:
            for msg in result.messages:
                print(f"  {sf.parent.name}/SKILL.md: {msg}")
        if result.severity == Severity.ERROR:
            errors += 1
        elif result.severity == Severity.WARNING:
            warnings += 1
        if result.severity > max_severity:
            max_severity = result.severity

    total = len(skill_files)
    print(f"\nSkills validated: {total} | Errors: {errors} | Warnings: {warnings}")

    if max_severity == Severity.ERROR:
        return 2
    if max_severity == Severity.WARNING:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
