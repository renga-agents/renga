"""
Contract tests for transpilation scripts.

These tests verify that port_to_cursor.py and port_to_claude_code.py
correctly preserve essential agent content during format conversion.

Run from workspace root:
    python tests/test_transpilation.py
"""
import unittest
import sys
import shutil
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — must happen before importing transpilation modules
# ---------------------------------------------------------------------------

WORKSPACE = Path(__file__).parent.parent
AGENTS_DIR = WORKSPACE / ".github" / "agents"
INSTRUCTIONS_DIR = WORKSPACE / ".github" / "instructions"
SCRIPTS_DIR = WORKSPACE / "scripts"

# Inject scripts/ into sys.path so the script modules can be imported directly
sys.path.insert(0, str(SCRIPTS_DIR))

import port_to_cursor       # noqa: E402  (intentionally after sys.path setup)
import port_to_claude_code  # noqa: E402
import agent_parser          # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Real agent used as the primary fixture — well-structured, representative
REFERENCE_AGENT = AGENTS_DIR / "backend-dev.agent.md"

# Minimal inline agent — only the required frontmatter fields
MINIMAL_AGENT_CONTENT = """\
---
name: minimal-agent
description: "Agent de test minimal"
---
# Agent Minimal

Contenu minimal pour le test.
"""

# Controlled fixture with exactly the four canonical sections
CANONICAL_SECTIONS_AGENT = """\
---
name: canonical-agent
description: "Agent canonique avec les quatre sections standard"
tools: ["execute", "read", "edit"]
model: Claude Sonnet 4 (copilot)
user-invocable: true
---
# Agent : CanonicalAgent

**Domaine** : Test

---

## Identité & Posture

Identité de l'agent canonique.

---

## Règles de comportement

- Toujours vérifier les inputs
- Jamais ignorer une erreur

---

## Checklist avant livraison

- ☐ Tests passants
- ☐ Revue terminée

---

## Contrat de handoff

Handoff principal vers le code-reviewer.
"""


# ---------------------------------------------------------------------------
# Tests: port_to_cursor.py
# ---------------------------------------------------------------------------

