#!/usr/bin/env python3
"""Convert .agent.md agents and instructions (GitHub Copilot format) to Claude Code format.

Reads .agent.md files from .github/agents/, .instructions.md from .github/instructions/,
SKILL.md files from .github/skills/, and .hooks.json from .github/hooks/, then generates
a complete Claude Code configuration optimised for the Agent SDK (sub-agents, skills, hooks).

Usage:
    python3 scripts/port_to_claude_code.py [OPTIONS]

Options:
    --agents-dir        Source agents dir (default: .github/agents)
    --instructions-dir  Source instructions dir (default: .github/instructions)
    --skills-dir        Source skills dir (default: .github/skills)
    --hooks-dir         Source hooks dir (default: .github/hooks)
    --output-dir        Output dir (default: output/claude-code)

Output structure:
    output/claude-code/
    ├── CLAUDE.md                     # Project constitution
    └── .claude/
        ├── settings.json             # MCP servers + permissions + hooks
        ├── commands/
        │   └── <agent-name>.md       # Slash commands (user-invocable agents)
        ├── agents/
        │   └── <agent-name>.md       # Reference profiles (non-invocable agents)
        ├── skills/
        │   └── <name>/               # Skills (copied as-is)
        └── MIGRATION.md              # Gaps, warnings, manual steps

Agent classification:
    orchestrator-lead:    seiji → enhanced slash command with full orchestration protocol
    orchestrator-filiere: non-invocable orchestrators → .claude/agents/ reference profiles
    delegating:           user-invocable with agents: field → slash command + delegation section
    specialized:          standard agents → slash command

Requires: Python 3.10+, stdlib only.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from agent_parser import (
    AgentData,
    SkillData,
    parse_agent_file,
    parse_frontmatter,
    parse_list_value,
    parse_skill_file,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Agent classification
# ---------------------------------------------------------------------------

class AgentTier(Enum):
    ORCHESTRATOR_LEAD    = "orchestrator-lead"     # seiji
    ORCHESTRATOR_FILIERE = "orchestrator-filiere"  # orchestrator-tech/data/product/governance
    DELEGATING           = "delegating"             # user-invocable with agents: field
    SPECIALIZED          = "specialized"            # standard specialized agent


# ---------------------------------------------------------------------------
# Model mapping (corrected IDs)
# ---------------------------------------------------------------------------

# None = not available in Claude Code; DEFAULT_MODEL used as fallback
MODEL_MAPPING: dict[str, str | None] = {
    "Claude Opus 4.6 (copilot)":   "claude-opus-4-6",
    "Claude Sonnet 4.6 (copilot)": "claude-sonnet-4-6",
    "Claude Sonnet 4 (copilot)":   "claude-sonnet-4-6",
    "Claude Haiku 4.5 (copilot)":  "claude-haiku-4-5-20251001",
    "Claude Haiku 4.5":            "claude-haiku-4-5-20251001",
    # Non-Claude models — not available in Claude Code
    "GPT-4o (copilot)":            None,
    "GPT-4.1 (copilot)":           None,
    "GPT-5 mini (copilot)":        None,
    "o3 (copilot)":                None,
    "o3-mini (copilot)":           None,
    "Gemini 2.0 Flash (copilot)":  None,
    "Grok 3 (copilot)":            None,
}

DEFAULT_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Tool mapping (Copilot → Claude Code)
# ---------------------------------------------------------------------------

# Maps Copilot tool names to Claude Code tool names (comma-separated when multiple)
TOOL_MAPPING: dict[str, str] = {
    "execute":          "Bash",
    "read":             "Read",
    "edit":             "Edit, Write",
    "search":           "Grep, Glob",
    "web/fetch":        "WebFetch",
    "web":              "WebFetch",
    "agent/runSubagent": "Agent",
    "agent":            "Agent",
    "todo":             "TodoRead, TodoWrite",
}

TOOL_DESCRIPTIONS: dict[str, str] = {
    "Bash":       "execute shell commands",
    "Read":       "read files and directories",
    "Edit":       "modify existing files",
    "Write":      "create new files",
    "Grep":       "search file content with regex",
    "Glob":       "find files by name pattern",
    "WebFetch":   "fetch web pages and documentation",
    "Agent":      "spawn specialized sub-agents via the Agent tool",
    "TodoRead":   "read the task list",
    "TodoWrite":  "manage the task list",
}


# ---------------------------------------------------------------------------
# Known MCP server packages
# ---------------------------------------------------------------------------

KNOWN_MCP_SERVERS: dict[str, dict] = {
    "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp@latest"],
    },
    "chrome-devtools-mcp": {
        "command": "npx",
        "args": ["-y", "@anthropic/chrome-devtools-mcp@latest"],
    },
    "playwright": {
        "command": "npx",
        "args": ["-y", "@anthropic/playwright-mcp@latest"],
    },
}


# ---------------------------------------------------------------------------
# Hook event mapping (Copilot → Claude Code)
# ---------------------------------------------------------------------------

# None = no Claude Code equivalent (becomes a gap)
HOOK_EVENT_MAP: dict[str, str | None] = {
    "preToolUse":          "PreToolUse",
    "postToolUse":         "PostToolUse",
    "sessionStart":        "SessionStart",
    "agentStop":           "Stop",           # closest equivalent; see HOOK_CAVEATS
    "subagentStop":        "SubagentStop",
    "userPromptSubmitted": "UserPromptSubmit",
    "errorOccurred":       None,             # no Claude Code equivalent
}

# Events that mapped but with behavioural differences to document
HOOK_CAVEATS: dict[str, str] = {
    "agentStop": (
        "Mapped to `Stop` (Claude finishes responding). "
        "Not a precise equivalent to Copilot's `agentStop` (main agent session end)."
    ),
}

# Script name (stem) → tool matchers for PreToolUse/PostToolUse
# Empty string "" means no matcher (applies to all tools / fires unconditionally)
SCRIPT_MATCHERS: dict[str, list[str]] = {
    "pre-tool-security":   ["Bash", "Edit", "Write"],
    "pre-tool-worktree":   ["Edit", "Write"],
    "post-tool-audit":     [""],   # all tools — no matcher
    "post-tool-md-format": ["Edit", "Write"],
    "session-init":        [""],   # SessionStart — no tool matcher
    "session-cleanup":     [""],   # Stop — no tool matcher
    "quality-check":       [""],   # SubagentStop — no tool matcher
    "error-tracker":       [],     # No CC equivalent — gap (handled via HOOK_EVENT_MAP)
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class InstructionData:
    apply_to: str = ""
    description: str = ""
    body: str = ""
    source_file: str = ""


@dataclass
class ConversionResult:
    name: str
    kind: str    # "agent" | "instruction" | "skill" | "hook"
    status: str  # "converted" | "skipped" | "warning" | "gap"
    message: str = ""
    output_file: str = ""


@dataclass
class HookGap:
    """A hook that could not be fully transpiled to Claude Code."""
    copilot_event: str
    script: str
    description: str
    source_file: str
    reason: str


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_instruction_file(path: Path) -> InstructionData | None:
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
# Agent classification
# ---------------------------------------------------------------------------

def classify_agent(agent: AgentData) -> AgentTier:
    """Classify an agent into its output tier.

    orchestrator-tech/data/product/governance are filière routing profiles (not slash commands).
    All other agents — including those with user-invocable: false — get slash commands,
    because in Claude Code the user may invoke any agent directly or via seiji.
    """
    if agent.name == "seiji":
        return AgentTier.ORCHESTRATOR_LEAD
    # Filière orchestrators: non-invocable AND name matches orchestrator-* pattern
    if not agent.user_invocable and agent.name.startswith("orchestrator-"):
        return AgentTier.ORCHESTRATOR_FILIERE
    if agent.agents and parse_list_value(agent.agents):
        return AgentTier.DELEGATING
    return AgentTier.SPECIALIZED


def map_model(copilot_model: str) -> tuple[str, bool]:
    """Map a Copilot model name to a Claude Code model ID.

    Returns (model_id, is_fallback).  is_fallback=True means the original model
    is not available and DEFAULT_MODEL was substituted.
    """
    if not copilot_model:
        return DEFAULT_MODEL, False
    clean = copilot_model.strip("[]'\" ")
    mapped = MODEL_MAPPING.get(clean)
    if mapped is None:
        return DEFAULT_MODEL, True
    return mapped, False


# ---------------------------------------------------------------------------
# MCP utilities
# ---------------------------------------------------------------------------

def is_mcp_tool(tool: str) -> bool:
    return "/" in tool and "." in tool.split("/")[0]


def extract_mcp_servers(agents: list[AgentData]) -> dict[str, list[str]]:
    """Return {server_name: [agent_names]} for all MCP tool references."""
    servers: dict[str, list[str]] = {}
    for agent in agents:
        for tool in agent.tools:
            if is_mcp_tool(tool):
                parts = tool.split("/")
                if len(parts) >= 2:
                    server = parts[1]
                    if server not in servers:
                        servers[server] = []
                    if agent.name not in servers[server]:
                        servers[server].append(agent.name)
    return servers


# ---------------------------------------------------------------------------
# Skill utilities
# ---------------------------------------------------------------------------

def build_skill_map(agents: list[AgentData], skills: list[SkillData]) -> dict[str, list[str]]:
    """Build reverse map: skill_name → [agent_names that declare it]."""
    skill_map: dict[str, list[str]] = {s.name: [] for s in skills}
    for agent in agents:
        for skill_name in agent.skills:
            if skill_name not in skill_map:
                skill_map[skill_name] = []
            if agent.name not in skill_map[skill_name]:
                skill_map[skill_name].append(agent.name)
    return skill_map


# ---------------------------------------------------------------------------
# Command generation helpers
# ---------------------------------------------------------------------------

def _resolved_cc_tools(agent: AgentData) -> list[str]:
    """Return deduplicated list of Claude Code tool names from an agent's tools."""
    seen: set[str] = set()
    result: list[str] = []
    for tool in agent.tools:
        if is_mcp_tool(tool):
            continue
        for cc_tool in TOOL_MAPPING.get(tool, tool).split(", "):
            cc_tool = cc_tool.strip()
            if cc_tool and cc_tool not in seen:
                seen.add(cc_tool)
                result.append(cc_tool)
    return result


