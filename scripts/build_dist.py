#!/usr/bin/env python3
"""Build the distribution artifact for renga.

Creates a dist/ directory with agents, instructions, schema, config example,
CLI script and a manifest.json with SHA-256 checksums.

Usage:
    python3 scripts/build_dist.py
    python3 scripts/build_dist.py --version 1.2.0
    python3 scripts/build_dist.py --output-dir build/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

# Minimum CLI version required to consume this distribution
MIN_CLI_VERSION = "1.0.0"

# Directories / files to exclude from any copy
EXCLUDED_DIRS = {"_local"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    """Return hex SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stem_key(path: Path) -> str:
    """Derive a manifest key from filename (strip extensions like .agent.md)."""
    name = path.name
    for suffix in (".agent.md", ".instructions.md"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return path.stem


def _copy_file(src: Path, dest: Path) -> None:
    """Copy a single file, creating parent dirs as needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _copy_tree_filtered(src: Path, dest: Path) -> None:
    """Recursively copy a directory, excluding EXCLUDED_DIRS."""
    if not src.is_dir():
        return
    for item in sorted(src.iterdir()):
        if item.name in EXCLUDED_DIRS:
            continue
        target = dest / item.name
        if item.is_dir():
            _copy_tree_filtered(item, target)
        else:
            _copy_file(item, target)


# ---------------------------------------------------------------------------
# Version resolution
# ---------------------------------------------------------------------------

def _resolve_version(cli_version: str | None, root: Path) -> str:
    """Determine the distribution version.

    Priority: CLI arg → framework_version in config example → fallback.
    """
    if cli_version:
        return cli_version

    config_path = root / ".renga.example.yml"
    if config_path.exists():
        text = config_path.read_text(encoding="utf-8")
        match = re.search(r'framework_version:\s*"?([^"\n]+)"?', text)
        if match:
            return match.group(1).strip()

    return "0.0.0-dev"


# ---------------------------------------------------------------------------
# Copy operations
# ---------------------------------------------------------------------------

def _copy_agents(root: Path, output: Path) -> list[Path]:
    """Copy root-level .agent.md files to dist/agents/."""
    agents_src = root / ".github" / "agents"
    if not agents_src.is_dir():
        log.error("Agents directory not found: %s", agents_src)
        raise SystemExit(1)

    agents_dest = output / "agents"
    copied: list[Path] = []

    for f in sorted(agents_src.glob("*.agent.md")):
        dest = agents_dest / f.name
        _copy_file(f, dest)
        copied.append(dest)

    return copied


def _copy_references(root: Path, output: Path) -> list[Path]:
    """Copy _references/ → dist/agents/_references/."""
    refs_src = root / ".github" / "agents" / "_references"
    refs_dest = output / "agents" / "_references"
    if not refs_src.is_dir():
        return []

    _copy_tree_filtered(refs_src, refs_dest)
    return sorted(refs_dest.rglob("*") if refs_dest.exists() else [])


def _copy_plugins(root: Path, output: Path) -> list[Path]:
    """Copy _plugins/ → dist/plugins/ (renamed)."""
    plugins_src = root / ".github" / "agents" / "_plugins"
    plugins_dest = output / "plugins"
    if not plugins_src.is_dir():
        return []

    _copy_tree_filtered(plugins_src, plugins_dest)
    return sorted(plugins_dest.rglob("*") if plugins_dest.exists() else [])


def _copy_instructions(root: Path, output: Path) -> list[Path]:
    """Copy instructions/ → dist/instructions/, excluding _local/."""
    inst_src = root / ".github" / "instructions"
    inst_dest = output / "instructions"
    if not inst_src.is_dir():
        return []

    _copy_tree_filtered(inst_src, inst_dest)
    return sorted(inst_dest.rglob("*") if inst_dest.exists() else [])


def _copy_skills(root: Path, output: Path) -> list[Path]:
    """Copy .github/skills/ → dist/skills/, excluding _local/."""
    skills_src = root / ".github" / "skills"
    skills_dest = output / "skills"
    if not skills_src.is_dir():
        return []

    _copy_tree_filtered(skills_src, skills_dest)
    return sorted(skills_dest.rglob("*") if skills_dest.exists() else [])


def _copy_schema(root: Path, output: Path) -> list[Path]:
    """Copy schemas/*.json → dist/schemas/."""
    copied: list[Path] = []
    for schema_name in ("agent.schema.json", "skill.schema.json", "hooks.schema.json"):
        schema_src = root / "schemas" / schema_name
        if not schema_src.exists():
            if schema_name == "agent.schema.json":
                log.warning("Schema file not found: %s", schema_src)
            continue
        schema_dest = output / "schemas" / schema_name
        _copy_file(schema_src, schema_dest)
        copied.append(schema_dest)
    return copied


def _copy_config_example(root: Path, output: Path) -> Path | None:
    """Copy .renga.example.yml → dist/."""
    config_src = root / ".renga.example.yml"
    if not config_src.exists():
        log.warning("Config example not found: %s", config_src)
        return None
    config_dest = output / ".renga.example.yml"
    _copy_file(config_src, config_dest)
    return config_dest


def _copy_cli(root: Path, output: Path) -> Path | None:
    """Copy scripts/renga.sh → dist/renga (chmod +x)."""
    cli_src = root / "scripts" / "renga.sh"
    if not cli_src.exists():
        log.warning("CLI script not found: %s", cli_src)
        return None
    cli_dest = output / "renga"
    _copy_file(cli_src, cli_dest)
    cli_dest.chmod(cli_dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return cli_dest


def _copy_hooks(root: Path, output: Path) -> list[Path]:
    """Copy .github/hooks/ → dist/hooks/, excluding _local/."""
    hooks_src = root / ".github" / "hooks"
    hooks_dest = output / "hooks"
    if not hooks_src.is_dir():
        return []

    _copy_tree_filtered(hooks_src, hooks_dest)

    # Ensure scripts are executable
    scripts_dir = hooks_dest / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.glob("*.sh"):
            script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return sorted(hooks_dest.rglob("*") if hooks_dest.exists() else [])


# ---------------------------------------------------------------------------
# Manifest generation
# ---------------------------------------------------------------------------

def _build_manifest(output: Path, version: str) -> dict:
    """Build the manifest.json structure from the dist/ tree."""
    manifest: dict = {
        "version": version,
        "date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        "min_cli_version": MIN_CLI_VERSION,
        "agents": {},
        "instructions": {},
        "references": {},
        "skills": {},
        "plugins": {},
    }

    # --- Agents (root-level) ---
    agents_dir = output / "agents"
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.agent.md")):
            key = _stem_key(f)
            manifest["agents"][key] = {
                "sha256": _sha256(f),
                "path": f.relative_to(output).as_posix(),
            }

    # --- References ---
    refs_dir = output / "agents" / "_references"
    if refs_dir.is_dir():
        for f in sorted(refs_dir.rglob("*")):
            if f.is_file():
                key = f.stem
                manifest["references"][key] = {
                    "sha256": _sha256(f),
                    "path": f.relative_to(output).as_posix(),
                }

    # --- Instructions ---
    inst_dir = output / "instructions"
    if inst_dir.is_dir():
        for f in sorted(inst_dir.rglob("*")):
            if f.is_file():
                key = _stem_key(f)
                manifest["instructions"][key] = {
                    "sha256": _sha256(f),
                    "path": f.relative_to(output).as_posix(),
                }

    # --- Skills ---
    skills_dir = output / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            skill_name = skill_md.parent.name
            # Collect companion assets
            assets = []
            for asset in sorted(skill_md.parent.rglob("*")):
                if asset.is_file() and asset != skill_md:
                    assets.append(asset.relative_to(output).as_posix())
            manifest["skills"][skill_name] = {
                "sha256": _sha256(skill_md),
                "path": skill_md.relative_to(output).as_posix(),
                "assets": assets,
            }

    # --- Plugins ---
    plugins_dir = output / "plugins"
    if plugins_dir.is_dir():
        for pack_dir in sorted(plugins_dir.iterdir()):
            if not pack_dir.is_dir():
                continue
            pack_name = pack_dir.name
            agent_files = sorted(pack_dir.glob("*.agent.md"))
            agents_list = [_stem_key(a) for a in agent_files]
            files_map: dict[str, dict[str, str]] = {}
            for f in sorted(pack_dir.rglob("*")):
                if f.is_file():
                    files_map[f.name] = {
                        "sha256": _sha256(f),
                        "path": f.relative_to(output).as_posix(),
                    }
            manifest["plugins"][pack_name] = {
                "version": version,
                "agents": agents_list,
                "files": files_map,
            }

    # --- Hooks ---
    hooks_dir = output / "hooks"
    if hooks_dir.is_dir():
        manifest["hooks"] = {}
        for f in sorted(hooks_dir.rglob("*")):
            if f.is_file():
                key = f.name
                manifest["hooks"][key] = {
                    "sha256": _sha256(f),
                    "path": f.relative_to(output).as_posix(),
                }

    # --- Schema ---
    for schema_name in ("agent.schema.json", "skill.schema.json", "hooks.schema.json"):
        schema_path = output / "schemas" / schema_name
        if schema_path.exists():
            manifest.setdefault("schemas", {})
            manifest["schemas"][schema_name] = {
                "sha256": _sha256(schema_path),
                "path": schema_path.relative_to(output).as_posix(),
            }

    # Backward compat: keep singular "schema" key for older consumers
    if "schemas" in manifest and "agent.schema.json" in manifest["schemas"]:
        manifest["schema"] = manifest["schemas"]["agent.schema.json"]

    # --- Config example ---
    config_path = output / ".renga.example.yml"
    if config_path.exists():
        manifest["config_example"] = {
            "sha256": _sha256(config_path),
            "path": config_path.relative_to(output).as_posix(),
        }

    return manifest


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def _print_summary(output: Path, manifest: dict) -> None:
    """Print a human-readable build summary."""
    n_agents = len(manifest.get("agents", {}))
    n_instructions = len(manifest.get("instructions", {}))
    n_references = len(manifest.get("references", {}))
    n_skills = len(manifest.get("skills", {}))
    plugins = manifest.get("plugins", {})
    n_plugins = len(plugins)
    n_hooks = len(manifest.get("hooks", {}))

    # Count all files in dist (excluding manifest.json itself)
    total_files = sum(1 for f in output.rglob("*") if f.is_file() and f.name != "manifest.json")

    lines = [
        f"✅ Distribution built: {output}/",
        f"   Version: {manifest['version']}",
        f"   Agents: {n_agents}",
        f"   Instructions: {n_instructions}",
        f"   References: {n_references}",
        f"   Skills: {n_skills}",
    ]
    if n_plugins:
        plugin_details = ", ".join(
            f"{name}: {len(info['agents'])} agents" for name, info in plugins.items()
        )
        lines.append(f"   Plugins: {n_plugins} ({plugin_details})")
    else:
        lines.append("   Plugins: 0")
    lines.append(f"   Hooks: {n_hooks}")
    lines.append(f"   Total files: {total_files}")

    print("\n".join(lines))  # noqa: T201


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    """Entry point for build_dist."""
    parser = argparse.ArgumentParser(description="Build renga distribution")
    parser.add_argument("--version", type=str, default=None, help="Version semver")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("dist"), help="Output directory"
    )
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    output: Path = args.output_dir
    if not output.is_absolute():
        output = root / output

    version = _resolve_version(args.version, root)

    # Clean previous build
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    # Copy all artifacts
    _copy_agents(root, output)
    _copy_references(root, output)
    _copy_plugins(root, output)
    _copy_instructions(root, output)
    _copy_skills(root, output)
    _copy_schema(root, output)
    _copy_config_example(root, output)
    _copy_cli(root, output)
    _copy_hooks(root, output)

    # Build and write manifest
    manifest = _build_manifest(output, version)
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    _print_summary(output, manifest)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