class TestCursorTranspilation(unittest.TestCase):
    """Contract tests for port_to_cursor.py."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_cursor_"))
        self.input_dir = self.temp_dir / "agents"
        self.input_dir.mkdir()
        self.output_dir = self.temp_dir / "output"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_agent(self, filename: str, content: str) -> Path:
        """Write an inline agent fixture to the temp input directory."""
        path = self.input_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def _run_on_reference_agent(self) -> str:
        """Copy backend-dev.agent.md, run cursor conversion, return .mdc content."""
        shutil.copy(REFERENCE_AGENT, self.input_dir / "backend-dev.agent.md")
        port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        output_file = self.output_dir / "backend-dev.mdc"
        self.assertTrue(
            output_file.exists(),
            "Le fichier backend-dev.mdc doit être créé par la conversion Cursor",
        )
        return output_file.read_text(encoding="utf-8")

    def test_cursor_output_contains_frontmatter(self):
        """Verify that the .mdc contains the essential Cursor frontmatter fields."""
        content = self._run_on_reference_agent()

        self.assertTrue(
            content.startswith("---"),
            "Le fichier .mdc doit commencer par le délimiteur de frontmatter YAML (---)",
        )
        self.assertIn(
            "description:",
            content,
            "Le frontmatter Cursor doit contenir le champ 'description'",
        )
        self.assertIn(
            "alwaysApply:",
            content,
            "Le frontmatter Cursor doit contenir le champ 'alwaysApply'",
        )

    def test_cursor_output_contains_main_sections(self):
        """Verify that the four canonical sections are preserved verbatim in the .mdc output.

        Uses a controlled inline fixture (CANONICAL_SECTIONS_AGENT) so the test
        is independent of future changes to backend-dev.agent.md.
        """
        self._write_agent("canonical-agent.agent.md", CANONICAL_SECTIONS_AGENT)
        port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        output_file = self.output_dir / "canonical-agent.mdc"
        self.assertTrue(
            output_file.exists(),
            "Le fichier canonical-agent.mdc doit être créé",
        )
        content = output_file.read_text(encoding="utf-8")

        required_sections = [
            "## Identité & Posture",
            "## Règles de comportement",
            "## Checklist avant livraison",
            "## Contrat de handoff",
        ]
        for section in required_sections:
            self.assertIn(
                section,
                content,
                f"La section '{section}' présente dans l'input doit être préservée dans l'output Cursor",
            )

    def test_cursor_handles_missing_optional_fields(self):
        """Verify the script does not crash on a minimal agent (name + description only)."""
        self._write_agent("minimal-agent.agent.md", MINIMAL_AGENT_CONTENT)

        try:
            results = port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        except Exception as exc:
            self.fail(f"Le script a planté sur un agent minimal : {exc}")

        converted = [r for r in results if r.status in ("converted", "warning")]
        self.assertEqual(
            len(converted),
            1,
            "L'agent minimal doit être converti sans erreur (1 résultat attendu)",
        )
        output_file = self.output_dir / "minimal-agent.mdc"
        self.assertTrue(
            output_file.exists(),
            "Le fichier .mdc doit être créé même pour un agent minimal",
        )

    def test_cursor_output_is_valid_markdown(self):
        """Verify the .mdc has a properly closed frontmatter and a non-truncated body."""
        content = self._run_on_reference_agent()
        lines = content.splitlines()

        # Locate the closing --- of the frontmatter (skip line 0 which is the opening ---)
        closing_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                closing_idx = i
                break

        self.assertIsNotNone(
            closing_idx,
            "Le frontmatter YAML doit être fermé par un second '---'",
        )

        # Body after frontmatter must not be truncated
        body = "\n".join(lines[closing_idx + 1 :]).strip()
        self.assertGreater(
            len(body),
            200,
            "Le corps du .mdc ne doit pas être tronqué (minimum 200 caractères attendus)",
        )

        # description field must not be blank in the frontmatter
        frontmatter_block = "\n".join(lines[1:closing_idx])
        self.assertNotIn(
            'description: ""',
            frontmatter_block,
            "La description dans le frontmatter ne doit pas être vide",
        )


# ---------------------------------------------------------------------------
# Tests: port_to_claude_code.py
# ---------------------------------------------------------------------------

class TestClaudeCodeTranspilation(unittest.TestCase):
    """Contract tests for port_to_claude_code.py."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_claude_"))
        self.input_agents_dir = self.temp_dir / "agents"
        self.input_agents_dir.mkdir()
        self.input_instructions_dir = self.temp_dir / "instructions"
        self.input_instructions_dir.mkdir()
        self.output_dir = self.temp_dir / "output"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_conversion(self) -> str:
        """Run the claude-code conversion and return the CLAUDE.md content."""
        port_to_claude_code.convert_all(
            self.input_agents_dir,
            self.input_instructions_dir,
            self.output_dir,
        )
        claude_md = self.output_dir / "CLAUDE.md"
        self.assertTrue(
            claude_md.exists(),
            "Le fichier CLAUDE.md doit être généré par la conversion",
        )
        return claude_md.read_text(encoding="utf-8")

    def test_claude_output_contains_all_agents(self):
        """Verify that CLAUDE.md contains an entry for each agent that was processed."""
        # Use a small set of representative agents to keep the test fast
        agent_names = ["backend-dev", "frontend-dev", "qa-engineer"]
        copied = []
        for name in agent_names:
            source = AGENTS_DIR / f"{name}.agent.md"
            if source.exists():
                shutil.copy(source, self.input_agents_dir / f"{name}.agent.md")
                copied.append(name)

        self.assertGreater(len(copied), 0, "Aucun agent de référence trouvé sur le disque")

        content = self._run_conversion()

        for name in copied:
            self.assertIn(
                name,
                content,
                f"L'agent '{name}' doit apparaître dans CLAUDE.md après conversion",
            )

    def test_claude_output_preserves_agent_names(self):
        """Verify that the reference agent name (backend-dev) is present in CLAUDE.md."""
        shutil.copy(REFERENCE_AGENT, self.input_agents_dir / "backend-dev.agent.md")

        content = self._run_conversion()

        self.assertIn(
            "backend-dev",
            content,
            "Le nom 'backend-dev' doit être présent dans CLAUDE.md",
        )

    def test_claude_handles_plugin_agents(self):
        """Verify that agents in _plugins/ subdirectory are NOT processed.

        The script uses a non-recursive glob("*.agent.md"), so agents nested
        inside subdirectories (e.g. _plugins/game-studio/) are excluded purely
        by directory structure — the _ prefix exclusion rule is irrelevant here.
        A top-level agent (no subdirectory) MUST still be processed normally.
        """
        # Mirror the _plugins/game-studio/ directory structure inside the temp agents dir
        plugin_dir = self.input_agents_dir / "_plugins" / "game-studio"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "audio-generator.agent.md").write_text(
            "---\nname: audio-generator\ndescription: Plugin audio\n---\n# Plugin Audio",
            encoding="utf-8",
        )
        # Add a regular top-level agent so conversion has something to process
        shutil.copy(REFERENCE_AGENT, self.input_agents_dir / "backend-dev.agent.md")

        self._run_conversion()

        commands_dir = self.output_dir / ".claude" / "commands"

        # Plugin agent in subdirectory must NOT generate a slash command
        self.assertFalse(
            (commands_dir / "audio-generator.md").exists(),
            "Un agent dans _plugins/ (sous-répertoire) ne doit pas générer de commande slash — "
            "le glob non-récursif l'exclut implicitement",
        )
        # Top-level agent MUST generate a slash command
        self.assertTrue(
            (commands_dir / "backend-dev.md").exists(),
            "L'agent top-level doit générer une commande slash dans .claude/commands/",
        )