def _format_tools_section(agent: AgentData) -> str:
    lines: list[str] = ["## Tools Available", ""]
    native = _resolved_cc_tools(agent)
    mcp: list[str] = []
    seen_mcp: set[str] = set()
    for tool in agent.tools:
        if is_mcp_tool(tool):
            parts = tool.split("/")
            server = parts[1] if len(parts) >= 2 else tool
            if server not in seen_mcp:
                seen_mcp.add(server)
                mcp.append(server)
    if not native and not mcp:
        lines.append("*(no tools declared)*")
        return "\n".join(lines)
    for cc_tool in native:
        desc = TOOL_DESCRIPTIONS.get(cc_tool, "")
        lines.append(f"- **{cc_tool}**" + (f" — {desc}" if desc else ""))
    for server in mcp:
        lines.append(f"- **MCP `{server}`** — configured in `.claude/settings.json`")
    return "\n".join(lines)


def _format_skills_section(agent: AgentData, skills_by_name: dict[str, SkillData]) -> str:
    if not agent.skills:
        return ""
    lines: list[str] = [
        "## Skills",
        "",
        "Invoke these protocols with the Skill tool when the task requires them:",
        "",
    ]
    for skill_name in agent.skills:
        skill = skills_by_name.get(skill_name)
        desc = skill.description if skill else ""
        flags: list[str] = []
        if skill and not skill.user_invocable:
            flags.append("agent-only")
        if skill and skill.disable_model_invocation:
            flags.append("explicit invocation only")
        flag_str = f" *({', '.join(flags)})*" if flags else ""
        line = f"- **`/{skill_name}`**{flag_str}"
        if desc:
            line += f" — {desc}"
        lines.append(line)
    return "\n".join(lines)


