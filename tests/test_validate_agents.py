"""
Tests for scripts/validate_agents.py — core validation functions.

Covers:
- parse_frontmatter: valid, missing, unclosed, empty, YAML lists
- _pascal_to_kebab: various PascalCase conversions
- validate_plugin_tools: subset check, violation, no plugins dir
- _parse_tools_list: inline list, single value, empty

Run:
    python -m pytest tests/test_validate_agents.py -v
"""
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_agents  # noqa: E402


# =========================================================================
# parse_frontmatter
# =========================================================================

class TestParseFrontmatter(unittest.TestCase):
    """Tests for parse_frontmatter()."""

    def test_valid_frontmatter(self):
        text = "---\nname: backend-dev\ndescription: Backend developer\n---\n# Body\n"
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["name"], "backend-dev")
        self.assertEqual(fm["description"], "Backend developer")
        self.assertIn("# Body", body)

    def test_missing_frontmatter_no_delimiters(self):
        text = "# Just a markdown file\nNo frontmatter here."
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNone(fm)
        self.assertEqual(body, text)

    def test_unclosed_frontmatter(self):
        text = "---\nname: test\ndescription: oops no closing\n# Body\n"
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNone(fm)
        self.assertEqual(body, text)

    def test_empty_frontmatter(self):
        text = "---\n---\n# Body\n"
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm, {})

    def test_frontmatter_with_yaml_list(self):
        text = '---\nname: test\ntools: ["execute", "read", "edit"]\n---\n# Body\n'
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["tools"], '["execute", "read", "edit"]')

    def test_frontmatter_with_quoted_values(self):
        text = '---\nname: "my-agent"\ndescription: \'Agent de test\'\n---\n# Body\n'
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["name"], "my-agent")
        self.assertEqual(fm["description"], "Agent de test")

    def test_frontmatter_with_boolean(self):
        text = "---\nname: test\nuser-invocable: true\n---\n# Body\n"
        fm, body = validate_agents.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        self.assertEqual(fm["user-invocable"], "true")


# =========================================================================
# _pascal_to_kebab
# =========================================================================

class TestPascalToKebab(unittest.TestCase):
    """Tests for _pascal_to_kebab()."""

    def test_qa_engineer(self):
        self.assertEqual(validate_agents._pascal_to_kebab("QAEngineer"), "qa-engineer")

    def test_api_designer(self):
        self.assertEqual(validate_agents._pascal_to_kebab("APIDesigner"), "api-designer")

    def test_mlops_engineer(self):
        self.assertEqual(validate_agents._pascal_to_kebab("MLOpsEngineer"), "ml-ops-engineer")

    def test_backend_dev(self):
        self.assertEqual(validate_agents._pascal_to_kebab("BackendDev"), "backend-dev")

    def test_ai_ethics_governance(self):
        self.assertEqual(
            validate_agents._pascal_to_kebab("AIEthicsGovernance"),
            "ai-ethics-governance",
        )


# =========================================================================
# _parse_tools_list
# =========================================================================

class TestParseToolsList(unittest.TestCase):
    """Tests for _parse_tools_list()."""

    def test_inline_list(self):
        result = validate_agents._parse_tools_list('["execute", "read", "edit"]')
        self.assertEqual(result, {"execute", "read", "edit"})

    def test_single_value(self):
        result = validate_agents._parse_tools_list('"execute"')
        self.assertEqual(result, {"execute"})

    def test_empty_string(self):
        result = validate_agents._parse_tools_list("")
        self.assertEqual(result, set())

    def test_list_with_spaces(self):
        result = validate_agents._parse_tools_list('[  "a" ,  "b"  ]')
        self.assertEqual(result, {"a", "b"})


# =========================================================================
# validate_plugin_tools
# =========================================================================

