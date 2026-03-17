#!/usr/bin/env python3
"""Convertit les agents .agent.md et instructions (format GitHub Copilot) vers le format Claude Code.

Lit les fichiers .agent.md dans .github/agents/ et les .instructions.md dans
.github/instructions/, puis génère la configuration Claude Code correspondante.

Usage:
    python3 scripts/port_to_claude_code.py [--agents-dir PATH] [--instructions-dir PATH] [--output-dir PATH]

Options:
    --agents-dir        Répertoire des agents sources
                        (défaut: .github/agents)
    --instructions-dir  Répertoire des instructions
                        (défaut: .github/instructions)
    --output-dir        Répertoire de sortie pour les fichiers Claude Code
                        (défaut: output/claude-code)

Structure de sortie :
    output/claude-code/
    ├── CLAUDE.md                    # Instructions projet consolidées
    ├── .claude/
    │   ├── settings.json            # Configuration MCP servers
    │   └── commands/
    │       └── <agent-name>.md      # Slash commands (agents invocables)

Mapping appliqué :
- Agents invocables → .claude/commands/<name>.md (slash commands)
- Agents non-invocables → documentés dans CLAUDE.md (références internes)
- Instructions .instructions.md → sections dans CLAUDE.md avec globs
- Tools Copilot → outils natifs Claude Code :
    execute → Bash | read → Read | edit → Edit/Write | search → Grep/Glob
    web/fetch → WebFetch | agent/runSubagent → SubAgent | todo → TodoRead/TodoWrite
- MCP tools → template dans .claude/settings.json

Dépendances : stdlib uniquement (Python 3.10+).
"""

# NOTE: GitHub Copilot Agent Hooks (.github/hooks/) are NOT transpiled.
# Hooks are Copilot-specific (preToolUse, postToolUse, etc.) and have no
# equivalent in Claude Code's CLAUDE.md format. See ADR-008 for rationale.

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from agent_parser import AgentData, SkillData, parse_agent_file, parse_frontmatter, parse_skill_file

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class InstructionData:
    """Parsed instruction data from a .instructions.md file."""
    apply_to: str = ""
    description: str = ""
    body: str = ""
    source_file: str = ""


@dataclass
class ConversionResult:
    name: str
    kind: str  # "agent" | "instruction"
    status: str  # "converted" | "skipped" | "warning"
    message: str = ""
    output_file: str = ""


# ---------------------------------------------------------------------------
# Copilot tools → Claude Code capabilities mapping
# ---------------------------------------------------------------------------

TOOL_MAPPING: dict[str, str] = {
    "execute": "Bash (intégré)",
    "read": "Read (intégré)",
    "edit": "Edit / Write (intégré)",
    "search": "Grep / Glob (intégré)",
    "web/fetch": "WebFetch (intégré)",
    "web": "WebFetch (intégré)",
    "agent/runSubagent": "SubAgent (intégré — délégation native)",
    "agent": "SubAgent (intégré — délégation native)",
    "todo": "TodoRead / TodoWrite (intégré)",
}

MODEL_MAPPING: dict[str, str] = {
    "Claude Opus 4.6 (copilot)": "claude-opus-4-2025-04-14",
    "Claude Sonnet 4 (copilot)": "claude-sonnet-4-2025-04-14",
    "GPT-4o (copilot)": "⚠️ non disponible (Claude Code = modèles Claude uniquement)",
    "o3 (copilot)": "⚠️ non disponible (Claude Code = modèles Claude uniquement)",
}


