#!/usr/bin/env python3
"""Convertit les agents .agent.md (format GitHub Copilot) vers le format Cursor (.mdc).

Lit tous les `.agent.md` dans `.github/agents/`, convertit le frontmatter YAML
vers le format Cursor et génère les fichiers dans un répertoire de sortie.

Usage:
    python3 scripts/port_to_cursor.py [--agents-dir PATH] [--output-dir PATH]

Options:
    --agents-dir    Répertoire des agents sources
                    (défaut: .github/agents)
    --output-dir    Répertoire de sortie pour les fichiers Cursor
                    (défaut: output/cursor)

Mapping appliqué :
- Emplacement : .github/agents/*.agent.md → .cursor/rules/*.mdc
- Frontmatter : name/description/tools/model → description/globs/alwaysApply
- Tools : convertis en commentaire de capacités (Cursor gère ses outils nativement)
- Délégation : runSubagent → mention documentée dans le body
- Model : champ informatif uniquement (Cursor gère le modèle via UI)

Dépendances : stdlib uniquement (Python 3.10+).
"""

# NOTE: GitHub Copilot Agent Hooks (.github/hooks/) are NOT transpiled.
# Hooks are Copilot-specific (preToolUse, postToolUse, etc.) and have no
# equivalent in Cursor's .mdc format. See ADR-008 for rationale.

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from agent_parser import AgentData, parse_agent_file

log = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    agent: str
    status: str  # "converted", "skipped", "warning"
    message: str = ""
    output_file: str = ""


# ---------------------------------------------------------------------------
# Copilot tools → Cursor capabilities mapping
# ---------------------------------------------------------------------------

TOOL_MAPPING: dict[str, str] = {
    "execute": "terminal (run_terminal_command)",
    "read": "file reading",
    "edit": "file editing",
    "search": "codebase search",
    "web/fetch": "web fetching",
    "web": "web fetching",
    "agent/runSubagent": "⚠️ multi-agent (non supporté nativement — prompt chaining)",
    "agent": "⚠️ multi-agent (non supporté nativement — prompt chaining)",
    "todo": "task management (non supporté — utiliser commentaires TODO)",
}

MODEL_MAPPING: dict[str, str] = {
    "Claude Opus 4.6 (copilot)": "claude-opus-4-6",
    "Claude Sonnet 4 (copilot)": "claude-sonnet-4",
    "GPT-4o (copilot)": "gpt-4o",
    "o3 (copilot)": "o3",
}


# ---------------------------------------------------------------------------
# Conversion Copilot → Cursor
# ---------------------------------------------------------------------------

