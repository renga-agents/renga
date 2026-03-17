"""Tests for scripts/validate_hooks.py — hook JSON validation functions.

Covers:
- validate_hook_json: schema, types, fields, syntax
- validate_hook_scripts: existence, permissions, shebang, orphans
- validate_hooks_directory: full directory validation, edge cases

TDD Wave 1 — all tests are RED (validate_hooks.py does not exist yet).

Run:
    python -m pytest tests/test_validate_hooks.py -v
"""
import json
import os
import stat
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import validate_hooks  # noqa: E402
except ImportError:
    validate_hooks = None

_SKIP_REASON = "validate_hooks not yet implemented"

# Valid hook types per spec
_VALID_HOOK_TYPES = frozenset({
    "sessionStart",
    "sessionEnd",
    "userPromptSubmitted",
    "preToolUse",
    "postToolUse",
    "agentStop",
    "subagentStop",
    "errorOccurred",
})


# =========================================================================
# TestValidateHookJson
# =========================================================================

@unittest.skipIf(validate_hooks is None, _SKIP_REASON)
class TestValidateHookJson(unittest.TestCase):
    """Tests for validate_hook_json(path) -> list[ValidationResult]."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_hooks_json_"))
        self.hooks_dir = self.temp_dir / ".github" / "hooks"
        self.hooks_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- helpers ----------------------------------------------------------

    def _write_valid_hook_json(self, path: Path) -> None:
        """Write a minimal valid hooks.json file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/pre-tool-security.sh",
                    "description": "Security policy enforcement",
                }]
            }
        }), encoding="utf-8")

    def _write_hook_json(self, path: Path, data: dict) -> None:
        """Write arbitrary JSON to a hooks file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    # -- tests ------------------------------------------------------------

    def test_valid_hook_json(self):
        """A well-formed hooks.json file produces zero errors."""
        hook_file = self.hooks_dir / "security.hooks.json"
        self._write_valid_hook_json(hook_file)
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertEqual(len(errors), 0)

    def test_missing_version_field(self):
        """Missing 'version' key produces an ERROR."""
        hook_file = self.hooks_dir / "bad.hooks.json"
        self._write_hook_json(hook_file, {
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/check.sh",
                    "description": "Check",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("version" in r.message.lower() for r in errors),
            f"Expected ERROR about missing 'version', got: {errors}",
        )

    def test_wrong_version_value(self):
        """Version != 1 produces an ERROR."""
        hook_file = self.hooks_dir / "bad-version.hooks.json"
        self._write_hook_json(hook_file, {
            "version": 99,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/check.sh",
                    "description": "Check",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("version" in r.message.lower() for r in errors),
            f"Expected ERROR about wrong version value, got: {errors}",
        )

    def test_missing_hooks_field(self):
        """Missing 'hooks' key produces an ERROR."""
        hook_file = self.hooks_dir / "no-hooks.hooks.json"
        self._write_hook_json(hook_file, {"version": 1})
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("hooks" in r.message.lower() for r in errors),
            f"Expected ERROR about missing 'hooks', got: {errors}",
        )

    def test_invalid_hook_type(self):
        """An unrecognised hook type produces an ERROR."""
        hook_file = self.hooks_dir / "bad-type.hooks.json"
        self._write_hook_json(hook_file, {
            "version": 1,
            "hooks": {
                "fooBarEvent": [{
                    "command": "bash .github/hooks/scripts/foo.sh",
                    "description": "Unknown hook type",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("fooBarEvent" in r.message or "hook type" in r.message.lower()
                for r in errors),
            f"Expected ERROR about invalid hook type, got: {errors}",
        )

    def test_empty_hooks_object(self):
        """An empty 'hooks' dict produces a WARNING."""
        hook_file = self.hooks_dir / "empty-hooks.hooks.json"
        self._write_hook_json(hook_file, {"version": 1, "hooks": {}})
        results = validate_hooks.validate_hook_json(hook_file)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("empty" in r.message.lower() for r in warnings),
            f"Expected WARNING about empty hooks, got: {warnings}",
        )

    def test_hook_entry_missing_command(self):
        """A hook entry without 'command' produces an ERROR."""
        hook_file = self.hooks_dir / "no-cmd.hooks.json"
        self._write_hook_json(hook_file, {
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "description": "Missing command field",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("command" in r.message.lower() for r in errors),
            f"Expected ERROR about missing 'command', got: {errors}",
        )

    def test_hook_entry_invalid_command_path(self):
        """A command pointing to a non-existent script produces a WARNING."""
        hook_file = self.hooks_dir / "bad-path.hooks.json"
        self._write_hook_json(hook_file, {
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/does-not-exist.sh",
                    "description": "Points to missing script",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("does-not-exist" in r.message or "script" in r.message.lower()
                for r in warnings),
            f"Expected WARNING about invalid command path, got: {warnings}",
        )

    def test_invalid_json_syntax(self):
        """An unparseable JSON file produces an ERROR."""
        hook_file = self.hooks_dir / "broken.hooks.json"
        hook_file.write_text("{not valid json!!!", encoding="utf-8")
        results = validate_hooks.validate_hook_json(hook_file)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("json" in r.message.lower() or "parse" in r.message.lower()
                for r in errors),
            f"Expected ERROR about JSON syntax, got: {errors}",
        )

    def test_hook_entry_missing_description(self):
        """A hook entry without 'description' produces a WARNING."""
        hook_file = self.hooks_dir / "no-desc.hooks.json"
        self._write_hook_json(hook_file, {
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/pre-tool-security.sh",
                }]
            }
        })
        results = validate_hooks.validate_hook_json(hook_file)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("description" in r.message.lower() for r in warnings),
            f"Expected WARNING about missing 'description', got: {warnings}",
        )


# =========================================================================
# TestValidateHookScripts
# =========================================================================

@unittest.skipIf(validate_hooks is None, _SKIP_REASON)
class TestValidateHookScripts(unittest.TestCase):
    """Tests for validate_hook_scripts(hooks_dir) -> list[ValidationResult]."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_hooks_scripts_"))
        self.hooks_dir = self.temp_dir / ".github" / "hooks"
        self.scripts_dir = self.hooks_dir / "scripts"
        self.scripts_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- helpers ----------------------------------------------------------

    def _write_valid_hook_json(self, path: Path) -> None:
        """Write a minimal valid hooks.json file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/pre-tool-security.sh",
                    "description": "Security policy enforcement",
                }]
            }
        }), encoding="utf-8")

    def _write_valid_script(self, path: Path) -> None:
        """Write a minimal executable hook script."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # -- tests ------------------------------------------------------------

    def test_all_scripts_exist_and_executable(self):
        """All referenced scripts exist and are +x — zero errors."""
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        self._write_valid_script(self.scripts_dir / "pre-tool-security.sh")
        results = validate_hooks.validate_hook_scripts(self.hooks_dir)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertEqual(len(errors), 0)

    def test_script_not_executable(self):
        """A script present but without +x produces an ERROR."""
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        script = self.scripts_dir / "pre-tool-security.sh"
        script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        # Ensure NOT executable
        script.chmod(stat.S_IRUSR | stat.S_IWUSR)
        results = validate_hooks.validate_hook_scripts(self.hooks_dir)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("executable" in r.message.lower() or "permission" in r.message.lower()
                for r in errors),
            f"Expected ERROR about missing execute permission, got: {errors}",
        )

    def test_script_referenced_but_missing(self):
        """A script referenced in JSON but absent from disk produces an ERROR."""
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        # Do NOT create the script file
        results = validate_hooks.validate_hook_scripts(self.hooks_dir)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertTrue(
            any("missing" in r.message.lower() or "not found" in r.message.lower()
                or "exist" in r.message.lower()
                for r in errors),
            f"Expected ERROR about missing script file, got: {errors}",
        )

    def test_orphan_script_not_referenced(self):
        """A script in scripts/ not referenced by any JSON produces a WARNING."""
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        self._write_valid_script(self.scripts_dir / "pre-tool-security.sh")
        # Create an extra script not referenced anywhere
        self._write_valid_script(self.scripts_dir / "orphan-script.sh")
        results = validate_hooks.validate_hook_scripts(self.hooks_dir)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("orphan" in r.message.lower() or "not referenced" in r.message.lower()
                or "unreferenced" in r.message.lower()
                for r in warnings),
            f"Expected WARNING about orphan script, got: {warnings}",
        )

    def test_script_has_shebang(self):
        """A script without proper shebang produces a WARNING."""
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        script = self.scripts_dir / "pre-tool-security.sh"
        script.parent.mkdir(parents=True, exist_ok=True)
        # Write script WITHOUT shebang
        script.write_text("echo 'no shebang'\nexit 0\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        results = validate_hooks.validate_hook_scripts(self.hooks_dir)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("shebang" in r.message.lower() for r in warnings),
            f"Expected WARNING about missing shebang, got: {warnings}",
        )