def parse_instruction_file(path: Path) -> InstructionData | None:
    """Parse a .instructions.md file into InstructionData."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm, body = parse_frontmatter(text)

    return InstructionData(
        apply_to=fm.get("applyTo", "") if fm else "",
        description=fm.get("description", "") if fm else "",
        body=body.strip() if body else text.strip(),
        source_file=str(path),
    )


# ---------------------------------------------------------------------------
# MCP server extraction
# ---------------------------------------------------------------------------

def is_mcp_tool(tool: str) -> bool:
    """Check if a tool reference is an MCP server pattern."""
    return "/" in tool and "." in tool.split("/")[0]


def extract_mcp_servers(agents: list[AgentData]) -> dict[str, list[str]]:
    """Extract unique MCP server references from agent tools.

    Returns: {server_name: [agent names using it]}
    """
    servers: dict[str, list[str]] = {}

    for agent in agents:
        for tool in agent.tools:
            if is_mcp_tool(tool):
                parts = tool.split("/")
                if len(parts) >= 2:
                    server_name = parts[1]
                    if server_name not in servers:
                        servers[server_name] = []
                    if agent.name not in servers[server_name]:
                        servers[server_name].append(agent.name)

    return servers


# ---------------------------------------------------------------------------
# Conversion: Agent → Claude Code slash command
# ---------------------------------------------------------------------------

def convert_agent_to_command(agent: AgentData) -> str:
    """Convert an AgentData to a Claude Code slash command (.md)."""
    lines: list[str] = []

    # Line 1: command description (shown in /help)
    desc = agent.description or f"Agent converti depuis {agent.name}"
    lines.append(desc)
    lines.append("")

    # $ARGUMENTS placeholder for user input
    lines.append("$ARGUMENTS")
    lines.append("")

    # Generation notice
    lines.append(f"<!-- Auto-généré depuis .github/agents/{agent.name}.agent.md -->")
    lines.append("")

    # Plugin warning
    if agent.plugin:
        lines.append("<!-- ⚠️ Plugin agent: content originates from a third-party plugin pack. Review before use. -->")
        lines.append("")

    # Tool mapping comment
    if agent.tools:
        mapped_lines: list[str] = []
        for tool in agent.tools:
            if is_mcp_tool(tool):
                mapped_lines.append(
                    f"  - {tool} → MCP server (configurer dans .claude/settings.json)"
                )
            else:
                mapped = TOOL_MAPPING.get(
                    tool, f"{tool} (vérifier disponibilité Claude Code)"
                )
                mapped_lines.append(f"  - {tool} → {mapped}")

        lines.append("<!-- Outils Copilot mappés vers Claude Code :")
        lines.extend(mapped_lines)
        lines.append("-->")
        lines.append("")

    # Model note (only when incompatible)
    if agent.model:
        clean_model = agent.model.strip("[]'\" ")
        mapped_model = MODEL_MAPPING.get(clean_model, clean_model)
        if "non disponible" in mapped_model:
            lines.append(f"<!-- ⚠️ Modèle source : {clean_model} — {mapped_model} -->")
            lines.append("")

    # Multi-agent note (informational — Claude Code supports SubAgent natively)
    if agent.agents:
        lines.append(
            "> **Note** : cet agent utilise la délégation multi-agent (`SubAgent`)."
        )
        lines.append(
            "> Claude Code supporte cette fonctionnalité nativement via l'outil SubAgent."
        )
        lines.append("")

    # Body content — kept as-is
    lines.append(agent.body)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Conversion: Instructions → CLAUDE.md
# ---------------------------------------------------------------------------

def build_claude_md(
    instructions: list[InstructionData],
    invocable_agents: list[AgentData],
    non_invocable_agents: list[AgentData],
    mcp_servers: dict[str, list[str]],
    skills: list[SkillData] = None,
) -> str:
    """Generate the consolidated CLAUDE.md content."""
    lines: list[str] = []

    # Header
    lines.append("# Instructions projet")
    lines.append("")
    lines.append("> Auto-généré par `scripts/port_to_claude_code.py`")
    lines.append(
        "> depuis `.github/agents/` et `.github/instructions/` (format GitHub Copilot)."
    )
    lines.append(
        "> Pour modifier, éditez les fichiers source puis relancez le script."
    )
    lines.append("")

    # Instructions sections
    if instructions:
        for inst in sorted(instructions, key=lambda i: i.source_file):
            filename = Path(inst.source_file).name.replace(".instructions.md", "")
            # Handle subdirectory instructions (e.g., project/foo)
            rel_parts = Path(inst.source_file).parts
            try:
                idx = rel_parts.index("instructions")
                rel_path = "/".join(rel_parts[idx + 1 :])
            except ValueError:
                rel_path = filename

            title = filename.replace("-", " ").title()
            lines.append(f"## {title}")
            lines.append("")
            if inst.apply_to:
                lines.append(f"*S'applique aux fichiers : `{inst.apply_to}`*")
                lines.append("")
            lines.append(inst.body)
            lines.append("")
            lines.append("---")
            lines.append("")

    # Skills section
    if skills:
        lines.append("## Skills disponibles")
        lines.append("")
        lines.append("Les skills suivantes sont disponibles dans `.claude/skills/` :")
        lines.append("")
        lines.append("| Skill | Description |")
        lines.append("|---|---|")
        for skill in sorted(skills, key=lambda s: s.name):
            desc = skill.description or "—"
            lines.append(f"| `{skill.name}` | {desc} |")
        lines.append("")

    # Agent index table
    if invocable_agents:
        lines.append("## Agents disponibles (slash commands)")
        lines.append("")
        lines.append(
            "Les agents suivants sont disponibles via `/command-name` dans Claude Code :"
        )
        lines.append("")
        lines.append("| Commande | Description |")
        lines.append("|---|---|")
        for agent in sorted(invocable_agents, key=lambda a: a.name):
            desc = agent.description or "—"
            lines.append(f"| `/{agent.name}` | {desc} |")
        lines.append("")

    # Non-invocable agents (reference only)
    if non_invocable_agents:
        lines.append("## Agents internes (référence)")
        lines.append("")
        lines.append(
            "Ces agents sont des références internes, non invocables directement :"
        )
        lines.append("")
        for agent in sorted(non_invocable_agents, key=lambda a: a.name):
            desc = agent.description or "—"
            lines.append(f"- **{agent.name}** : {desc}")
        lines.append("")

    # MCP servers note
    if mcp_servers:
        lines.append("## Serveurs MCP requis")
        lines.append("")
        lines.append(
            "Les agents suivants utilisent des serveurs MCP à configurer "
            "dans `.claude/settings.json` :"
        )
        lines.append("")
        for server, agents in sorted(mcp_servers.items()):
            lines.append(f"- **{server}** — utilisé par : {', '.join(agents)}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Generate settings.json
# ---------------------------------------------------------------------------

def generate_settings(mcp_servers: dict[str, list[str]]) -> dict:
    """Generate .claude/settings.json with MCP server templates."""
    settings: dict = {}

    if mcp_servers:
        mcp_config: dict = {}
        for server_name in sorted(mcp_servers):
            mcp_config[server_name] = {
                "command": "npx",
                "args": [f"TODO: remplacer par le package npm du serveur {server_name}"],
            }
        settings["mcpServers"] = mcp_config

    return settings


# ---------------------------------------------------------------------------
# Main conversion logic
# ---------------------------------------------------------------------------

def convert_all(
    agents_dir: Path,
    instructions_dir: Path,
    output_dir: Path,
    skills_dir: Path = Path(".github/skills"),
) -> list[ConversionResult]:
    """Convert all agents and instructions, return results."""
    results: list[ConversionResult] = []
    commands_dir = output_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Parse agents ---
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    all_agents: list[AgentData] = []
    invocable_agents: list[AgentData] = []
    non_invocable_agents: list[AgentData] = []

    for path in agent_files:
        if path.name.startswith("_"):
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Fichier interne (_prefixed)",
            ))
            continue

        agent = parse_agent_file(path)
        if agent is None:
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Frontmatter YAML absent ou invalide",
            ))
            continue

        # Validate agent name to prevent path traversal
        if not re.match(r'^[a-z][a-z0-9-]*$', agent.name):
            log.warning("Skipping agent with invalid name: %s", agent.name)
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Invalid agent name (path traversal risk)",
            ))
            continue

        all_agents.append(agent)

        if not agent.user_invocable:
            non_invocable_agents.append(agent)
            results.append(ConversionResult(
                name=agent.name, kind="agent", status="skipped",
                message="Non invocable — référence interne (documenté dans CLAUDE.md)",
            ))
            continue

        invocable_agents.append(agent)

        # Generate slash command
        content = convert_agent_to_command(agent)
        output_path = commands_dir / f"{agent.name}.md"
        output_path.write_text(content, encoding="utf-8")

        warnings: list[str] = []
        if agent.model:
            clean_model = agent.model.strip("[]'\" ")
            mapped = MODEL_MAPPING.get(clean_model, "")
            if "non disponible" in mapped:
                warnings.append(f"modèle {clean_model} non disponible dans Claude Code")

        status = "warning" if warnings else "converted"
        msg = "; ".join(warnings) if warnings else "OK"

        results.append(ConversionResult(
            name=agent.name, kind="agent", status=status,
            message=msg, output_file=str(output_path),
        ))

    # --- 2. Parse instructions ---
    all_instructions: list[InstructionData] = []

    if instructions_dir.is_dir():
        for path in sorted(instructions_dir.rglob("*.instructions.md")):
            inst = parse_instruction_file(path)
            if inst is None:
                results.append(ConversionResult(
                    name=path.name, kind="instruction", status="skipped",
                    message="Lecture échouée",
                ))
                continue

            all_instructions.append(inst)
            results.append(ConversionResult(
                name=path.stem.replace(".instructions", ""),
                kind="instruction", status="converted", message="OK",
            ))

    # --- 3. Extract MCP servers ---
    mcp_servers = extract_mcp_servers(all_agents)

    # --- 3.5. Parse and copy skills ---
    all_skills: list[SkillData] = []
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            # Skip _local/ skills
            if "_local" in skill_md.parts:
                continue
            skill = parse_skill_file(skill_md)
            if skill is not None:
                all_skills.append(skill)
                # Copy skill to .claude/skills/<name>/
                skill_name = skill_md.parent.name
                dest_dir = output_dir / ".claude" / "skills" / skill_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                # Copy all files from the skill folder
                for src_file in skill_md.parent.rglob("*"):
                    if src_file.is_file():
                        rel = src_file.relative_to(skill_md.parent)
                        dest_file = dest_dir / rel
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dest_file)
                results.append(ConversionResult(
                    name=skill_name, kind="skill", status="converted",
                    message="OK", output_file=str(dest_dir / "SKILL.md"),
                ))

    # --- 4. Generate CLAUDE.md ---
    claude_md = build_claude_md(
        all_instructions, invocable_agents, non_invocable_agents, mcp_servers, skills=all_skills
    )
    claude_md_path = output_dir / "CLAUDE.md"
    claude_md_path.write_text(claude_md, encoding="utf-8")

    # --- 5. Generate settings.json ---
    if mcp_servers:
        settings = generate_settings(mcp_servers)
        settings_path = output_dir / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return results


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_summary(results: list[ConversionResult]) -> None:
    """Print conversion summary."""
    agents = [r for r in results if r.kind == "agent"]
    instructions = [r for r in results if r.kind == "instruction"]

    skills = [r for r in results if r.kind == "skill"]

    a_converted = sum(1 for r in agents if r.status == "converted")
    a_warnings = sum(1 for r in agents if r.status == "warning")
    a_skipped = sum(1 for r in agents if r.status == "skipped")
    i_converted = sum(1 for r in instructions if r.status == "converted")
    s_converted = sum(1 for r in skills if r.status == "converted")

    print("\n" + "=" * 60)
    print("  Résumé de conversion Copilot → Claude Code")
    print("=" * 60)
    print("  Agents :")
    print(f"    ✅ Convertis (slash commands) : {a_converted}")
    print(f"    ⚠️  Warnings                  : {a_warnings}")
    print(f"    ⏭️  Ignorés                    : {a_skipped}")
    print("  Instructions :")
    print(f"    ✅ Intégrées dans CLAUDE.md    : {i_converted}")
    print("  Skills :")
    print(f"    ✅ Copiées dans .claude/skills/  : {s_converted}")
    print(f"  📊 Total                        : {len(results)}")
    print("=" * 60)

    if any(r.status == "warning" for r in results):
        print("\nWarnings :")
        for r in results:
            if r.status == "warning":
                print(f"  - [{r.kind}] {r.name}: {r.message}")

    if a_skipped > 0:
        print("\nAgents ignorés :")
        for r in agents:
            if r.status == "skipped":
                print(f"  - {r.name}: {r.message}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convertit les agents Copilot .agent.md vers le format Claude Code"
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=Path(".github/agents"),
        help="Répertoire des agents (défaut: .github/agents)",
    )
    parser.add_argument(
        "--instructions-dir",
        type=Path,
        default=Path(".github/instructions"),
        help="Répertoire des instructions (défaut: .github/instructions)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(".github/skills"),
        help="Répertoire des skills (défaut: .github/skills)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/claude-code"),
        help="Répertoire de sortie (défaut: output/claude-code)",
    )
    args = parser.parse_args()

    if not args.agents_dir.is_dir():
        print(f"❌ Répertoire introuvable : {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    results = convert_all(args.agents_dir, args.instructions_dir, args.output_dir, skills_dir=args.skills_dir)
    print_summary(results)

    converted = sum(1 for r in results if r.status in ("converted", "warning"))
    if converted > 0:
        print(f"📁 Fichiers générés dans : {args.output_dir}/")
        print(f"   ├── CLAUDE.md (instructions consolidées)")
        print(f"   ├── .claude/commands/ (slash commands)")
        if (args.output_dir / ".claude" / "skills").is_dir():
            print(f"   ├── .claude/skills/ (agent skills)")
        if (args.output_dir / ".claude" / "settings.json").exists():
            print(f"   └── .claude/settings.json (config MCP)")
    else:
        print("Aucun fichier converti.")


if __name__ == "__main__":
    main()