# ---------------------------------------------------------------------------
# Tests communs: absence de perte de données lors du roundtrip
# ---------------------------------------------------------------------------

class TestNoDataLossRoundtrip(unittest.TestCase):
    """Verify that essential content survives both transpilation pipelines end-to-end."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_roundtrip_"))
        self.input_dir = self.temp_dir / "agents"
        self.input_dir.mkdir()
        self.instructions_dir = self.temp_dir / "instructions"
        self.instructions_dir.mkdir()
        shutil.copy(REFERENCE_AGENT, self.input_dir / "backend-dev.agent.md")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _extract_headings(self) -> list[str]:
        """Return all ## headings found in the reference agent body."""
        text = REFERENCE_AGENT.read_text(encoding="utf-8")
        _, body = agent_parser.parse_frontmatter(text)
        return [line.strip() for line in body.splitlines() if line.strip().startswith("## ")]

    def test_no_data_loss_cursor_roundtrip(self):
        """Cursor: agent title, description and at least 3 section headings must survive."""
        output_dir = self.temp_dir / "cursor"
        port_to_cursor.convert_agents(self.input_dir, output_dir)

        mdc = output_dir / "backend-dev.mdc"
        self.assertTrue(mdc.exists(), "Le fichier .mdc doit exister après conversion Cursor")
        content = mdc.read_text(encoding="utf-8")

        # Agent title (from body H1)
        self.assertIn(
            "BackendDev",
            content,
            "Le titre 'BackendDev' doit être préservé dans l'output Cursor",
        )
        # Description (from frontmatter, injected into Cursor frontmatter)
        self.assertIn(
            "Backend APIs, services, business logic, integrations",
            content,
            "La description de l'agent doit être préservée dans l'output Cursor",
        )
        # At least 3 ## section headings from the original body
        headings = self._extract_headings()
        preserved = [h for h in headings if h in content]
        self.assertGreaterEqual(
            len(preserved),
            3,
            f"Au moins 3 sections de l'agent original doivent être préservées dans l'output Cursor "
            f"(préservées : {preserved})",
        )

    def test_no_data_loss_claude_roundtrip(self):
        """Claude Code: agent name, description and at least 3 sections must survive."""
        output_dir = self.temp_dir / "claude"
        port_to_claude_code.convert_all(
            self.input_dir, self.instructions_dir, output_dir
        )

        # CLAUDE.md must reference the agent by name
        claude_md = output_dir / "CLAUDE.md"
        self.assertTrue(claude_md.exists(), "Le fichier CLAUDE.md doit exister")
        self.assertIn(
            "backend-dev",
            claude_md.read_text(encoding="utf-8"),
            "Le nom 'backend-dev' doit apparaître dans CLAUDE.md",
        )

        # Slash command file must exist
        command_file = output_dir / ".claude" / "commands" / "backend-dev.md"
        self.assertTrue(
            command_file.exists(),
            "Le fichier .claude/commands/backend-dev.md doit être généré",
        )
        content = command_file.read_text(encoding="utf-8")

        # Description preserved
        self.assertIn(
            "Backend APIs, services, business logic, integrations",
            content,
            "La description doit être préservée dans la commande Claude Code",
        )
        # At least 3 ## section headings preserved
        headings = self._extract_headings()
        preserved = [h for h in headings if h in content]
        self.assertGreaterEqual(
            len(preserved),
            3,
            f"Au moins 3 sections doivent être préservées dans la commande Claude Code "
            f"(préservées : {preserved})",
        )


