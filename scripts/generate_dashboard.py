#!/usr/bin/env python3
"""Génère un dashboard de performance à partir des fichiers de mémoire.

Parse `.copilot/memory/agent-performance.md` et `.copilot/memory/error-patterns.md`
pour produire un rapport Markdown avec KPIs, classements et tendances.

Usage:
    python3 scripts/generate_dashboard.py [--memory-dir PATH] [--output PATH]

Options:
    --memory-dir    Répertoire contenant les fichiers de mémoire
                    (défaut: .copilot/memory)
    --output        Chemin du rapport généré
                    (défaut: reports/dashboard.md)

Le script fonctionne avec des fichiers vides ou absents (affiche "Pas de données").
Dépendances : stdlib uniquement (Python 3.10+).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

from agent_parser import parse_markdown_table


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PerformanceEntry:
    date: str
    session: str
    agent: str
    task: str
    score: int
    comment: str


@dataclass
class ErrorPattern:
    pattern_id: str
    pattern: str
    agents: list[str]
    occurrences: int
    first_seen: str
    last_seen: str
    action: str


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_performance(path: Path) -> list[PerformanceEntry]:
    """Parse agent-performance.md and return scored entries."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")

    # Find the Historique table
    section = text.split("## Historique")[-1] if "## Historique" in text else text
    rows = parse_markdown_table(section)
    entries: list[PerformanceEntry] = []
    for cells in rows:
        if len(cells) < 5:
            continue
        try:
            score = int(cells[4])
        except (ValueError, IndexError):
            continue
        entries.append(PerformanceEntry(
            date=cells[0],
            session=cells[1],
            agent=cells[2],
            task=cells[3],
            score=score,
            comment=cells[5] if len(cells) > 5 else "",
        ))
    return entries


def parse_error_patterns(path: Path) -> tuple[list[ErrorPattern], list[dict[str, str]]]:
    """Parse error-patterns.md — returns (active_patterns, resolved_patterns)."""
    if not path.exists():
        return [], []
    text = path.read_text(encoding="utf-8")

    active: list[ErrorPattern] = []
    resolved: list[dict[str, str]] = []

    # Active patterns
    active_section = ""
    if "## Patterns actifs" in text:
        active_section = text.split("## Patterns actifs")[1]
        if "## Patterns résolus" in active_section:
            active_section = active_section.split("## Patterns résolus")[0]

    for cells in parse_markdown_table(active_section):
        if len(cells) < 6:
            continue
        try:
            occ = int(cells[3])
        except (ValueError, IndexError):
            continue
        active.append(ErrorPattern(
            pattern_id=cells[0],
            pattern=cells[1],
            agents=[a.strip() for a in cells[2].split(",") if a.strip()],
            occurrences=occ,
            first_seen=cells[4],
            last_seen=cells[5],
            action=cells[6] if len(cells) > 6 else "",
        ))

    # Resolved patterns
    resolved_section = ""
    if "## Patterns résolus" in text:
        resolved_section = text.split("## Patterns résolus")[1]

    for cells in parse_markdown_table(resolved_section):
        if len(cells) >= 3:
            resolved.append({
                "id": cells[0],
                "pattern": cells[1],
                "resolution": cells[2],
                "date": cells[3] if len(cells) > 3 else "",
            })

    return active, resolved


# ---------------------------------------------------------------------------
# Dashboard generation
# ---------------------------------------------------------------------------

