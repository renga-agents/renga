"""Tests for scripts/build_dist.py."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from build_dist import (
    _build_manifest,
    _copy_agents,
    _copy_cli,
    _copy_config_example,
    _copy_instructions,
    _copy_plugins,
    _copy_references,
    _copy_schema,
    _copy_skills,
    _resolve_version,
    _sha256,
    _stem_key,
)

try:
    from build_dist import _copy_hooks
except ImportError:
    _copy_hooks = None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mini_project(tmp_path: Path) -> Path:
    """Create a minimal renga project structure."""
    # .github/agents/
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "test-agent.agent.md").write_text(
        "---\nname: test-agent\ndescription: Test\n---\n# Body"
    )

    # .github/agents/_references/
    refs_dir = agents_dir / "_references"
    refs_dir.mkdir()
    (refs_dir / "error-catalog.md").write_text("# Error catalog")

    # .github/agents/_plugins/my-plugin/
    plugin_dir = agents_dir / "_plugins" / "my-plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin-agent.agent.md").write_text(
        "---\nname: plugin-agent\ndescription: Plugin\n---\n# Plugin body"
    )

    # .github/agents/_local/ (should be excluded)
    local_dir = agents_dir / "_local"
    local_dir.mkdir()
    (local_dir / "local-agent.agent.md").write_text("---\nname: local\n---\n# Local")

    # .github/instructions/
    instr_dir = tmp_path / ".github" / "instructions"
    instr_dir.mkdir(parents=True)
    (instr_dir / "typescript.instructions.md").write_text("# TS instructions")

    # .github/instructions/_local/ (should be excluded)
    instr_local = instr_dir / "_local"
    instr_local.mkdir()
    (instr_local / "custom.instructions.md").write_text("# Custom")

    # schemas/
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "agent.schema.json").write_text('{"type": "object"}')

    # .renga.example.yml
    (tmp_path / ".renga.example.yml").write_text(
        'project:\n  framework_version: "1.0.0"'
    )

    # .github/skills/
    skill_dir = tmp_path / ".github" / "skills" / "task-decomposition"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: task-decomposition\ndescription: Decompose tasks\n---\n# Steps"
    )

    # .github/skills/_local/ (should be excluded)
    skills_local = tmp_path / ".github" / "skills" / "_local"
    skills_local.mkdir(parents=True)
    (skills_local / "SKILL.md").write_text("---\nname: local-skill\n---\n# Local")

    # schemas/skill.schema.json
    (schema_dir / "skill.schema.json").write_text('{"type": "object"}')

    # scripts/renga.sh
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "renga.sh").write_text("#!/usr/bin/env bash\necho hello")

    # .github/hooks/
    hooks_dir = tmp_path / ".github" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "security.hooks.json").write_text(json.dumps({
        "version": 1,
        "hooks": {
            "preToolUse": [{
                "command": "bash .github/hooks/scripts/pre-tool-security.sh",
                "description": "Security enforcement"
            }]
        }
    }))

    # .github/hooks/scripts/
    hooks_scripts_dir = hooks_dir / "scripts"
    hooks_scripts_dir.mkdir()
    script = hooks_scripts_dir / "pre-tool-security.sh"
    script.write_text("#!/usr/bin/env bash\nexit 0\n")
    script.chmod(script.stat().st_mode | 0o755)

    # .github/hooks/_local/ (should be excluded)
    hooks_local = hooks_dir / "_local"
    hooks_local.mkdir()
    (hooks_local / "dev-only.hooks.json").write_text(json.dumps({
        "version": 1,
        "hooks": {"preToolUse": []}
    }))

    return tmp_path


@pytest.fixture
def dist_dir(tmp_path: Path) -> Path:
    """Return a clean output directory for the build."""
    out = tmp_path / "dist"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# TestSha256
# ---------------------------------------------------------------------------


class TestSha256:
    """Tests for _sha256 helper."""

    def test_known_content(self, tmp_path: Path) -> None:
        """A file with known content produces the expected SHA-256 digest."""
        f = tmp_path / "hello.txt"
        f.write_bytes(b"hello")
        expected = hashlib.sha256(b"hello").hexdigest()
        assert _sha256(f) == expected

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        """Two files with identical content yield the same hash."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        content = b"deterministic content"
        f1.write_bytes(content)
        f2.write_bytes(content)
        assert _sha256(f1) == _sha256(f2)

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        """Files with different content produce different hashes."""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"alpha")
        f2.write_bytes(b"beta")
        assert _sha256(f1) != _sha256(f2)


# ---------------------------------------------------------------------------
# TestStemKey
# ---------------------------------------------------------------------------


class TestStemKey:
    """Tests for _stem_key helper."""

    def test_agent_md_suffix(self, tmp_path: Path) -> None:
        assert _stem_key(Path("foo.agent.md")) == "foo"

    def test_instructions_md_suffix(self, tmp_path: Path) -> None:
        assert _stem_key(Path("typescript.instructions.md")) == "typescript"

    def test_plain_file(self, tmp_path: Path) -> None:
        assert _stem_key(Path("readme.md")) == "readme"