# ---------------------------------------------------------------------------
# Edge cases (AQ-007-P2)
# ---------------------------------------------------------------------------

# Agent with body empty (frontmatter only)
EMPTY_BODY_AGENT = """\
---
name: empty-body
description: "Agent sans contenu dans le body"
tools: ["read"]
model: Claude Sonnet 4 (copilot)
---
"""

# Agent with UTF-8 characters (emoji, French accents)
UTF8_AGENT = """\
---
name: utf8-agent
description: "Agent avec caractères spéciaux 🚀"
tools: ["read"]
model: Claude Sonnet 4 (copilot)
---
# Agent : UTF8Agent

**Domaine** : Gestion des accès réseau — sécurité périmétrique

## Identité & Posture

L'agent gère les données éphémères et les clés d'accès.
Il supporte les caractères accentués : àâäéèêëïîôùûüÿç — et les emoji : 🔒 🛡️ ✅ ❌.

## Règles de comportement

- Toujours vérifier l'intégrité des données
- Créer des rapports détaillés

## Contrat de handoff

Handoff vers le `security-engineer`.
"""

# Agent with escaped quotes in frontmatter
ESCAPED_QUOTES_AGENT = """\
---
name: escaped-quotes
description: "Agent qui gère les \\"edge cases\\" de parsing"
tools: ["read", "edit"]
model: Claude Sonnet 4 (copilot)
---
# Agent : EscapedQuotes

Contenu de test pour les guillemets échappés.
"""