def generate_dashboard(
    entries: list[PerformanceEntry],
    active_errors: list[ErrorPattern],
    resolved_errors: list[dict[str, str]],
    skills_count: int = 0,
) -> str:
    """Generate the Markdown dashboard report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = [
        "# Dashboard de Performance — Agent Team",
        "",
        f"> Généré le {now}",
        "",
    ]

    if not entries and not active_errors:
        lines += [
            "## Pas de données",
            "",
            "Aucune donnée de performance ou d'erreur n'a été enregistrée.",
            "Alimentez `.copilot/memory/agent-performance.md` et "
            "`.copilot/memory/error-patterns.md` pour générer un dashboard.",
            "",
        ]
        return "\n".join(lines)

    # --- KPIs globaux ---
    lines += ["## KPIs globaux", ""]

    total_tasks = len(entries)
    retries = sum(1 for e in entries if e.score <= 2)
    avg_score = mean(e.score for e in entries) if entries else 0
    retry_rate = (retries / total_tasks * 100) if total_tasks > 0 else 0

    lines += [
        "| KPI | Valeur |",
        "|---|---|",
        f"| Nombre total de tâches | {total_tasks} |",
        f"| Score moyen global | {avg_score:.2f} / 5 |",
        f"| Taux de retry (score ≤ 2) | {retry_rate:.1f}% ({retries}/{total_tasks}) |"
        if total_tasks > 0 else
        "| Taux de retry (score ≤ 2) | N/A |",
        f"| Patterns d'erreur actifs | {len(active_errors)} |",
        f"| Patterns d'erreur résolus | {len(resolved_errors)} |",
        f"| Skills installées | {skills_count} |",
        "",
    ]

    # --- Classement par agent ---
    if entries:
        agent_scores: dict[str, list[int]] = defaultdict(list)
        for e in entries:
            agent_scores[e.agent].append(e.score)

        ranked = sorted(
            [(agent, mean(scores), len(scores)) for agent, scores in agent_scores.items()],
            key=lambda x: x[1],
            reverse=True,
        )

        lines += ["## Classement des agents", ""]
        lines += [
            "| Rang | Agent | Score moyen | Nb tâches | Min | Max |",
            "|---|---|---|---|---|---|",
        ]
        for i, (agent, avg, count) in enumerate(ranked, 1):
            scores = agent_scores[agent]
            lines.append(
                f"| {i} | {agent} | {avg:.2f} | {count} | {min(scores)} | {max(scores)} |"
            )
        lines.append("")

        # Top 3 / Bottom 3
        if len(ranked) >= 3:
            lines += ["### Top 3 agents", ""]
            for agent, avg, count in ranked[:3]:
                lines.append(f"- **{agent}** — {avg:.2f}/5 ({count} tâches)")
            lines.append("")

            lines += ["### Bottom 3 agents", ""]
            for agent, avg, count in ranked[-3:]:
                lines.append(f"- **{agent}** — {avg:.2f}/5 ({count} tâches)")
            lines.append("")

        # --- Tendance par agent (dernières N sessions) ---
        lines += ["## Tendance par agent (dernières sessions)", ""]
        max_trend = 10
        for agent, scores_list in sorted(agent_scores.items()):
            recent = scores_list[-max_trend:]
            trend_str = " → ".join(str(s) for s in recent)
            direction = ""
            if len(recent) >= 2:
                if recent[-1] > recent[0]:
                    direction = " 📈"
                elif recent[-1] < recent[0]:
                    direction = " 📉"
                else:
                    direction = " ➡️"
            lines.append(f"- **{agent}** : {trend_str}{direction}")
        lines.append("")

    # --- Patterns d'erreur ---
    if active_errors:
        lines += ["## Patterns d'erreur les plus fréquents", ""]
        sorted_errors = sorted(active_errors, key=lambda e: e.occurrences, reverse=True)
        lines += [
            "| # | ID | Pattern | Agent(s) | Occurrences | Action |",
            "|---|---|---|---|---|---|",
        ]
        for i, ep in enumerate(sorted_errors, 1):
            agents_str = ", ".join(ep.agents) if ep.agents else "—"
            lines.append(
                f"| {i} | {ep.pattern_id} | {ep.pattern} | {agents_str} "
                f"| {ep.occurrences} | {ep.action} |"
            )
        lines.append("")

    if resolved_errors:
        lines += ["## Patterns résolus", ""]
        lines += [
            "| ID | Pattern | Résolution | Date |",
            "|---|---|---|---|",
        ]
        for rp in resolved_errors:
            lines.append(
                f"| {rp['id']} | {rp['pattern']} | {rp['resolution']} | {rp['date']} |"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "*Rapport généré par `scripts/generate_dashboard.py` — stdlib Python uniquement.*",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Génère le dashboard de performance")
    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=Path(".copilot/memory"),
        help="Répertoire mémoire (défaut: .copilot/memory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/dashboard.md"),
        help="Chemin du rapport (défaut: reports/dashboard.md)",
    )
    args = parser.parse_args()

    perf_path = args.memory_dir / "agent-performance.md"
    errors_path = args.memory_dir / "error-patterns.md"

    entries = parse_performance(perf_path)
    active_errors, resolved_errors = parse_error_patterns(errors_path)

    # Count installed skills
    skills_dir = args.memory_dir.parent.parent / ".github" / "skills"
    skills_count = sum(
        1 for d in skills_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "SKILL.md").exists()
    ) if skills_dir.is_dir() else 0

    report = generate_dashboard(entries, active_errors, resolved_errors, skills_count=skills_count)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"✅ Dashboard généré : {args.output}")
    print(f"   {len(entries)} entrées de performance, {len(active_errors)} patterns actifs")


if __name__ == "__main__":
    main()