# =========================================================================
# TestValidateHooksDirectory
# =========================================================================

@unittest.skipIf(validate_hooks is None, _SKIP_REASON)
class TestValidateHooksDirectory(unittest.TestCase):
    """Tests for validate_hooks_directory(hooks_dir) -> list[ValidationResult]."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_hooks_dir_"))
        self.hooks_dir = self.temp_dir / ".github" / "hooks"
        self.scripts_dir = self.hooks_dir / "scripts"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- helpers ----------------------------------------------------------

    def _write_valid_hook_json(self, path: Path) -> None:
        """Write a minimal valid hooks.json file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "version": 1,
            "hooks": {
                "preToolUse": [{
                    "command": "bash .github/hooks/scripts/pre-tool-security.sh",
                    "description": "Security policy enforcement",
                }]
            }
        }), encoding="utf-8")

    def _write_valid_script(self, path: Path) -> None:
        """Write a minimal executable hook script."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # -- tests ------------------------------------------------------------

    def test_valid_directory(self):
        """A well-formed hooks directory produces zero errors."""
        self.hooks_dir.mkdir(parents=True)
        self.scripts_dir.mkdir(parents=True)
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        self._write_valid_script(self.scripts_dir / "pre-tool-security.sh")
        results = validate_hooks.validate_hooks_directory(self.hooks_dir)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        self.assertEqual(len(errors), 0)

    def test_empty_directory(self):
        """An empty hooks directory produces a WARNING."""
        self.hooks_dir.mkdir(parents=True)
        results = validate_hooks.validate_hooks_directory(self.hooks_dir)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("empty" in r.message.lower() or "no hook" in r.message.lower()
                for r in warnings),
            f"Expected WARNING about empty directory, got: {warnings}",
        )

    def test_no_hooks_directory(self):
        """A non-existent hooks directory is handled gracefully (no crash)."""
        missing_dir = self.temp_dir / "nonexistent" / "hooks"
        results = validate_hooks.validate_hooks_directory(missing_dir)
        # Should either return an error/warning or an empty list — not raise
        self.assertIsInstance(results, list)

    def test_json_without_hooks_suffix(self):
        """A .json file without .hooks.json suffix produces a WARNING."""
        self.hooks_dir.mkdir(parents=True)
        # Write a valid hooks file with correct suffix
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        self._write_valid_script(
            self.scripts_dir / "pre-tool-security.sh",
        )
        # Write a .json file WITHOUT .hooks.json suffix
        bad_file = self.hooks_dir / "config.json"
        bad_file.write_text(json.dumps({"some": "data"}), encoding="utf-8")
        results = validate_hooks.validate_hooks_directory(self.hooks_dir)
        warnings = [r for r in results
                     if r.severity == validate_hooks.Severity.WARNING]
        self.assertTrue(
            any("config.json" in r.message or "hooks.json" in r.message.lower()
                for r in warnings),
            f"Expected WARNING about non-.hooks.json file, got: {warnings}",
        )

    def test_local_hooks_override_directory(self):
        """A _local/hooks/ directory is ignored — no errors produced."""
        self.hooks_dir.mkdir(parents=True)
        self._write_valid_hook_json(self.hooks_dir / "security.hooks.json")
        self._write_valid_script(self.scripts_dir / "pre-tool-security.sh")
        # Create _local override directory with arbitrary content
        local_dir = self.hooks_dir / "_local"
        local_dir.mkdir()
        (local_dir / "custom.hooks.json").write_text(
            json.dumps({"version": 1, "hooks": {}}), encoding="utf-8",
        )
        results = validate_hooks.validate_hooks_directory(self.hooks_dir)
        errors = [r for r in results if r.severity == validate_hooks.Severity.ERROR]
        # _local content must not produce errors
        local_errors = [r for r in errors
                        if r.path and "_local" in str(r.path)]
        self.assertEqual(
            len(local_errors), 0,
            f"_local/ content should be ignored, got errors: {local_errors}",
        )


if __name__ == "__main__":
    unittest.main()