class TestValidatePluginTools(unittest.TestCase):
    """Tests for validate_plugin_tools()."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_plugins_"))
        self.agents_dir = self.temp_dir / "agents"
        self.agents_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_agent(self, path: Path, name: str, tools: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'---\nname: {name}\ndescription: "Test"\ntools: {tools}\n---\n# {name}\n',
            encoding="utf-8",
        )

    def test_plugin_tools_subset_of_core(self):
        self._write_agent(
            self.agents_dir / "core.agent.md",
            "core",
            '["execute", "read", "edit"]',
        )
        plugins_dir = self.agents_dir / "_plugins"
        self._write_agent(
            plugins_dir / "my-plugin.agent.md",
            "my-plugin",
            '["read"]',
        )
        results = validate_agents.validate_plugin_tools(self.agents_dir)
        self.assertEqual(len(results), 0, "No violations expected when plugin tools ⊆ core tools")

    def test_plugin_tools_not_subset_of_core(self):
        self._write_agent(
            self.agents_dir / "core.agent.md",
            "core",
            '["read"]',
        )
        plugins_dir = self.agents_dir / "_plugins"
        self._write_agent(
            plugins_dir / "bad-plugin.agent.md",
            "bad-plugin",
            '["read", "execute", "destroy"]',
        )
        results = validate_agents.validate_plugin_tools(self.agents_dir)
        self.assertGreater(len(results), 0, "Violations expected when plugin uses non-core tools")
        self.assertEqual(results[0].severity, validate_agents.Severity.WARNING)

    def test_no_plugins_directory(self):
        self._write_agent(
            self.agents_dir / "core.agent.md",
            "core",
            '["read"]',
        )
        results = validate_agents.validate_plugin_tools(self.agents_dir)
        self.assertEqual(len(results), 0, "No results when _plugins/ does not exist")


# =========================================================================
# Schema structural tests (AQ-006-QA)
# =========================================================================

class TestSchemaStructure(unittest.TestCase):
    """Structural tests for schemas/agent.schema.json — no jsonschema lib needed."""

    @classmethod
    def setUpClass(cls):
        schema_path = WORKSPACE / "schemas" / "agent.schema.json"
        with open(schema_path, encoding="utf-8") as f:
            cls.schema = json.load(f)

    def test_schema_is_valid_json(self):
        self.assertIsInstance(self.schema, dict)

    def test_schema_has_required_fields(self):
        self.assertIn("required", self.schema)
        required = self.schema["required"]
        self.assertIsInstance(required, list)
        for field in ("name", "description"):
            self.assertIn(field, required, f"'{field}' should be in required")

    def test_additional_properties_false(self):
        self.assertIn("additionalProperties", self.schema)
        self.assertFalse(
            self.schema["additionalProperties"],
            "additionalProperties must be false to prevent unknown fields",
        )

    def test_schema_has_properties(self):
        self.assertIn("properties", self.schema)
        props = self.schema["properties"]
        self.assertIn("name", props)
        self.assertIn("description", props)
        self.assertIn("tools", props)

    def test_name_has_pattern(self):
        name_prop = self.schema["properties"]["name"]
        self.assertIn("pattern", name_prop, "name property should have a regex pattern")


# =========================================================================
# validate_agent_file  (AQ-201)
# =========================================================================

class TestValidateAgentFile(unittest.TestCase):
    """Tests for validate_agent_file() — single-file validation pipeline."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_validate_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write(self, name: str, content: str) -> Path:
        p = self.temp_dir / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_agent_returns_ok(self):
        path = self._write(
            "good.agent.md",
            "---\nname: good\ndescription: A good agent\ntools: [\"read\"]\nmodel: gpt-4o\n---\n"
            "# Agent : Good\n\n## Identité & Posture\n\nIdentité.\n\n"
            "## Contrat de handoff\n\nHandoff.\n",
        )
        result = validate_agents.validate_agent_file(path, {"good"})
        self.assertEqual(result.severity, validate_agents.Severity.OK)

    def test_missing_name_returns_error(self):
        path = self._write(
            "noname.agent.md",
            "---\ndescription: No name agent\n---\n# Body\n",
        )
        result = validate_agents.validate_agent_file(path, set())
        self.assertEqual(result.severity, validate_agents.Severity.ERROR)
        self.assertTrue(any("name" in m for m in result.messages))

    def test_unknown_field_returns_warning(self):
        path = self._write(
            "extra.agent.md",
            "---\nname: extra\ndescription: Extra field\nfoo: bar\n---\n# Body\n",
        )
        result = validate_agents.validate_agent_file(path, {"extra"})
        self.assertGreaterEqual(result.severity, validate_agents.Severity.WARNING)
        self.assertTrue(any("foo" in m for m in result.messages))

    def test_missing_identity_section_returns_warning(self):
        path = self._write(
            "noid.agent.md",
            "---\nname: noid\ndescription: No identity\n---\n\nJuste du texte libre.\n",
        )
        result = validate_agents.validate_agent_file(path, {"noid"})
        self.assertGreaterEqual(result.severity, validate_agents.Severity.WARNING)

    def test_crossref_missing_agent_returns_warning(self):
        path = self._write(
            "crossref.agent.md",
            "---\nname: crossref\ndescription: Cross-ref test\n---\n"
            "# Agent\n\n## Contrat de handoff\n\nHandoff vers `nonexistent-agent`.\n",
        )
        result = validate_agents.validate_agent_file(path, {"crossref"})
        self.assertGreaterEqual(result.severity, validate_agents.Severity.WARNING)
        self.assertTrue(any("nonexistent-agent" in m for m in result.messages))


