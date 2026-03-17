"""
Tests for scripts/agent_parser.py — shared parser functions (AQ-206).

Covers:
- parse_list_value: comma-separated, bracketed, JSON-style, empty, single
- parse_agent_file: valid agent, missing frontmatter

Run:
    python -m pytest tests/test_agent_parser.py -v
"""
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import agent_parser  # noqa: E402


# =========================================================================
# parse_list_value
# =========================================================================

class TestParseListValue(unittest.TestCase):
    """Tests for parse_list_value()."""

    def test_comma_separated_in_brackets(self):
        result = agent_parser.parse_list_value("[a, b, c]")
        self.assertEqual(result, ["a", "b", "c"])

    def test_json_style_quoted(self):
        result = agent_parser.parse_list_value('["a", "b"]')
        self.assertEqual(result, ["a", "b"])

    def test_single_quoted(self):
        result = agent_parser.parse_list_value("['x', 'y']")
        self.assertEqual(result, ["x", "y"])

    def test_empty_string(self):
        result = agent_parser.parse_list_value("")
        self.assertEqual(result, [])

    def test_single_value(self):
        result = agent_parser.parse_list_value("single")
        self.assertEqual(result, ["single"])

    def test_single_quoted_value(self):
        result = agent_parser.parse_list_value('"execute"')
        self.assertEqual(result, ["execute"])


# =========================================================================
# parse_agent_file
# =========================================================================

class TestParseAgentFile(unittest.TestCase):
    """Tests for parse_agent_file()."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_parser_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_agent_file(self):
        path = self.temp_dir / "test.agent.md"
        path.write_text(
            '---\nname: test-agent\ndescription: "Test agent"\n'
            'tools: ["read", "edit"]\nmodel: gpt-4o\n---\n'
            "# Agent : TestAgent\n\nBody content.\n",
            encoding="utf-8",
        )
        data = agent_parser.parse_agent_file(path)
        self.assertIsNotNone(data)
        self.assertEqual(data.name, "test-agent")
        self.assertEqual(data.description, "Test agent")
        self.assertEqual(data.tools, ["read", "edit"])
        self.assertEqual(data.model, "gpt-4o")
        self.assertIn("Body content", data.body)

    def test_file_without_frontmatter_returns_none(self):
        path = self.temp_dir / "nofm.agent.md"
        path.write_text("# Just markdown\n\nNo frontmatter here.\n", encoding="utf-8")
        data = agent_parser.parse_agent_file(path)
        self.assertIsNone(data)

    def test_nonexistent_file_returns_none(self):
        path = self.temp_dir / "ghost.agent.md"
        data = agent_parser.parse_agent_file(path)
        self.assertIsNone(data)

    def test_user_invocable_false(self):
        path = self.temp_dir / "hidden.agent.md"
        path.write_text(
            "---\nname: hidden\ndescription: Hidden agent\nuser-invocable: false\n---\n# Hidden\n",
            encoding="utf-8",
        )
        data = agent_parser.parse_agent_file(path)
        self.assertIsNotNone(data)
        self.assertFalse(data.user_invocable)


if __name__ == "__main__":
    unittest.main(verbosity=2)