# ---------------------------------------------------------------------------
# TestResolveVersion
# ---------------------------------------------------------------------------


class TestResolveVersion:
    """Tests for _resolve_version."""

    def test_cli_version_takes_priority(self, tmp_path: Path) -> None:
        """Explicit CLI version overrides everything."""
        (tmp_path / ".renga.example.yml").write_text(
            'project:\n  framework_version: "2.0.0"'
        )
        assert _resolve_version("3.5.0", tmp_path) == "3.5.0"

    def test_reads_version_from_config(self, tmp_path: Path) -> None:
        """Version is extracted from .renga.example.yml."""
        (tmp_path / ".renga.example.yml").write_text(
            'project:\n  framework_version: "1.2.3"'
        )
        assert _resolve_version(None, tmp_path) == "1.2.3"

    def test_fallback_when_no_config(self, tmp_path: Path) -> None:
        """Falls back to 0.0.0-dev when no config file exists."""
        assert _resolve_version(None, tmp_path) == "0.0.0-dev"


# ---------------------------------------------------------------------------
# TestBuildDist — integration via individual copy functions + manifest
# ---------------------------------------------------------------------------


class TestBuildDist:
    """Integration tests exercising the full build pipeline."""

    def _run_build(self, root: Path, output: Path) -> dict:
        """Run all copy steps and build the manifest, mirroring main()."""
        _copy_agents(root, output)
        _copy_references(root, output)
        _copy_plugins(root, output)
        _copy_instructions(root, output)
        _copy_skills(root, output)
        _copy_schema(root, output)
        _copy_config_example(root, output)
        _copy_cli(root, output)

        version = _resolve_version(None, root)
        manifest = _build_manifest(output, version)
        manifest_path = output / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return manifest

    # -- Existence checks --

    def test_build_creates_dist_dir(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        assert dist_dir.is_dir()

    def test_agent_copied(self, mini_project: Path, dist_dir: Path) -> None:
        self._run_build(mini_project, dist_dir)
        assert (dist_dir / "agents" / "test-agent.agent.md").is_file()

    def test_references_copied(self, mini_project: Path, dist_dir: Path) -> None:
        self._run_build(mini_project, dist_dir)
        assert (
            dist_dir / "agents" / "_references" / "error-catalog.md"
        ).is_file()

    def test_plugin_copied_to_plugins(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        assert (
            dist_dir / "plugins" / "my-plugin" / "plugin-agent.agent.md"
        ).is_file()

    def test_local_excluded(self, mini_project: Path, dist_dir: Path) -> None:
        """Files under _local/ must NOT appear anywhere in dist/."""
        self._run_build(mini_project, dist_dir)
        all_files = [f.name for f in dist_dir.rglob("*") if f.is_file()]
        assert "local-agent.agent.md" not in all_files

    def test_instructions_copied(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        assert (
            dist_dir / "instructions" / "typescript.instructions.md"
        ).is_file()

    def test_instructions_local_excluded(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Instructions under _local/ must NOT appear in dist/."""
        self._run_build(mini_project, dist_dir)
        all_files = [f.name for f in dist_dir.rglob("*") if f.is_file()]
        assert "custom.instructions.md" not in all_files

    def test_schema_copied(self, mini_project: Path, dist_dir: Path) -> None:
        self._run_build(mini_project, dist_dir)
        assert (dist_dir / "schemas" / "agent.schema.json").is_file()

    def test_cli_executable(self, mini_project: Path, dist_dir: Path) -> None:
        self._run_build(mini_project, dist_dir)
        cli = dist_dir / "renga"
        assert cli.is_file()
        assert os.access(cli, os.X_OK)

    # -- Manifest structure --

    def test_manifest_valid_json(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        manifest_path = dist_dir / "manifest.json"
        assert manifest_path.is_file()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_manifest_has_version(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert manifest["version"] == "1.0.0"

    def test_manifest_has_agents(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "test-agent" in manifest["agents"]
        assert "sha256" in manifest["agents"]["test-agent"]
        assert "path" in manifest["agents"]["test-agent"]

    def test_manifest_has_plugins(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "my-plugin" in manifest["plugins"]
        plugin = manifest["plugins"]["my-plugin"]
        assert "plugin-agent" in plugin["agents"]
        assert "files" in plugin

    def test_manifest_has_instructions(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "typescript" in manifest["instructions"]
        assert "sha256" in manifest["instructions"]["typescript"]

    def test_manifest_has_references(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "error-catalog" in manifest["references"]

    def test_manifest_has_schemas(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "schemas" in manifest
        assert "agent.schema.json" in manifest["schemas"]
        assert "skill.schema.json" in manifest["schemas"]
        assert "sha256" in manifest["schemas"]["agent.schema.json"]

    def test_skills_copied(self, mini_project: Path, dist_dir: Path) -> None:
        self._run_build(mini_project, dist_dir)
        assert (
            dist_dir / "skills" / "task-decomposition" / "SKILL.md"
        ).is_file()

    def test_skills_local_excluded(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        local_dir = dist_dir / "skills" / "_local"
        assert not local_dir.exists()

    def test_manifest_has_skills(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        manifest = self._run_build(mini_project, dist_dir)
        assert "skills" in manifest
        assert "task-decomposition" in manifest["skills"]
        skill = manifest["skills"]["task-decomposition"]
        assert "sha256" in skill
        assert "path" in skill
        assert "assets" in skill

    def test_config_example_copied(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        self._run_build(mini_project, dist_dir)
        assert (dist_dir / ".renga.example.yml").is_file()


# ---------------------------------------------------------------------------
# TestBuildDistHooks — TDD red tests for _copy_hooks integration
# ---------------------------------------------------------------------------


@pytest.mark.skipif(_copy_hooks is None, reason="_copy_hooks not yet implemented")
class TestBuildDistHooks:
    """Tests for hooks integration in build_dist."""

    def _run_build_with_hooks(self, root: Path, output: Path) -> dict:
        """Run the full build pipeline including _copy_hooks."""
        _copy_agents(root, output)
        _copy_references(root, output)
        _copy_plugins(root, output)
        _copy_instructions(root, output)
        _copy_skills(root, output)
        _copy_schema(root, output)
        _copy_config_example(root, output)
        _copy_cli(root, output)
        _copy_hooks(root, output)

        version = _resolve_version(None, root)
        manifest = _build_manifest(output, version)
        manifest_path = output / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return manifest

    def test_hooks_json_copied(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Hook JSON config files are copied to dist/hooks/."""
        self._run_build_with_hooks(mini_project, dist_dir)
        hooks_files = list((dist_dir / "hooks").glob("*.hooks.json"))
        assert len(hooks_files) >= 1
        assert (dist_dir / "hooks" / "security.hooks.json").is_file()

    def test_hooks_scripts_copied(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Hook shell scripts are copied to dist/hooks/scripts/."""
        self._run_build_with_hooks(mini_project, dist_dir)
        scripts = list((dist_dir / "hooks" / "scripts").glob("*.sh"))
        assert len(scripts) >= 1
        assert (dist_dir / "hooks" / "scripts" / "pre-tool-security.sh").is_file()

    def test_hooks_scripts_executable(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Copied hook scripts retain their executable permission."""
        self._run_build_with_hooks(mini_project, dist_dir)
        script = dist_dir / "hooks" / "scripts" / "pre-tool-security.sh"
        assert script.is_file()
        assert os.access(script, os.X_OK)

    def test_manifest_has_hooks_section(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Manifest contains a 'hooks' section with entries."""
        manifest = self._run_build_with_hooks(mini_project, dist_dir)
        assert "hooks" in manifest
        assert len(manifest["hooks"]) >= 1

    def test_manifest_hooks_entry_has_sha256(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Each hook entry in the manifest has sha256 and path fields."""
        manifest = self._run_build_with_hooks(mini_project, dist_dir)
        assert "hooks" in manifest
        for key, entry in manifest["hooks"].items():
            assert "sha256" in entry, f"hook '{key}' missing sha256"
            assert "path" in entry, f"hook '{key}' missing path"

    def test_hooks_local_excluded(
        self, mini_project: Path, dist_dir: Path
    ) -> None:
        """Files under .github/hooks/_local/ must NOT appear in dist/."""
        self._run_build_with_hooks(mini_project, dist_dir)
        all_files = [f.name for f in dist_dir.rglob("*") if f.is_file()]
        assert "dev-only.hooks.json" not in all_files
        local_dir = dist_dir / "hooks" / "_local"
        assert not local_dir.exists()

    def test_no_hooks_directory_graceful(
        self, tmp_path: Path, dist_dir: Path
    ) -> None:
        """When .github/hooks/ does not exist, no error and no hooks in manifest."""
        # Arrange — minimal project without hooks
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "a.agent.md").write_text(
            "---\nname: a\ndescription: A\n---\n# A"
        )
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        (schema_dir / "agent.schema.json").write_text('{"type": "object"}')
        (schema_dir / "skill.schema.json").write_text('{"type": "object"}')
        (tmp_path / ".renga.example.yml").write_text(
            'project:\n  framework_version: "1.0.0"'
        )
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "renga.sh").write_text("#!/usr/bin/env bash\necho hi")

        # Act
        _copy_agents(tmp_path, dist_dir)
        _copy_schema(tmp_path, dist_dir)
        _copy_config_example(tmp_path, dist_dir)
        _copy_cli(tmp_path, dist_dir)
        _copy_hooks(tmp_path, dist_dir)

        version = _resolve_version(None, tmp_path)
        manifest = _build_manifest(dist_dir, version)

        # Assert
        assert "hooks" not in manifest