class TestTranspilationEdgeCases(unittest.TestCase):
    """Edge case tests for transpilation scripts (AQ-007-P2)."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_edge_"))
        self.input_dir = self.temp_dir / "agents"
        self.input_dir.mkdir()
        self.instructions_dir = self.temp_dir / "instructions"
        self.instructions_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_agent(self, filename: str, content: str) -> Path:
        path = self.input_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    # -- Empty body --

    def test_cursor_handles_empty_body(self):
        """Cursor conversion must not crash on an agent with empty body."""
        self._write_agent("empty-body.agent.md", EMPTY_BODY_AGENT)
        try:
            port_to_cursor.convert_agents(self.input_dir, self.temp_dir / "out")
        except Exception as exc:
            self.fail(f"Cursor conversion crashed on empty body agent: {exc}")

    def test_claude_handles_empty_body(self):
        """Claude Code conversion must not crash on an agent with empty body."""
        self._write_agent("empty-body.agent.md", EMPTY_BODY_AGENT)
        try:
            port_to_claude_code.convert_all(
                self.input_dir, self.instructions_dir, self.temp_dir / "out"
            )
        except Exception as exc:
            self.fail(f"Claude Code conversion crashed on empty body agent: {exc}")

    # -- UTF-8 characters --

    def test_cursor_preserves_utf8(self):
        """Cursor conversion must preserve UTF-8 characters (accents, emoji)."""
        self._write_agent("utf8-agent.agent.md", UTF8_AGENT)
        out_dir = self.temp_dir / "out"
        port_to_cursor.convert_agents(self.input_dir, out_dir)
        output = (out_dir / "utf8-agent.mdc").read_text(encoding="utf-8")
        self.assertIn("🚀", output, "Emoji must be preserved in Cursor output")
        self.assertIn("àâäéèêëïîôùûüÿç", output, "French accents must be preserved")

    def test_claude_preserves_utf8(self):
        """Claude Code conversion must preserve UTF-8 characters."""
        self._write_agent("utf8-agent.agent.md", UTF8_AGENT)
        out_dir = self.temp_dir / "out"
        port_to_claude_code.convert_all(
            self.input_dir, self.instructions_dir, out_dir
        )
        cmd_file = out_dir / ".claude" / "commands" / "utf8-agent.md"
        self.assertTrue(cmd_file.exists(), "UTF-8 agent must generate a slash command")
        content = cmd_file.read_text(encoding="utf-8")
        self.assertIn("🚀", content, "Emoji must be preserved in Claude Code output")

    # -- Escaped quotes in frontmatter --

    def test_cursor_handles_escaped_quotes(self):
        """Cursor conversion must not crash on escaped quotes in frontmatter."""
        self._write_agent("escaped-quotes.agent.md", ESCAPED_QUOTES_AGENT)
        try:
            port_to_cursor.convert_agents(self.input_dir, self.temp_dir / "out")
        except Exception as exc:
            self.fail(f"Cursor conversion crashed on escaped quotes: {exc}")
        output_file = self.temp_dir / "out" / "escaped-quotes.mdc"
        self.assertTrue(output_file.exists(), "Output file must be created")

    def test_claude_handles_escaped_quotes(self):
        """Claude Code conversion must not crash on escaped quotes in frontmatter."""
        self._write_agent("escaped-quotes.agent.md", ESCAPED_QUOTES_AGENT)
        try:
            port_to_claude_code.convert_all(
                self.input_dir, self.instructions_dir, self.temp_dir / "out"
            )
        except Exception as exc:
            self.fail(f"Claude Code conversion crashed on escaped quotes: {exc}")


# ---------------------------------------------------------------------------
# Path traversal protection (AQ-207)
# ---------------------------------------------------------------------------

# Agent whose name contains a path traversal payload
PATH_TRAVERSAL_AGENT = """\
---
name: ../../../etc/passwd
description: "Malicious agent"
---
# Malicious
"""

PATH_TRAVERSAL_DOTDOT = """\
---
name: ../../tmp/evil
description: "Another traversal attempt"
---
# Evil
"""


class TestPathTraversal(unittest.TestCase):
    """Verify that agents with path traversal names are skipped by port_to_cursor."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_traversal_"))
        self.input_dir = self.temp_dir / "agents"
        self.input_dir.mkdir()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_agent(self, filename: str, content: str) -> Path:
        path = self.input_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def test_path_traversal_agent_is_skipped(self):
        """An agent with name='../../../etc/passwd' must be skipped, not written."""
        self._write_agent("malicious.agent.md", PATH_TRAVERSAL_AGENT)
        output_dir = self.temp_dir / "output"
        results = port_to_cursor.convert_agents(self.input_dir, output_dir)

        skipped = [r for r in results if r.status == "skipped"]
        self.assertGreater(len(skipped), 0, "The traversal agent must be skipped")

        # Ensure no file was written outside the output directory
        if output_dir.exists():
            written = list(output_dir.rglob("*"))
            for f in written:
                self.assertTrue(
                    str(f.resolve()).startswith(str(output_dir.resolve())),
                    f"File {f} escaped the output directory",
                )

    def test_dotdot_name_is_skipped(self):
        """An agent with name='../../tmp/evil' must be skipped."""
        self._write_agent("evil.agent.md", PATH_TRAVERSAL_DOTDOT)
        output_dir = self.temp_dir / "output"
        results = port_to_cursor.convert_agents(self.input_dir, output_dir)

        skipped = [r for r in results if r.status == "skipped"]
        self.assertGreater(len(skipped), 0, "The dotdot agent must be skipped")


# ---------------------------------------------------------------------------
# Tests: Copilot Agent Hooks must NOT be transpiled (D4)
# ---------------------------------------------------------------------------