# =========================================================================
# extract_mentioned_agents & _extract_collab_handoff_sections  (AQ-202)
# =========================================================================

class TestExtractMentionedAgents(unittest.TestCase):
    """Tests for extract_mentioned_agents() and _extract_collab_handoff_sections()."""

    def test_pascal_case_extraction(self):
        body = "## Contrat de handoff\n\nHandoff vers BackendDev et SecurityEngineer.\n"
        mentioned = validate_agents.extract_mentioned_agents(body)
        self.assertIn("backend-dev", mentioned)
        self.assertIn("security-engineer", mentioned)

    def test_at_mention_extraction(self):
        body = "## Collaboration\n\nCollaborer avec @frontend-dev et @qa-engineer.\n"
        mentioned = validate_agents.extract_mentioned_agents(body)
        self.assertIn("frontend-dev", mentioned)
        self.assertIn("qa-engineer", mentioned)

    def test_backtick_kebab_extraction(self):
        body = "## Contrat de handoff\n\nHandoff vers `code-reviewer` et `tech-writer`.\n"
        mentioned = validate_agents.extract_mentioned_agents(body)
        self.assertIn("code-reviewer", mentioned)
        self.assertIn("tech-writer", mentioned)

    def test_false_positive_filtering(self):
        body = (
            "## Collaboration\n\n"
            "Utilise context7 et chrome-devtools pour le debug.\n"
            "Gère les animations CSS prefers-reduced-motion.\n"
        )
        mentioned = validate_agents.extract_mentioned_agents(body)
        self.assertNotIn("context7", mentioned)
        self.assertNotIn("chrome-devtools", mentioned)

    def test_body_without_collab_section_returns_empty(self):
        body = "## Identité & Posture\n\nJe suis un agent.\n\n## Règles\n\n- Règle 1\n"
        mentioned = validate_agents.extract_mentioned_agents(body)
        self.assertEqual(mentioned, set())

    def test_extract_collab_sections_inline(self):
        body = "**Collaboration** : BackendDev, FrontendDev\n\n## Autre section\n"
        section = validate_agents._extract_collab_handoff_sections(body)
        self.assertIn("BackendDev", section)
        self.assertIn("FrontendDev", section)

    def test_extract_collab_sections_heading(self):
        body = "## Identité\n\nBlabla.\n\n## Contrat de handoff\n\nHandoff vers @qa-engineer.\n"
        section = validate_agents._extract_collab_handoff_sections(body)
        self.assertIn("@qa-engineer", section)

    def test_extract_collab_sections_no_match(self):
        body = "## Identité\n\nRien de pertinent.\n\n## Règles\n\n- Règle.\n"
        section = validate_agents._extract_collab_handoff_sections(body)
        self.assertEqual(section, "")


# =========================================================================
# discover_filieres  (AQ-204)
# =========================================================================

