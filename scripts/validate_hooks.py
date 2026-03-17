#!/usr/bin/env python3
"""Validate .hooks.json files and referenced scripts in renga framework.

Scans all *.hooks.json files under .github/hooks/ and validates:
- JSON syntax and required fields (version, hooks)
- Hook types against the known set
- Hook entry fields (command, description)
- Referenced script existence, permissions and shebang
- Orphan scripts not referenced by any hook JSON

Usage:
    python3 scripts/validate_hooks.py [--hooks-dir PATH] [--verbose]

Exit codes:
    0 — all hooks valid
    1 — warnings only
    2 — errors found
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_HOOK_TYPES: set[str] = {
    "sessionStart",
    "sessionEnd",
    "userPromptSubmitted",
    "preToolUse",
    "postToolUse",
    "agentStop",
    "subagentStop",
    "errorOccurred",
}

# Regex to extract script paths from command strings like "bash .github/hooks/scripts/foo.sh"
_SCRIPT_PATH_RE = re.compile(r"(\S+\.sh)\b")

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    severity: Severity
    message: str
    path: Path | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_script_paths(command: str) -> list[str]:
    """Extract .sh script paths from a hook command string."""
    return _SCRIPT_PATH_RE.findall(command)


def _collect_referenced_scripts(hooks_dir: Path) -> set[str]:
    """Collect all script paths referenced across all *.hooks.json in hooks_dir."""
    referenced: set[str] = set()
    for hook_file in hooks_dir.glob("*.hooks.json"):
        try:
            data = json.loads(hook_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        hooks = data.get("hooks")
        if not isinstance(hooks, dict):
            continue
        for entries in hooks.values():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                command = entry.get("command", "")
                for script_path in _extract_script_paths(command):
                    referenced.add(script_path)
    return referenced


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_hook_json(path: Path) -> list[ValidationResult]:
    """Validate a single *.hooks.json file."""
    results: list[ValidationResult] = []

    # 1. Parse JSON
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        results.append(ValidationResult(
            Severity.ERROR,
            f"Invalid JSON syntax in {path.name}: {exc}",
            path,
        ))
        return results
    except OSError as exc:
        results.append(ValidationResult(
            Severity.ERROR,
            f"Cannot read file {path.name}: {exc}",
            path,
        ))
        return results

    # 2. Check version
    if "version" not in data:
        results.append(ValidationResult(
            Severity.ERROR,
            f"Missing required 'version' field in {path.name}",
            path,
        ))
    elif data["version"] != 1:
        results.append(ValidationResult(
            Severity.ERROR,
            f"Unsupported version {data['version']} in {path.name} (expected 1)",
            path,
        ))

    # 3. Check hooks field
    if "hooks" not in data:
        results.append(ValidationResult(
            Severity.ERROR,
            f"Missing required 'hooks' field in {path.name}",
            path,
        ))
        return results

    hooks = data["hooks"]
    if not isinstance(hooks, dict):
        results.append(ValidationResult(
            Severity.ERROR,
            f"'hooks' must be an object in {path.name}",
            path,
        ))
        return results

    # 4. Empty hooks
    if not hooks:
        results.append(ValidationResult(
            Severity.WARNING,
            f"Empty hooks object in {path.name} — no hooks defined",
            path,
        ))
        return results

    # 5-6. Validate each hook type and entry
    # Resolve workspace root relative to the hooks file
    # hooks files live in <workspace>/.github/hooks/
    workspace_root = path.parent
    while workspace_root != workspace_root.parent:
        if (workspace_root / ".github").is_dir():
            break
        workspace_root = workspace_root.parent

    for hook_type, entries in hooks.items():
        if hook_type not in VALID_HOOK_TYPES:
            results.append(ValidationResult(
                Severity.ERROR,
                f"Invalid hook type '{hook_type}' in {path.name}",
                path,
            ))

        if not isinstance(entries, list):
            continue

        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue

            # command required
            if "command" not in entry:
                results.append(ValidationResult(
                    Severity.ERROR,
                    f"Hook entry {hook_type}[{i}] missing 'command' in {path.name}",
                    path,
                ))
            else:
                # Check if referenced script exists
                for script_path in _extract_script_paths(entry["command"]):
                    resolved = workspace_root / script_path
                    if not resolved.is_file():
                        results.append(ValidationResult(
                            Severity.WARNING,
                            f"Script '{script_path}' referenced in {path.name} does not exist",
                            path,
                        ))

            # description recommended
            if "description" not in entry:
                results.append(ValidationResult(
                    Severity.WARNING,
                    f"Hook entry {hook_type}[{i}] missing 'description' in {path.name}",
                    path,
                ))

    return results


def validate_hook_scripts(hooks_dir: Path) -> list[ValidationResult]:
    """Validate scripts referenced by hooks JSON files exist and are executable."""
    results: list[ValidationResult] = []

    # Resolve workspace root
    workspace_root = hooks_dir
    while workspace_root != workspace_root.parent:
        if (workspace_root / ".github").is_dir():
            break
        workspace_root = workspace_root.parent

    # Collect all referenced scripts
    referenced_scripts = _collect_referenced_scripts(hooks_dir)

    # Collect all .sh files in scripts/
    scripts_subdir = hooks_dir / "scripts"
    existing_scripts: set[Path] = set()
    if scripts_subdir.is_dir():
        existing_scripts = {p for p in scripts_subdir.glob("*.sh") if p.is_file()}

    # Validate each referenced script
    for script_rel in referenced_scripts:
        script_abs = workspace_root / script_rel
        if not script_abs.is_file():
            results.append(ValidationResult(
                Severity.ERROR,
                f"Referenced script does not exist: {script_rel}",
                Path(script_rel),
            ))
            continue

        # Check executable
        if not os.access(script_abs, os.X_OK):
            results.append(ValidationResult(
                Severity.ERROR,
                f"Script is not executable: {script_rel}",
                script_abs,
            ))

        # Check shebang
        try:
            first_line = script_abs.read_text(encoding="utf-8").split("\n", 1)[0]
            if not first_line.startswith("#!/usr/bin/env bash"):
                results.append(ValidationResult(
                    Severity.WARNING,
                    f"Script missing '#!/usr/bin/env bash' shebang: {script_rel}",
                    script_abs,
                ))
        except OSError:
            pass

    # Check for orphan scripts
    referenced_abs = {(workspace_root / s).resolve() for s in referenced_scripts}
    for script_file in existing_scripts:
        if script_file.resolve() not in referenced_abs:
            results.append(ValidationResult(
                Severity.WARNING,
                f"Orphan script not referenced by any hook: {script_file.name}",
                script_file,
            ))

    return results


def validate_hooks_directory(hooks_dir: Path) -> list[ValidationResult]:
    """Full validation of a hooks directory."""
    results: list[ValidationResult] = []

    # 1. Non-existent directory — skip gracefully
    if not hooks_dir.is_dir():
        return results

    # Collect all items (excluding _local/)
    all_items = [
        f for f in hooks_dir.iterdir()
        if f.name != "_local" and not f.name.startswith(".")
    ]

    # 2. Empty directory
    hook_json_files = [f for f in all_items if f.name.endswith(".hooks.json")]
    json_files = [f for f in all_items if f.is_file() and f.suffix == ".json"]

    if not all_items or (not json_files and not hook_json_files):
        results.append(ValidationResult(
            Severity.WARNING,
            f"Hooks directory is empty — no hook files found in {hooks_dir}",
            hooks_dir,
        ))
        return results

    # 3. .json without .hooks.json suffix
    for f in json_files:
        if not f.name.endswith(".hooks.json"):
            results.append(ValidationResult(
                Severity.WARNING,
                f"JSON file '{f.name}' does not use .hooks.json suffix",
                f,
            ))

    # 4. Validate each *.hooks.json
    for hook_file in hook_json_files:
        results.extend(validate_hook_json(hook_file))

    # 5. Validate scripts
    results.extend(validate_hook_scripts(hooks_dir))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate hooks JSON files and referenced scripts.",
    )
    parser.add_argument(
        "--hooks-dir",
        type=Path,
        default=None,
        help="Path to hooks directory (default: .github/hooks/ relative to workspace)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all results including INFO",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve hooks directory
    if args.hooks_dir:
        hooks_dir = args.hooks_dir.resolve()
    else:
        workspace = Path(__file__).resolve().parent.parent
        hooks_dir = workspace / ".github" / "hooks"

    log.info("Validating hooks in: %s", hooks_dir)

    results = validate_hooks_directory(hooks_dir)

    # Report
    errors = [r for r in results if r.severity == Severity.ERROR]
    warnings = [r for r in results if r.severity == Severity.WARNING]
    infos = [r for r in results if r.severity == Severity.INFO]

    for r in errors:
        log.error("ERROR: %s", r.message)
    for r in warnings:
        log.warning("WARNING: %s", r.message)
    if args.verbose:
        for r in infos:
            log.info("INFO: %s", r.message)

    log.info(
        "\nSummary: %d error(s), %d warning(s), %d info(s)",
        len(errors), len(warnings), len(infos),
    )

    if errors:
        return 2
    if warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