class TestHooksNotTranspiled(unittest.TestCase):
    """Verify that Copilot Agent Hooks are NOT transpiled to other formats.

    Decision D4: hooks are Copilot-specific and must be ignored by
    port_to_cursor.py and port_to_claude_code.py.  These tests act as a
    non-regression contract — they should pass today (scripts already ignore
    the hooks directory) and prevent a future accidental copy.
    """

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_hooks_transp_"))
        self.input_dir = self.temp_dir / "agents"
        self.input_dir.mkdir(parents=True)
        self.instructions_dir = self.temp_dir / "instructions"
        self.instructions_dir.mkdir()
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()

        # Write a minimal agent so the transpilers have something to process
        (self.input_dir / "test-agent.agent.md").write_text(
            '---\nname: test-agent\ndescription: "Test"\n---\n'
            "# Test Agent\nBody content.",
            encoding="utf-8",
        )

        # Create a realistic hooks directory at .github/hooks/
        hooks_dir = self.temp_dir / ".github" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "security.hooks.json").write_text(
            '{"version": 1, "hooks": {"preToolUse": [{"command": '
            '"bash .github/hooks/scripts/test.sh", "description": "test"}]}}',
            encoding="utf-8",
        )
        scripts_dir = hooks_dir / "scripts"
        scripts_dir.mkdir()
        script = scripts_dir / "test.sh"
        script.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | 0o755)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -- Cursor: no hooks artefacts in output ---------------------------------

    def test_cursor_output_has_no_hooks_files(self):
        """After Cursor transpilation, no *.hooks.json must appear in output."""
        port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        hooks_files = list(self.output_dir.rglob("*.hooks.json"))
        self.assertEqual(
            hooks_files,
            [],
            "No .hooks.json file should be present in Cursor output",
        )

    def test_cursor_output_has_no_hooks_scripts(self):
        """After Cursor transpilation, no hook shell scripts must appear in output."""
        port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        # Check for any .sh files that would come from hooks/scripts/
        sh_files = [
            f for f in self.output_dir.rglob("*.sh")
            if "hooks" in str(f).lower() or "scripts" in f.parent.name
        ]
        self.assertEqual(
            sh_files,
            [],
            "No hook shell scripts should be present in Cursor output",
        )

    def test_hooks_directory_presence_does_not_crash_cursor(self):
        """Cursor transpilation must not crash when .github/hooks/ exists."""
        try:
            results = port_to_cursor.convert_agents(self.input_dir, self.output_dir)
        except Exception as exc:
            self.fail(
                f"Cursor transpilation crashed with .github/hooks/ present: {exc}"
            )
        converted = [r for r in results if r.status in ("converted", "warning")]
        self.assertGreaterEqual(
            len(converted), 1,
            "At least the test-agent should be converted successfully",
        )

    # -- Claude Code: no hooks artefacts in output ----------------------------

    def test_claude_output_has_no_hooks_files(self):
        """After Claude Code transpilation, no *.hooks.json must appear in output."""
        port_to_claude_code.convert_all(
            self.input_dir,
            self.instructions_dir,
            self.output_dir,
        )
        hooks_files = list(self.output_dir.rglob("*.hooks.json"))
        self.assertEqual(
            hooks_files,
            [],
            "No .hooks.json file should be present in Claude Code output",
        )

    def test_claude_output_has_no_hooks_scripts(self):
        """After Claude Code transpilation, no hook shell scripts must appear in output."""
        port_to_claude_code.convert_all(
            self.input_dir,
            self.instructions_dir,
            self.output_dir,
        )
        sh_files = [
            f for f in self.output_dir.rglob("*.sh")
            if "hooks" in str(f).lower() or "scripts" in f.parent.name
        ]
        self.assertEqual(
            sh_files,
            [],
            "No hook shell scripts should be present in Claude Code output",
        )

    def test_hooks_directory_presence_does_not_crash_claude(self):
        """Claude Code transpilation must not crash when .github/hooks/ exists."""
        try:
            results = port_to_claude_code.convert_all(
                self.input_dir,
                self.instructions_dir,
                self.output_dir,
            )
        except Exception as exc:
            self.fail(
                f"Claude Code transpilation crashed with .github/hooks/ present: {exc}"
            )
        converted = [r for r in results if r.status in ("converted", "warning")]
        self.assertGreaterEqual(
            len(converted), 1,
            "At least the test-agent should be converted successfully",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