class TestDiscoverFilieres(unittest.TestCase):
    """Tests for discover_filieres() — filière auto-discovery."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_filieres_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_discovers_filieres_from_orchestrators(self):
        (self.temp_dir / "orchestrator-tech.agent.md").write_text(
            "---\nname: orchestrator-tech\ndescription: Tech\n---\n# Tech\n", encoding="utf-8"
        )
        (self.temp_dir / "orchestrator-product.agent.md").write_text(
            "---\nname: orchestrator-product\ndescription: Product\n---\n# Product\n", encoding="utf-8"
        )
        filieres = validate_agents.discover_filieres(self.temp_dir)
        self.assertEqual(filieres, {"tech", "product"})

    def test_no_orchestrators_returns_empty(self):
        (self.temp_dir / "backend-dev.agent.md").write_text(
            "---\nname: backend-dev\ndescription: Dev\n---\n# Dev\n", encoding="utf-8"
        )
        filieres = validate_agents.discover_filieres(self.temp_dir)
        self.assertEqual(filieres, set())

    def test_ignores_non_matching_files(self):
        (self.temp_dir / "orchestrator.agent.md").write_text(
            "---\nname: orchestrator\ndescription: Main\n---\n# Main\n", encoding="utf-8"
        )
        filieres = validate_agents.discover_filieres(self.temp_dir)
        self.assertEqual(filieres, set())


# =========================================================================
# validate_config_waivers  (AQ-204)
# =========================================================================

class TestValidateConfigWaivers(unittest.TestCase):
    """Tests for validate_config_waivers() — YAML waiver validation."""

    @classmethod
    def setUpClass(cls):
        try:
            import yaml  # noqa: F401
            cls.has_yaml = True
        except ImportError:
            cls.has_yaml = False

    def setUp(self):
        if not self.has_yaml:
            self.skipTest("PyYAML not installed — skipping waiver tests")
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_waivers_"))
        self.captured_warnings: list[str] = []
        self._original_warning = validate_agents.log.warning

        def _capture(msg, *args):
            self.captured_warnings.append(msg % args if args else msg)

        validate_agents.log.warning = _capture

    def tearDown(self):
        validate_agents.log.warning = self._original_warning
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_config(self, config: dict) -> None:
        import yaml
        config_path = self.temp_dir / ".renga.yml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

    def _call(self) -> None:
        """Call validate_config_waivers with patched __file__ to use temp dir."""
        import unittest.mock
        # Create the expected directory structure: temp_dir/scripts/validate_agents.py
        fake_scripts = self.temp_dir / "scripts"
        fake_scripts.mkdir(exist_ok=True)
        (fake_scripts / "validate_agents.py").touch()
        # Patch __file__ so Path(__file__).resolve().parent.parent == temp_dir
        with unittest.mock.patch.object(
            validate_agents, "__file__", str(fake_scripts / "validate_agents.py")
        ):
            validate_agents.validate_config_waivers()

    def test_valid_waiver_no_warning(self):
        """A well-formed waiver emits no warnings about missing fields."""
        from datetime import date, timedelta
        future = (date.today() + timedelta(days=30)).isoformat()
        self._write_config({
            "waivers": [
                {"rule": "some-rule", "reason": "Valid reason", "expires": future, "approved_by": "admin"}
            ]
        })
        self._call()
        self.assertEqual(self.captured_warnings, [])

    def test_expired_waiver_detected(self):
        """A waiver with a past expiration date triggers a warning."""
        from datetime import date, timedelta
        expired = (date.today() - timedelta(days=10)).isoformat()
        self._write_config({
            "waivers": [
                {"rule": "old-rule", "reason": "Was valid", "expires": expired, "approved_by": "admin"}
            ]
        })
        self._call()
        self.assertTrue(
            any("expired" in w for w in self.captured_warnings),
            f"Expected 'expired' warning, got: {self.captured_warnings}",
        )

    def test_missing_fields_detected(self):
        """A waiver without rule or reason triggers warnings."""
        from datetime import date, timedelta
        future = (date.today() + timedelta(days=30)).isoformat()
        self._write_config({
            "waivers": [{"expires": future}]
        })
        self._call()
        self.assertTrue(
            any("missing" in w.lower() and "rule" in w.lower() for w in self.captured_warnings),
            f"Expected 'missing rule' warning, got: {self.captured_warnings}",
        )
        self.assertTrue(
            any("missing" in w.lower() and "reason" in w.lower() for w in self.captured_warnings),
            f"Expected 'missing reason' warning, got: {self.captured_warnings}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