def _format_delegation_section(agent: AgentData, all_invocable: list[AgentData]) -> str:
    agents_list = parse_list_value(agent.agents) if agent.agents else []
    if not agents_list:
        return "\n".join([
            "## Reporting",
            "",
            "You do not delegate to other agents. When your task is complete, report back "
            "with a structured handoff block:",
            "",
            "- **For**: who should act on these results",
            "- **Fixed decisions**: what was decided (irreversible choices made)",
            "- **Open questions**: unresolved items requiring follow-up",
            "- **Artifacts**: files created or modified (paths)",
            "- **Next action**: recommended next step",
        ])

    is_wildcard = "*" in agents_list
    lines: list[str] = ["## Sub-Agent Delegation", ""]

    if is_wildcard:
        lines.extend([
            "You can delegate to any agent in the ecosystem via the **Agent tool**.",
            "Before dispatching, consult the Sub-Agent Type Registry in `CLAUDE.md`.",
            "",
            "**Mandatory dispatch format** — every agent prompt MUST start with:",
            "```",
            "Start by reading your configuration file at .claude/commands/<agent-name>.md.",
            "Apply your tools, constraints, and specialization from that file.",
            "```",
            "",
            "Then include: task description, acceptance criteria, and the expected handoff block format.",
            "",
            "**Available agents** — see `CLAUDE.md` Sub-Agent Type Registry.",
        ])
    else:
        lines.append("You can delegate to the following agents via the **Agent tool**:")
        lines.append("")
        by_name = {a.name: a for a in all_invocable}
        for dep_name in agents_list:
            dep = by_name.get(dep_name)
            desc = dep.description if dep else ""
            line = f"- **`/{dep_name}`**"
            if desc:
                line += f" — {desc}"
            lines.append(line)
        lines.extend([
            "",
            "Each dispatch MUST begin with the self-config loading instruction:",
            "```",
            "Start by reading your configuration file at .claude/commands/<agent-name>.md.",
            "Apply your tools, constraints, and specialization from that file.",
            "```",
        ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command generation: main function
# ---------------------------------------------------------------------------

def convert_agent_to_command(
    agent: AgentData,
    skills_by_name: dict[str, SkillData],
    all_invocable: list[AgentData],
) -> str:
    """Convert an AgentData to a Claude Code slash command (.md)."""
    tier = classify_agent(agent)
    model_id, is_fallback = map_model(agent.model)
    clean_model = agent.model.strip("[]'\" ") if agent.model else ""

    parts: list[str] = []

    # --- Frontmatter ---
    fm_lines = ["---"]
    fm_lines.append(f"description: {json.dumps(agent.description or agent.name, ensure_ascii=False)}")
    # Preserve non-invocability: hides from the /menu but Claude can still dispatch the agent
    if not agent.user_invocable:
        fm_lines.append("user-invocable: false")
    fm_lines.append("---")
    parts.append("\n".join(fm_lines))
    parts.append("")

    # --- $ARGUMENTS + generation notice ---
    parts.append("$ARGUMENTS")
    parts.append("")
    parts.append(f"<!-- Auto-generated from .github/agents/{agent.name}.agent.md -->")
    if agent.plugin:
        parts.append("<!-- ⚠️ Plugin agent: review content before use. -->")
    parts.append("")

    # --- Persona preamble ---
    parts.append(f"You are **{agent.name}**, a specialized agent in the renga multi-agent team.")
    parts.append("Read this configuration, then execute the task.")
    parts.append("")

    # --- Configuration section ---
    cfg: list[str] = ["## Configuration", ""]
    if clean_model:
        if is_fallback:
            cfg.append(
                f"- **Model note**: Source agent used `{clean_model}` (not available in Claude Code). "
                f"Using `{model_id}` as default. Adjust with `--model` if needed."
            )
        else:
            cfg.append(f"- **Recommended model**: `{model_id}` (source: `{clean_model}`)")
            if agent.name == "seiji":
                cfg.append(
                    "  Haiku is intentional for orchestration — low token generation, "
                    "high dispatch volume. Override with `--model` if needed."
                )
    if agent.plugin:
        cfg.append(f"- **Plugin**: `{agent.plugin}`")
    parts.append("\n".join(cfg))
    parts.append("")

    # --- Tools section ---
    parts.append(_format_tools_section(agent))
    parts.append("")

    # --- Skills section ---
    skills_section = _format_skills_section(agent, skills_by_name)
    if skills_section:
        parts.append(skills_section)
        parts.append("")

    # --- Seiji: orchestration protocol ---
    if tier == AgentTier.ORCHESTRATOR_LEAD:
        orch: list[str] = [
            "## Orchestration Protocol",
            "",
            "You are the **lead orchestrator**. You do NOT write code, design systems, "
            "or run audits directly. You plan, dispatch, and synthesize.",
            "",
            "**Dispatch via Agent tool** — every sub-agent prompt MUST include:",
            "1. Self-config loading (mandatory):",
            '   `"Start by reading your configuration file at .claude/commands/<agent-name>.md. '
            'Apply your tools, constraints, and specialization from that file."`',
            "2. Task description with acceptance criteria",
            "3. Expected handoff block format (For / Fixed decisions / Open questions / Artifacts / Next action)",
            "",
            "**Filière routing profiles** (read before dispatching):",
            "- `.claude/agents/orchestrator-tech.md` — tech lane (backend, frontend, QA, DevOps, infra)",
            "- `.claude/agents/orchestrator-data.md` — data lane (engineers, scientists, analysts)",
            "- `.claude/agents/orchestrator-product.md` — product lane (PM, strategist, UX, design)",
            "- `.claude/agents/orchestrator-governance.md` — governance lane (compliance, legal, risk)",
        ]
        # Available sub-agents table
        peers = [a for a in all_invocable if a.name != "seiji"]
        if peers:
            orch.extend(["", "**Available sub-agents** (see also `CLAUDE.md` Sub-Agent Type Registry):", ""])
            orch.append("| Agent | Domain | Key skills |")
            orch.append("|---|---|---|")
            for a in sorted(peers, key=lambda x: x.name):
                skills_str = ", ".join(f"`{s}`" for s in a.skills[:3]) if a.skills else "—"
                orch.append(f"| `/{a.name}` | {a.description or '—'} | {skills_str} |")
        parts.append("\n".join(orch))
        parts.append("")

    # --- Delegation / Reporting section ---
    parts.append(_format_delegation_section(agent, all_invocable))
    parts.append("")

    # --- Agent body ---
    parts.append("---")
    parts.append("")
    parts.append(agent.body)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Non-invocable agent reference
# ---------------------------------------------------------------------------

def generate_agent_reference(agent: AgentData) -> str:
    """Generate .claude/agents/<name>.md for a non-invocable agent (filière profile)."""
    lines = [
        "<!-- Non-invocable agent profile: used by seiji for dispatch routing. -->",
        f"<!-- Source: .github/agents/{agent.name}.agent.md -->",
        "",
        f"# Lane Profile: {agent.name}",
        "",
        agent.body,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Hook transpilation
# ---------------------------------------------------------------------------

def transpile_hooks(hooks_dir: Path) -> tuple[dict[str, list], list[HookGap]]:
    """Parse all .hooks.json files; return (cc_hooks_config, gaps).

    cc_hooks_config is ready to embed in settings.json under "hooks".
    gaps is a list of hooks that could not be transpiled.
    """
    cc_hooks: dict[str, list] = {}
    gaps: list[HookGap] = []

    if not hooks_dir.is_dir():
        return cc_hooks, gaps

    # Track (event, matcher, command) triples to avoid duplicates
    seen: set[tuple[str, str, str]] = set()

    for hooks_file in sorted(hooks_dir.glob("*.hooks.json")):
        try:
            data = json.loads(hooks_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log.warning("Cannot parse %s: %s", hooks_file.name, e)
            continue

        for copilot_event, entries in data.get("hooks", {}).items():
            cc_event = HOOK_EVENT_MAP.get(copilot_event)

            for entry in entries:
                command = entry.get("command", "")
                description = entry.get("description", "")
                script_stem = Path(command.split()[-1]).stem if command else ""

                if cc_event is None:
                    gaps.append(HookGap(
                        copilot_event=copilot_event,
                        script=command,
                        description=description,
                        source_file=hooks_file.name,
                        reason=f"No Claude Code equivalent for `{copilot_event}`",
                    ))
                    continue

                matchers = SCRIPT_MATCHERS.get(script_stem, [""])

                for matcher in matchers:
                    key = (cc_event, matcher, command)
                    if key in seen:
                        continue
                    seen.add(key)

                    if cc_event not in cc_hooks:
                        cc_hooks[cc_event] = []

                    hook_obj: dict = {"type": "command", "command": command}
                    entry_obj: dict = {"hooks": [hook_obj]}
                    if matcher:
                        entry_obj["matcher"] = matcher

                    cc_hooks[cc_event].append(entry_obj)

    return cc_hooks, gaps


# ---------------------------------------------------------------------------
# Settings generation
# ---------------------------------------------------------------------------

def generate_permissions(agents: list[AgentData]) -> dict:
    """Generate baseline permissions from the union of all agent tool declarations."""
    allow: set[str] = set()
    for agent in agents:
        for tool in agent.tools:
            if is_mcp_tool(tool):
                parts = tool.split("/")
                server = parts[1] if len(parts) >= 2 else tool
                allow.add(f"mcp__{server}__*")
            else:
                cc = TOOL_MAPPING.get(tool, "")
                for t in cc.split(", "):
                    t = t.strip()
                    if t:
                        allow.add(t)
    return {"allow": sorted(allow), "deny": []}


def generate_settings(
    mcp_servers: dict[str, list[str]],
    agents: list[AgentData],
    hooks_config: dict[str, list],
) -> dict:
    """Generate full .claude/settings.json: MCP servers + permissions + hooks."""
    settings: dict = {}

    # Permissions (union of all agent tool needs)
    settings["permissions"] = generate_permissions(agents)

    # MCP servers
    if mcp_servers:
        mcp_config: dict = {}
        for server_name in sorted(mcp_servers):
            if server_name in KNOWN_MCP_SERVERS:
                mcp_config[server_name] = KNOWN_MCP_SERVERS[server_name].copy()
            else:
                mcp_config[server_name] = {
                    "command": "npx",
                    "args": [f"TODO: replace with npm package for {server_name}"],
                }
        settings["mcpServers"] = mcp_config

    # Hooks
    if hooks_config:
        settings["hooks"] = hooks_config

    return settings


# ---------------------------------------------------------------------------
# CLAUDE.md generation
# ---------------------------------------------------------------------------

def build_claude_md(
    instructions: list[InstructionData],
    classified: dict[AgentTier, list[AgentData]],
    skill_map: dict[str, list[str]],
    skills: list[SkillData],
    mcp_servers: dict[str, list[str]],
) -> str:
    lines: list[str] = []

    invocable = (
        classified.get(AgentTier.ORCHESTRATOR_LEAD, [])
        + classified.get(AgentTier.DELEGATING, [])
        + classified.get(AgentTier.SPECIALIZED, [])
    )
    filiere = classified.get(AgentTier.ORCHESTRATOR_FILIERE, [])

    # --- Header ---
    lines += [
        "# Project Instructions",
        "",
        "> Auto-generated by `scripts/port_to_claude_code.py`",
        "> from `.github/agents/`, `.github/instructions/`, and `.github/skills/`.",
        "> To modify, edit the source files and re-run the script.",
        "",
    ]

    # --- Agent Ecosystem section ---
    lines += ["## Agent Ecosystem", ""]
    total = len(invocable) + len(filiere)
    lines.append(
        f"This project uses a multi-agent architecture with **{total} specialized agents**. "
        "The lead orchestrator is **seiji** (`/seiji`), which plans, dispatches, "
        "and synthesizes results from domain-expert sub-agents."
    )
    lines.append("")

    if filiere:
        lines.append("**Filière orchestrators** (non-invocable; seiji reads these during planning):")
        lines.append("")
        for agent in sorted(filiere, key=lambda a: a.name):
            lines.append(f"- **{agent.name}** — {agent.description or '—'} "
                          f"(profile: `.claude/agents/{agent.name}.md`)")
        lines.append("")

    # --- Sub-Agent Type Registry table ---
    if invocable:
        lines += [
            "### Sub-Agent Type Registry",
            "",
            "Use these agent types when dispatching via the Agent tool:",
            "",
            "| Slash command | Agent | Description | Skills |",
            "|---|---|---|---|",
        ]
        for agent in sorted(invocable, key=lambda a: a.name):
            skills_str = ", ".join(f"`{s}`" for s in agent.skills[:4]) if agent.skills else "—"
            lines.append(
                f"| `/{agent.name}` | {agent.name} | {agent.description or '—'} | {skills_str} |"
            )
        lines.append("")

    # --- Skills section ---
    if skills:
        lines += [
            "## Skills",
            "",
            "Skills are reusable protocols invocable via `/skill-name`:",
            "",
            "| Skill | Description | Declared by |",
            "|---|---|---|",
        ]
        for skill in sorted(skills, key=lambda s: s.name):
            users = skill_map.get(skill.name, [])
            users_str = ", ".join(f"`{a}`" for a in sorted(users)[:5]) if users else "—"
            flags = ""
            if not skill.user_invocable:
                flags = " *(agent-only)*"
            elif skill.disable_model_invocation:
                flags = " *(explicit only)*"
            lines.append(
                f"| `/{skill.name}`{flags} | {skill.description or '—'} | {users_str} |"
            )
        lines.append("")

    # --- File-pattern instructions ---
    if instructions:
        lines += [
            "## File-Pattern Instructions",
            "",
            "Apply the following rules when working with the specified file types.",
            "These replace Copilot's `applyTo` auto-injection — Claude applies them contextually.",
            "",
        ]
        for inst in sorted(instructions, key=lambda i: i.source_file):
            filename = Path(inst.source_file).name.replace(".instructions.md", "")
            title = filename.replace("-", " ").title()
            section_header = f"### {title}"
            if inst.apply_to:
                section_header += f" (`{inst.apply_to}`)"
            lines.append(section_header)
            lines.append("")
            lines.append(inst.body)
            lines.append("")
            lines.append("---")
            lines.append("")

    # --- MCP servers ---
    if mcp_servers:
        lines += [
            "## MCP Servers",
            "",
            "The following MCP servers are configured in `.claude/settings.json`:",
            "",
        ]
        for server, agent_names in sorted(mcp_servers.items()):
            lines.append(f"- **{server}** — used by: {', '.join(f'`{n}`' for n in agent_names)}")
        lines.append("")

    # --- Working memory note ---
    lines += [
        "## Working Memory",
        "",
        "Agent working memory is stored in `.renga/`. "
        "See skill `working-memory` for the full structure and conventions.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MIGRATION.md generation
# ---------------------------------------------------------------------------

def generate_migration_notes(
    agents: list[AgentData],
    hook_gaps: list[HookGap],
    hook_caveats: dict[str, list[str]],  # {copilot_event: [descriptions]}
) -> str:
    lines: list[str] = [
        "# Migration Notes: Copilot → Claude Code",
        "",
        "> Auto-generated by `scripts/port_to_claude_code.py`.",
        "> Review these notes after running the transpiler.",
        "",
    ]

    # --- Model compatibility ---
    model_rows: list[tuple[str, str, str, str]] = []
    for agent in sorted(agents, key=lambda a: a.name):
        if not agent.model:
            continue
        clean = agent.model.strip("[]'\" ")
        model_id, is_fallback = map_model(agent.model)
        status = "⚠️ Substituted (fallback)" if is_fallback else "✅ Direct map"
        model_rows.append((agent.name, clean, model_id, status))

    if model_rows:
        lines += [
            "## Model Compatibility",
            "",
            "| Agent | Source model | Claude Code model | Status |",
            "|---|---|---|---|",
        ]
        for agent_name, src, cc, status in model_rows:
            lines.append(f"| `{agent_name}` | `{src}` | `{cc}` | {status} |")
        lines.append("")

    # --- Hook transpilation gaps ---
    if hook_gaps:
        lines += [
            "## Hook Transpilation Gaps",
            "",
            "The following Copilot hooks have no direct Claude Code equivalent "
            "and were NOT added to `settings.json`:",
            "",
            "| Copilot event | Script | Reason | Impact |",
            "|---|---|---|---|",
        ]
        for gap in hook_gaps:
            impact = gap.description or "—"
            lines.append(
                f"| `{gap.copilot_event}` | `{gap.script}` | {gap.reason} | {impact} |"
            )
        lines.append("")

    # --- Hook caveats (partial mappings) ---
    if hook_caveats:
        lines += ["## Hook Mapping Caveats", ""]
        for event, descs in sorted(hook_caveats.items()):
            caveat = HOOK_CAVEATS.get(event, "")
            lines.append(f"### `{event}`")
            lines.append("")
            if caveat:
                lines.append(f"**Caveat**: {caveat}")
                lines.append("")
            for desc in descs:
                lines.append(f"- {desc}")
            lines.append("")

    # --- Behavioural differences ---
    lines += [
        "## Behavioural Differences",
        "",
        "### Permissions model",
        "",
        "- **Copilot**: per-agent tool declarations (`tools:` frontmatter)",
        "- **Claude Code**: global permissions in `settings.json`",
        "",
        "The generated `permissions.allow` list is the **union** of all agent tool requirements.",
        "This means every session has access to all tools. To restrict per-session, use the",
        "`--allowedTools` CLI flag or edit `settings.json`.",
        "",
        "### Skill invocation",
        "",
        "- **Copilot**: skills in `skills:` frontmatter are auto-loaded by the runtime",
        "- **Claude Code**: skills must be explicitly invoked via `/skill-name` or the Skill tool",
        "",
        "Slash commands include `/skill-name` invocation instructions for each declared skill.",
        "",
        "### File-pattern instructions (`applyTo`)",
        "",
        "- **Copilot**: `applyTo` globs auto-inject instructions when matching files are in context",
        "- **Claude Code**: instructions are in `CLAUDE.md` with documented globs; Claude applies",
        "  them contextually but without automatic enforcement",
        "",
        "### Sub-agent isolation",
        "",
        "- **Copilot**: `runSubagent` runs in a separate context with its own tool access",
        "- **Claude Code**: the Agent tool spawns a sub-agent that inherits the parent's",
        "  permissions. No per-agent tool scoping is enforced at runtime.",
        "",
    ]

    # --- Manual steps ---
    lines += [
        "## Manual Steps Required",
        "",
        "1. **MCP servers**: verify npm package names and add required env vars in `settings.json`.",
        "2. **Hook scripts**: verify `.github/hooks/scripts/*.sh` handle Claude Code's JSON payload.",
        "   Key difference: tool names are PascalCase in Claude Code (`Bash`, `Edit`) vs lowercase",
        "   in Copilot (`bash`, `edit`). Scripts using hardcoded tool name whitelists need updating.",
        "3. **Model selection**: review model annotations in slash commands; adjust `--model` as needed.",
        "4. **Working memory**: `.renga/` is filesystem-based and works identically in both environments.",
        "   No migration needed.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def convert_all(
    agents_dir: Path,
    instructions_dir: Path,
    output_dir: Path,
    skills_dir: Path = Path(".github/skills"),
    hooks_dir: Path = Path(".github/hooks"),
) -> list[ConversionResult]:
    """Convert all agents, instructions, skills, and hooks. Return results."""
    results: list[ConversionResult] = []

    commands_dir = output_dir / ".claude" / "commands"
    agents_ref_dir = output_dir / ".claude" / "agents"
    skills_out_dir = output_dir / ".claude" / "skills"
    commands_dir.mkdir(parents=True, exist_ok=True)
    agents_ref_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. Parse agents ----
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    all_agents: list[AgentData] = []
    classified: dict[AgentTier, list[AgentData]] = {t: [] for t in AgentTier}

    for path in agent_files:
        if path.name.startswith("_"):
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Internal file (_prefixed)",
            ))
            continue

        agent = parse_agent_file(path)
        if agent is None:
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Missing or invalid YAML frontmatter",
            ))
            continue

        if not re.match(r"^[a-z][a-z0-9-]*$", agent.name):
            log.warning("Skipping agent with invalid name: %s", agent.name)
            results.append(ConversionResult(
                name=path.name, kind="agent", status="skipped",
                message="Invalid agent name (path traversal risk)",
            ))
            continue

        all_agents.append(agent)
        tier = classify_agent(agent)
        classified[tier].append(agent)

    # Collect all user-invocable agents for cross-references
    all_invocable: list[AgentData] = (
        classified[AgentTier.ORCHESTRATOR_LEAD]
        + classified[AgentTier.DELEGATING]
        + classified[AgentTier.SPECIALIZED]
    )

    # ---- 2. Parse skills ----
    all_skills: list[SkillData] = []
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            if "_local" in skill_md.parts:
                continue
            skill = parse_skill_file(skill_md)
            if skill is not None:
                all_skills.append(skill)
                # Copy skill to output
                skill_name = skill_md.parent.name
                dest_dir = skills_out_dir / skill_name
                dest_dir.mkdir(parents=True, exist_ok=True)
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

    skills_by_name = {s.name: s for s in all_skills}
    skill_map = build_skill_map(all_agents, all_skills)

    # ---- 3. Generate slash commands (user-invocable agents) ----
    for agent in all_invocable:
        _, is_fallback = map_model(agent.model)
        content = convert_agent_to_command(agent, skills_by_name, all_invocable)
        out_path = commands_dir / f"{agent.name}.md"
        out_path.write_text(content, encoding="utf-8")

        warnings: list[str] = []
        if is_fallback:
            clean = agent.model.strip("[]'\" ")
            warnings.append(f"model `{clean}` not available in Claude Code; using {DEFAULT_MODEL}")

        results.append(ConversionResult(
            name=agent.name, kind="agent",
            status="warning" if warnings else "converted",
            message="; ".join(warnings) if warnings else "OK",
            output_file=str(out_path),
        ))

    # ---- 4. Generate reference profiles (non-invocable agents) ----
    for agent in classified[AgentTier.ORCHESTRATOR_FILIERE]:
        content = generate_agent_reference(agent)
        out_path = agents_ref_dir / f"{agent.name}.md"
        out_path.write_text(content, encoding="utf-8")
        results.append(ConversionResult(
            name=agent.name, kind="agent", status="converted",
            message="Reference profile in .claude/agents/",
            output_file=str(out_path),
        ))

    # ---- 5. Parse instructions ----
    all_instructions: list[InstructionData] = []
    if instructions_dir.is_dir():
        for path in sorted(instructions_dir.rglob("*.instructions.md")):
            inst = parse_instruction_file(path)
            if inst is None:
                results.append(ConversionResult(
                    name=path.name, kind="instruction", status="skipped",
                    message="Read failed",
                ))
                continue
            all_instructions.append(inst)
            results.append(ConversionResult(
                name=path.stem.replace(".instructions", ""),
                kind="instruction", status="converted", message="OK",
            ))

    # ---- 6. Extract MCP servers ----
    mcp_servers = extract_mcp_servers(all_agents)

    # ---- 7. Transpile hooks ----
    hooks_config, hook_gaps = transpile_hooks(hooks_dir)

    # Collect caveats for MIGRATION.md
    hook_caveats: dict[str, list[str]] = {}
    for gap in hook_gaps:
        pass  # gaps are documented separately; caveats come from HOOK_CAVEATS

    # Build caveat list from hook events that mapped with warnings
    if hooks_dir.is_dir():
        for hooks_file in hooks_dir.glob("*.hooks.json"):
            try:
                data = json.loads(hooks_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for copilot_event, entries in data.get("hooks", {}).items():
                if copilot_event in HOOK_CAVEATS and HOOK_EVENT_MAP.get(copilot_event):
                    if copilot_event not in hook_caveats:
                        hook_caveats[copilot_event] = []
                    for entry in entries:
                        desc = entry.get("description", "")
                        if desc and desc not in hook_caveats[copilot_event]:
                            hook_caveats[copilot_event].append(desc)

    for gap in hook_gaps:
        results.append(ConversionResult(
            name=gap.copilot_event, kind="hook", status="gap",
            message=gap.reason,
        ))

    if hooks_config:
        results.append(ConversionResult(
            name="hooks", kind="hook", status="converted",
            message=f"{sum(len(v) for v in hooks_config.values())} hook entries transpiled",
        ))

    # ---- 8. Generate CLAUDE.md ----
    claude_md = build_claude_md(all_instructions, classified, skill_map, all_skills, mcp_servers)
    claude_md_path = output_dir / "CLAUDE.md"
    claude_md_path.write_text(claude_md, encoding="utf-8")

    # ---- 9. Generate settings.json ----
    settings = generate_settings(mcp_servers, all_agents, hooks_config)
    settings_path = output_dir / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # ---- 10. Generate MIGRATION.md ----
    migration = generate_migration_notes(all_agents, hook_gaps, hook_caveats)
    migration_path = output_dir / ".claude" / "MIGRATION.md"
    migration_path.write_text(migration, encoding="utf-8")

    return results


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_summary(results: list[ConversionResult]) -> None:
    agents      = [r for r in results if r.kind == "agent"]
    instructions = [r for r in results if r.kind == "instruction"]
    skills      = [r for r in results if r.kind == "skill"]
    hooks       = [r for r in results if r.kind == "hook"]

    a_conv = sum(1 for r in agents if r.status == "converted")
    a_warn = sum(1 for r in agents if r.status == "warning")
    a_skip = sum(1 for r in agents if r.status == "skipped")
    i_conv = sum(1 for r in instructions if r.status == "converted")
    s_conv = sum(1 for r in skills if r.status == "converted")
    h_conv = sum(1 for r in hooks if r.status == "converted")
    h_gaps = sum(1 for r in hooks if r.status == "gap")

    print("\n" + "=" * 62)
    print("  Copilot → Claude Code conversion summary")
    print("=" * 62)
    print("  Agents:")
    print(f"    ✅ Slash commands + profiles  : {a_conv}")
    print(f"    ⚠️  Warnings (model fallback)  : {a_warn}")
    print(f"    ⏭️  Skipped                    : {a_skip}")
    print("  Instructions:")
    print(f"    ✅ Embedded in CLAUDE.md      : {i_conv}")
    print("  Skills:")
    print(f"    ✅ Copied to .claude/skills/  : {s_conv}")
    print("  Hooks:")
    print(f"    ✅ Transpiled to settings.json: {h_conv}")
    print(f"    ⚠️  Gaps (no CC equivalent)   : {h_gaps}")
    print(f"  📊 Total items processed       : {len(results)}")
    print("=" * 62)

    if any(r.status == "warning" for r in results):
        print("\nWarnings:")
        for r in results:
            if r.status == "warning":
                print(f"  [{r.kind}] {r.name}: {r.message}")

    if h_gaps:
        print("\nHook gaps (see .claude/MIGRATION.md):")
        for r in hooks:
            if r.status == "gap":
                print(f"  - {r.name}: {r.message}")

    if a_skip > 0:
        print("\nSkipped agents:")
        for r in agents:
            if r.status == "skipped":
                print(f"  - {r.name}: {r.message}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Copilot .agent.md agents to Claude Code format"
    )
    parser.add_argument("--agents-dir", type=Path, default=Path(".github/agents"))
    parser.add_argument("--instructions-dir", type=Path, default=Path(".github/instructions"))
    parser.add_argument("--skills-dir", type=Path, default=Path(".github/skills"))
    parser.add_argument("--hooks-dir", type=Path, default=Path(".github/hooks"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/claude-code"))
    args = parser.parse_args()

    if not args.agents_dir.is_dir():
        print(f"❌ Directory not found: {args.agents_dir}", file=sys.stderr)
        sys.exit(1)

    results = convert_all(
        args.agents_dir,
        args.instructions_dir,
        args.output_dir,
        skills_dir=args.skills_dir,
        hooks_dir=args.hooks_dir,
    )
    print_summary(results)

    converted = sum(1 for r in results if r.status in ("converted", "warning"))
    if converted > 0:
        out = args.output_dir
        print(f"📁 Output written to: {out}/")
        print(f"   ├── CLAUDE.md")
        print(f"   ├── .claude/commands/     (slash commands)")
        print(f"   ├── .claude/agents/       (filière reference profiles)")
        if (out / ".claude" / "skills").is_dir():
            print(f"   ├── .claude/skills/       (skills)")
        print(f"   ├── .claude/settings.json (MCP + permissions + hooks)")
        print(f"   └── .claude/MIGRATION.md  (gaps and manual steps)")
    else:
        print("No files converted.")


if __name__ == "__main__":
    main()
