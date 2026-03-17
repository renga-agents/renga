"""Tests for skill validation and parsing.

Covers:
- parse_skill_file: valid, missing frontmatter, empty body
- validate_skill_file: name mismatch, missing fields, unknown fields,
  schema constraints (name pattern, maxLength, description min/max, hint max)
- validate_skill_references: cross-ref agent → skill, plugins, multi-skills

Run:
    python -m pytest tests/test_validate_skills.py -v
"""
import sys
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from agent_parser import SkillData, parse_skill_file  # noqa: E402
from validate_agents import (  # noqa: E402
    Severity,
    validate_skill_file,
    validate_skill_references,
)


# =========================================================================
# parse_skill_file
# =========================================================================

class TestParseSkillFile(unittest.TestCase):
    """Tests for parse_skill_file()."""

    def test_valid_skill(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            skill_dir = Path(td) / "my-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(
                '---\nname: my-skill\ndescription: "A test skill"\n---\n'
                "# Instructions\n\nDo the thing.\n"
            )
            result = parse_skill_file(skill_file)
            self.assertIsNotNone(result)
            self.assertEqual(result.name, "my-skill")
            self.assertEqual(result.description, "A test skill")
            self.assertIn("Do the thing", result.body)
            self.assertTrue(result.user_invocable)
            self.assertFalse(result.disable_model_invocation)

    def test_non_invocable_skill(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            skill_dir = Path(td) / "bg-skill"
            skill_dir.mkdir()
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(
                "---\nname: bg-skill\ndescription: Background skill\n"
                "user-invocable: false\ndisable-model-invocation: true\n---\n# Body\n"
            )
            result = parse_skill_file(skill_file)
            self.assertIsNotNone(result)
            self.assertFalse(result.user_invocable)
            self.assertTrue(result.disable_model_invocation)

    def test_missing_frontmatter(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            skill_file = Path(td) / "SKILL.md"
            skill_file.write_text("# No frontmatter\nJust content.\n")
            result = parse_skill_file(skill_file)
            self.assertIsNone(result)

    def test_nonexistent_file(self):
        result = parse_skill_file(Path("/nonexistent/SKILL.md"))
        self.assertIsNone(result)


# =========================================================================
# validate_skill_file
# =========================================================================

class TestValidateSkillFile(unittest.TestCase):
    """Tests for validate_skill_file()."""

    def _make_skill(self, tmp_dir, name, content):
        skill_dir = Path(tmp_dir) / name
        skill_dir.mkdir(exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(content)
        return skill_file

    def test_valid_skill(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\nname: my-skill\ndescription: "Does stuff"\n---\n# Body\nContent.\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.OK)

    def test_missing_name(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\ndescription: "Does stuff"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("name" in m for m in result.messages))

    def test_missing_description(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                "---\nname: my-skill\n---\n# Body\n")
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)

    def test_name_mismatch(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\nname: wrong-name\ndescription: "Oops"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("does not match" in m for m in result.messages))

    def test_empty_body(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\nname: my-skill\ndescription: "One-liner"\n---\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.WARNING)
            self.assertTrue(any("empty" in m for m in result.messages))

    def test_unknown_fields(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\nname: my-skill\ndescription: "Has extras"\n'
                "custom-field: hello\n---\n# Body\n")
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.WARNING)

    # -- Schema constraint tests -------------------------------------------

    def test_name_uppercase_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "My-Skill",
                '---\nname: My-Skill\ndescription: "A valid description"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("pattern" in m for m in result.messages))

    def test_name_special_chars_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my_skill",
                '---\nname: my_skill\ndescription: "A valid description"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("pattern" in m for m in result.messages))

    def test_name_too_long(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            long_name = "a" + "-b" * 33  # 67 chars
            sf = self._make_skill(td, long_name,
                f'---\nname: {long_name}\ndescription: "A valid description"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("64" in m for m in result.messages))

    def test_description_too_short(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill",
                '---\nname: my-skill\ndescription: "Short"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.WARNING)
            self.assertTrue(any("short" in m for m in result.messages))

    def test_description_too_long(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            long_desc = "x" * 1025
            sf = self._make_skill(td, "my-skill",
                f'---\nname: my-skill\ndescription: "{long_desc}"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.ERROR)
            self.assertTrue(any("1024" in m for m in result.messages))

    def test_argument_hint_too_long(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            long_hint = "x" * 201
            sf = self._make_skill(td, "my-skill",
                f'---\nname: my-skill\ndescription: "A valid description"\n'
                f'argument-hint: "{long_hint}"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.WARNING)
            self.assertTrue(any("200" in m for m in result.messages))

    def test_valid_name_pattern(self):
        """Names like 'a', 'ab-cd', 'my-skill-2' should pass."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sf = self._make_skill(td, "my-skill-2",
                '---\nname: my-skill-2\ndescription: "A perfectly valid description"\n---\n# Body\n')
            result = validate_skill_file(sf)
            self.assertEqual(result.severity, Severity.OK)


# =========================================================================
# validate_skill_references
# =========================================================================

class TestValidateSkillReferences(unittest.TestCase):
    """Tests for validate_skill_references()."""

    def test_valid_reference(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            (agents_dir / "test-agent.agent.md").write_text(
                '---\nname: test-agent\ndescription: Agent\n'
                'skills: [my-skill]\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"my-skill"})
            self.assertEqual(len(result), 0)

    def test_broken_reference(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            (agents_dir / "test-agent.agent.md").write_text(
                '---\nname: test-agent\ndescription: Agent\n'
                'skills: [nonexistent-skill]\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"my-skill"})
            self.assertEqual(len(result), 1)
            self.assertTrue(any("nonexistent-skill" in m for m in result[0].messages))

    def test_plugin_agent_valid_reference(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            plugin_dir = agents_dir / "_plugins" / "my-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "custom-agent.agent.md").write_text(
                '---\nname: custom-agent\ndescription: Plugin agent\n'
                'skills: [my-skill]\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"my-skill"})
            self.assertEqual(len(result), 0)

    def test_plugin_agent_broken_reference(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            plugin_dir = agents_dir / "_plugins" / "my-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "custom-agent.agent.md").write_text(
                '---\nname: custom-agent\ndescription: Plugin agent\n'
                'skills: [ghost-skill]\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"my-skill"})
            self.assertEqual(len(result), 1)
            self.assertTrue(any("ghost-skill" in m for m in result[0].messages))

    def test_multiple_skills_in_agent(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            (agents_dir / "multi.agent.md").write_text(
                '---\nname: multi\ndescription: Agent\n'
                'skills: [skill-a, skill-b, skill-c]\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"skill-a", "skill-c"})
            self.assertEqual(len(result), 1)
            self.assertTrue(any("skill-b" in m for m in result[0].messages))

    def test_empty_skills_list(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            agents_dir = Path(td) / "agents"
            agents_dir.mkdir()
            (agents_dir / "empty.agent.md").write_text(
                '---\nname: empty\ndescription: Agent\n'
                'skills: []\n---\n# Body\n'
            )
            result = validate_skill_references(agents_dir, {"my-skill"})
            self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