def convert_to_cursor(agent: AgentData) -> str:
    """Convert an AgentData to Cursor .mdc format."""
    lines: list[str] = ["---"]

    # Description
    desc = agent.description or f"Règle convertie depuis l'agent {agent.name}"
    lines.append(f'description: "{desc}"')

    # alwaysApply — agents invocables par l'utilisateur sont toujours actifs
    lines.append(f"alwaysApply: {str(agent.user_invocable).lower()}")

    # globs — pas d'équivalent direct, on laisse vide (applicable partout)
    lines.append("globs: ")

    lines.append("---")
    lines.append("")

    # Plugin warning
    if agent.plugin:
        lines.append("<!-- ⚠️ Plugin agent: content originates from a third-party plugin pack. Review before use. -->")
        lines.append("")

    # Mapped capabilities comment
    if agent.tools:
        lines.append("<!-- Capacités mappées depuis Copilot tools:")
        warnings = []
        for tool in agent.tools:
            # Skip MCP tool references
            if "/" in tool and "." in tool:
                lines.append(f"  - {tool} → MCP (configurer dans .cursor/mcp.json)")
                continue
            mapped = TOOL_MAPPING.get(tool, f"{tool} (vérifier disponibilité Cursor)")
            lines.append(f"  - {tool} → {mapped}")
            if "⚠️" in mapped:
                warnings.append(mapped)
        lines.append("-->")
        lines.append("")

    # Model note
    if agent.model:
        clean_model = agent.model.strip("[]'\" ")
        cursor_model = MODEL_MAPPING.get(clean_model, clean_model)
        lines.append(f"<!-- Modèle recommandé : {cursor_model} (configurer via sélecteur Cursor UI) -->")
        lines.append("")

    # Multi-agent warning
    if agent.agents:
        lines.append("> **Note de portage** : cet agent utilisait la délégation multi-agent (`runSubagent`).")
        lines.append("> Cursor ne supporte pas le multi-agent natif. Utilisez le prompt chaining")
        lines.append("> ou référencez les règles pertinentes avec `@rules` dans le chat.")
        lines.append("")

    # Skills reference
    if agent.skills:
        lines.append("<!-- Skills référencées (GitHub Copilot Agent Skills) :")
        for skill in agent.skills:
            lines.append(f"  - {skill}")
        lines.append("  Note : les skills ne sont pas supportées nativement par Cursor.")
        lines.append("  Le contenu des skills est inclus inline dans les règles Cursor.")
        lines.append("-->")
        lines.append("")

    # Body content — kept as-is
    lines.append(agent.body)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def convert_agents(agents_dir: Path, output_dir: Path) -> list[ConversionResult]:
    """Convert all agents and return results."""
    results: list[ConversionResult] = []

    agent_files = sorted(agents_dir.glob("*.agent.md"))
    if not agent_files:
        print(f"⚠️  Aucun fichier .agent.md trouvé dans {agents_dir}")
        return results

    output_dir.mkdir(parents=True, exist_ok=True)

    for path in agent_files:
        # Skip reference/internal files
        if path.name.startswith("_"):
            results.append(ConversionResult(
                agent=path.name, status="skipped", message="Fichier interne (_prefixed)"
            ))
            continue

        agent = parse_agent_file(path)
        if agent is None:
            results.append(ConversionResult(
                agent=path.name, status="skipped", message="Frontmatter YAML absent ou invalide"
            ))
            continue

        # Validate agent name to prevent path traversal
        if not re.match(r'^[a-z][a-z0-9-]*$', agent.name):
            log.warning("Skipping agent with invalid name: %s", agent.name)
            results.append(ConversionResult(
                agent=path.name, status="skipped", message="Invalid agent name (path traversal risk)"
            ))
            continue

        cursor_content = convert_to_cursor(agent)
        output_name = f"{agent.name}.mdc"
        output_path = output_dir / output_name
        output_path.write_text(cursor_content, encoding="utf-8")

        warnings = []
        if agent.agents:
            warnings.append("délégation multi-agent non portable")
        for tool in agent.tools:
            if "runSubagent" in tool:
                warnings.append("outil runSubagent non disponible")

        status = "warning" if warnings else "converted"
        msg = "; ".join(warnings) if warnings else "OK"

        results.append(ConversionResult(
            agent=agent.name, status=status, message=msg, output_file=str(output_path)
        ))

    return results


def print_summary(results: list[ConversionResult]) -> None:
    """Print conversion summary."""
    converted = sum(1 for r in results if r.status == "converted")
    warnings = sum(1 for r in results if r.status == "warning")
    skipped = sum(1 for r in results if r.status == "skipped")

    print("\n" + "=" * 60)
    print("  Résumé de conversion Copilot → Cursor")
    print("=" * 60)
    print(f"  ✅ Convertis  : {converted}")
    print(f"  ⚠️  Warnings   : {warnings}")
    print(f"  ⏭️  Ignorés    : {skipped}")
    print(f"  📊 Total      : {len(results)}")
    print("=" * 60)

    if any(r.status == "warning" for r in results):
        print("\nWarnings :")
        for r in results:
            if r.status == "warning":
                print(f"  - {r.agent}: {r.message}")

    if skipped > 0:
        print("\nIgnorés :")
        for r in results:
            if r.status == "skipped":
                print(f"  - {r.agent}: {r.message}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convertit les agents Copilot .agent.md vers le format Cursor .mdc"
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=Path(".github/agents"),
        help="Répertoire des agents (défaut: .github/agents)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/cursor"),
        help="Répertoire de sortie (défaut: output/cursor)",
    )
    args = parser.parse_args()

    if not args.agents_dir.is_dir():
        print(f"❌ Répertoire introuvable : {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    results = convert_agents(args.agents_dir, args.output_dir)
    print_summary(results)

    converted = sum(1 for r in results if r.status in ("converted", "warning"))
    if converted > 0:
        print(f"📁 Fichiers générés dans : {args.output_dir}/")
    else:
        print("Aucun agent converti.")


if __name__ == "__main__":
    main()
