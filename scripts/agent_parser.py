"""Shared parser for .agent.md files (YAML frontmatter + AgentData).

Centralises ``parse_frontmatter``, ``parse_list_value``, ``AgentData``
and ``parse_agent_file`` — used by validate_agents.py, port_to_cursor.py
and port_to_claude_code.py.

Stdlib only (no PyYAML).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["parse_frontmatter", "parse_list_value", "parse_markdown_table", "AgentData", "parse_agent_file", "SkillData", "parse_skill_file"]

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Extract YAML frontmatter from text.

    Returns (parsed_dict | None, markdown_body).
    The parser handles simple key: value, key: [list], key: 'quoted',
    and key: "quoted" patterns — sufficient for agent frontmatter.
    """
    if not text.startswith("---"):
        return None, text

    end_match = re.search(r"\n---\s*\n", text[3:])
    if end_match is None:
        return None, text

    yaml_block = text[3 : 3 + end_match.start()]
    body = text[3 + end_match.end() :]

    result: dict[str, str] = {}
    seen_keys: set[str] = set()
    for line in yaml_block.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)", line)
        if match:
            key = match.group(1)
            if key in seen_keys:
                log.warning("Duplicate frontmatter key '%s' — last value wins", key)
            seen_keys.add(key)
            value = match.group(2).strip()
            # Strip surrounding quotes
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            result[key] = value

    return result, body


# ---------------------------------------------------------------------------
# List value parser
# ---------------------------------------------------------------------------

def parse_list_value(raw: str) -> list[str]:
    """Parse a YAML-like list value: [a, b, c] or 'a'."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        items = []
        for item in inner.split(","):
            item = item.strip().strip("'\"")
            if item:
                items.append(item)
        return items
    return [raw.strip("'\"")]  if raw else []


# ---------------------------------------------------------------------------# Markdown table parser
# ---------------------------------------------------------------------------

_MD_TABLE_ROW = re.compile(r"^\|(.+)\|$")
_MD_SEPARATOR_ROW = re.compile(r"^\|[\s\-:|]+\|$")


def parse_markdown_table(text: str, *, skip_header: bool = True) -> list[list[str]]:
    """Extract data rows from a Markdown table.

    Args:
        text: Markdown text containing a table.
        skip_header: If True (default), skip the header row and separator.
                     If False, include all non-separator rows (caller filters).
    """
    rows: list[list[str]] = []
    header_seen = False
    for line in text.splitlines():
        line = line.strip()
        m = _MD_TABLE_ROW.match(line)
        if not m:
            continue
        if _MD_SEPARATOR_ROW.match(line):
            header_seen = True
            continue
        if skip_header and not header_seen:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if all(c == "" for c in cells):
            continue
        rows.append(cells)
    return rows


# ---------------------------------------------------------------------------# Data model
# ---------------------------------------------------------------------------

@dataclass
class AgentData:
    """Parsed agent data from a .agent.md file."""
    name: str = ""
    description: str = ""
    tools: list[str] = field(default_factory=list)
    agents: str = ""
    model: str = ""
    user_invocable: bool = True
    plugin: str = ""
    skills: list[str] = field(default_factory=list)
    body: str = ""
    source_file: str = ""


# ---------------------------------------------------------------------------
# File parser
# ---------------------------------------------------------------------------

def parse_agent_file(path: Path) -> AgentData | None:
    """Parse a .agent.md file into AgentData."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm, body = parse_frontmatter(text)
    if fm is None:
        return None

    return AgentData(
        name=fm.get("name", path.stem.replace(".agent", "")),
        description=fm.get("description", ""),
        tools=parse_list_value(fm.get("tools", "")),
        agents=fm.get("agents", ""),
        model=fm.get("model", ""),
        user_invocable=fm.get("user-invocable", "true").lower() != "false",
        plugin=fm.get("plugin", ""),
        skills=parse_list_value(fm.get("skills", "")),
        body=body.strip(),
        source_file=str(path),
    )


# ---------------------------------------------------------------------------
# Skill data model & parser
# ---------------------------------------------------------------------------

@dataclass
class SkillData:
    """Parsed skill data from a SKILL.md file."""
    name: str = ""
    description: str = ""
    argument_hint: str = ""
    user_invocable: bool = True
    disable_model_invocation: bool = False
    body: str = ""
    source_file: str = ""


def parse_skill_file(path: Path) -> SkillData | None:
    """Parse a SKILL.md file into SkillData."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    fm, body = parse_frontmatter(text)
    if fm is None:
        return None

    return SkillData(
        name=fm.get("name", path.parent.name),
        description=fm.get("description", ""),
        argument_hint=fm.get("argument-hint", ""),
        user_invocable=fm.get("user-invocable", "true").lower() != "false",
        disable_model_invocation=fm.get("disable-model-invocation", "false").lower() == "true",
        body=body.strip(),
        source_file=str(path),
    )
