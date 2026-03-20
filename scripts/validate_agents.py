#!/usr/bin/env python3
"""Validate .agent.md files in the renga framework.

Scans all .agent.md files under .github/agents/ (recursively) and validates:
- YAML frontmatter presence and structure (--- delimited)
- Required fields: name, description
- Optional known fields: model, tools, mode, user-invocable, agents
- Warns on unknown frontmatter fields
- Markdown content: presence of identity section and collaboration/handoff section
- Cross-references: agents mentioned in collaboration sections exist as files

Usage:
    python3 scripts/validate_agents.py [--agents-dir PATH]

Exit codes:
    0 — all agents valid
    1 — warnings only (missing optional fields, unknown fields)
    2 — errors (missing frontmatter, missing required fields, invalid YAML)
"""

from __future__ import annotations

import argparse
import re
import sys
import logging
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

from agent_parser import parse_frontmatter, parse_list_value, parse_skill_file

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: set[str] = {"name", "description"}
KNOWN_OPTIONAL_FIELDS: set[str] = {
    "model", "tools", "mode", "user-invocable", "agents",
    "filiere", "plugin", "overrides", "framework_version",
    "skills",
}
KNOWN_FIELDS: set[str] = REQUIRED_FIELDS | KNOWN_OPTIONAL_FIELDS

# Pattern for filiere auto-discovery from orchestrator profile filenames.
FILIERE_FILENAME_PATTERN = re.compile(r"^orchestrator-(.+)\.agent\.md$")

IDENTITY_PATTERN = re.compile(
    r"^##\s+(Identité|Identity|Identité & Posture|Identity & Posture)",
    re.MULTILINE | re.IGNORECASE,
)
MAIN_TITLE_PATTERN = re.compile(r"^#\s+", re.MULTILINE)

COLLAB_PATTERN = re.compile(
    r"^##\s+.*(ollaboration|andoff|Handoff|Collaboration|Contrat de handoff)",
    re.MULTILINE | re.IGNORECASE,
)
COLLAB_INLINE_PATTERN = re.compile(
    r"^\*\*Collaboration\*\*\s*:", re.MULTILINE
)


class Severity(IntEnum):
    OK = 0
    WARNING = 1
    ERROR = 2


@dataclass
class ValidationResult:
    filename: str
    severity: Severity = Severity.OK
    messages: list[str] = field(default_factory=list)

    def warn(self, msg: str) -> None:
        self.messages.append(f"⚠️  {msg}")
        if self.severity < Severity.WARNING:
            self.severity = Severity.WARNING

    def error(self, msg: str) -> None:
        self.messages.append(f"❌ {msg}")
        self.severity = Severity.ERROR


# ---------------------------------------------------------------------------
# Cross-reference extraction
# ---------------------------------------------------------------------------

def _pascal_to_kebab(name: str) -> str:
    """Convert PascalCase to kebab-case, handling acronyms.

    Examples:
        QAEngineer -> qa-engineer
        APIDesigner -> api-designer
        BackendDev -> backend-dev
        MLOpsEngineer -> ml-ops-engineer
        AIEthicsGovernance -> ai-ethics-governance
    """
    # Step 1: insert dash between a lowercase/digit and an uppercase letter
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    # Step 2: insert dash between uppercase acronym and uppercase+lowercase
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    return s.lower()


def _extract_collab_handoff_sections(body: str) -> str:
    """Extract only the collaboration/handoff-relevant portions of the body."""
    sections: list[str] = []

    # Inline collaboration line: **Collaboration** : ...
    collab_match = re.search(
        r"\*\*Collaboration\*\*\s*:\s*(.+?)(?:\n\n|\n##|\n---|\Z)",
        body,
        re.DOTALL,
    )
    if collab_match:
        sections.append(collab_match.group(1))

    # ## Contrat de handoff / ## Handoff sections
    # First find headings (single-line match), then grab content until next heading
    heading_pattern = re.compile(
        r"^(##\s+[^\n]*(?:andoff|ollaboration)[^\n]*)\n",
        re.MULTILINE | re.IGNORECASE,
    )
    next_heading = re.compile(r"^##\s+", re.MULTILINE)

    for hm in heading_pattern.finditer(body):
        content_start = hm.end()
        nh = next_heading.search(body, content_start)
        content_end = nh.start() if nh else len(body)
        sections.append(body[content_start:content_end])

    return "\n".join(sections) if sections else ""


def extract_mentioned_agents(body: str) -> set[str]:
    """Extract agent names mentioned in collaboration/handoff sections.

    Only scans collaboration and handoff sections to avoid false positives
    from technology names, tool names, etc.
    """
    mentioned: set[str] = set()
    collab_text = _extract_collab_handoff_sections(body)

    if not collab_text:
        return mentioned

    # Pattern 1: PascalCase names (e.g. "BackendDev", "SecurityEngineer")
    # Require at least 6 chars to filter out plural acronyms like "APIs", "DTOs"
    pascal_names = re.findall(r"\b([A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)+)\b", collab_text)
    for name in pascal_names:
        if len(name) < 6:
            continue
        kebab = _pascal_to_kebab(name)
        mentioned.add(kebab)

    # Pattern 2: @agent-name mentions in collaboration/handoff sections only
    at_mentions = re.findall(r"@([a-z][a-z0-9-]+)", collab_text)
    mentioned.update(at_mentions)

    # Pattern 3: backtick-quoted kebab-case names in collaboration/handoff sections
    # Require a dash and each segment at least 2 chars (filters "a-b" style noise)
    backtick_matches = re.findall(r"`([a-z][a-z0-9-]+(?:-[a-z0-9]+)*)`", collab_text)
    for name in backtick_matches:
        if "-" not in name:
            continue
        segments = name.split("-")
        if all(len(s) >= 2 for s in segments) and len(segments) >= 2:
            mentioned.add(name)

    return mentioned


# ---------------------------------------------------------------------------
# Single file validation
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Filière auto-discovery
# ---------------------------------------------------------------------------

def discover_filieres(agents_dir: Path) -> set[str]:
    """Discover valid filières from orchestrator-*.agent.md files.

    Convention: each file matching orchestrator-<name>.agent.md defines
    a filière whose identifier is <name>.
    Example: orchestrator-tech.agent.md → filière "tech".
    """
    filieres: set[str] = set()
    for path in sorted(agents_dir.glob("orchestrator-*.agent.md")):
        m = FILIERE_FILENAME_PATTERN.match(path.name)
        if m:
            filieres.add(m.group(1))
    return filieres


# ---------------------------------------------------------------------------
# Single file validation
# ---------------------------------------------------------------------------

def validate_agent_file(
    filepath: Path,
    known_agent_names: set[str],
    known_filieres: set[str] | None = None,
) -> ValidationResult:
    """Validate a single .agent.md file."""
    result = ValidationResult(filename=filepath.name)

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        result.error(f"Cannot read file: {exc}")
        return result

    # --- Frontmatter ---
    frontmatter, body = parse_frontmatter(text)

    if frontmatter is None:
        result.error("Invalid or missing YAML frontmatter (no --- delimiters)")
        return result

    if not frontmatter:
        result.error("YAML frontmatter is empty")
        return result

    # Required fields
    for req in sorted(REQUIRED_FIELDS):
        if req not in frontmatter:
            result.error(f"Missing required field: {req}")
        elif not frontmatter[req].strip():
            result.error(f"Required field '{req}' is empty")

    # Unknown fields
    unknown = set(frontmatter.keys()) - KNOWN_FIELDS
    if unknown:
        result.warn(f"Unknown frontmatter fields: {', '.join(sorted(unknown))}")

    # Missing optional fields — warn for commonly expected fields
    missing_optional = KNOWN_OPTIONAL_FIELDS - set(frontmatter.keys())
    for recommended in ("tools", "model"):
        if recommended in missing_optional:
            result.warn(f"Missing recommended field: {recommended}")

    # --- Filière validation (auto-discovered) ---
    filiere_value = frontmatter.get("filiere", "").strip()
    if filiere_value and known_filieres is not None:
        if filiere_value not in known_filieres:
            result.warn(
                f"Filière '{filiere_value}' has no matching "
                f"orchestrator-{filiere_value}.agent.md profile. "
                f"Known filières: {', '.join(sorted(known_filieres))}"
            )

    # --- Markdown structure ---
    has_identity = bool(IDENTITY_PATTERN.search(body))
    has_main_title = bool(MAIN_TITLE_PATTERN.search(body))

    if not has_identity and not has_main_title:
        result.warn("Missing identity section (## Identité / ## Identity) and main title (# ...)")
    elif not has_identity:
        # Some reference docs may only have a main title — that's acceptable
        pass

    # Non-invocable agents (reference docs, filière orchestrator profiles, meta-protocols)
    # don't require collaboration contracts — they are read by seiji, not dispatched.
    # This covers: orchestrator-{tech,data,product,governance}.
    # user-invocable may be parsed as string 'false' or bool False from YAML.
    _inv = frontmatter.get("user-invocable", True)
    is_invocable = str(_inv).lower() != "false"
    if is_invocable:
        has_collab = bool(COLLAB_PATTERN.search(body)) or bool(COLLAB_INLINE_PATTERN.search(body))
        if not has_collab:
            result.warn("Missing collaboration/handoff section")

    # --- Cross-references ---
    mentioned = extract_mentioned_agents(body)
    agent_name = frontmatter.get("name", "")

    # Build a normalized lookup (without dashes) for fuzzy matching
    # Handles devops-engineer vs dev-ops-engineer, mlops vs ml-ops, etc.
    normalized_known = {n.replace("-", ""): n for n in known_agent_names}

    # Non-agent patterns to ignore (tools, technologies, CSS, HTML attrs, game terms, etc.)
    false_positive_prefixes = {
        "context7", "chrome-devtools", "devtools-mcp", "io-github",
        "get-library", "resolve-library", "library-docs", "library-id",
        "prefers-reduced-motion", "data-testid", "blocking", "non-blocking",
    }

    for ref in sorted(mentioned):
        # Skip self-references
        if ref == agent_name:
            continue
        # Skip known non-agent patterns
        if any(ref.startswith(p) or ref == p for p in false_positive_prefixes):
            continue
        # Single-word refs (no dash) must be long enough to be plausible agent names
        if "-" not in ref and len(ref) < 8:
            continue
        if len(ref) < 4:
            continue

        # Direct match
        if ref in known_agent_names:
            continue
        # Normalized match (handles dash variations)
        ref_normalized = ref.replace("-", "")
        if ref_normalized in normalized_known:
            continue

        result.warn(f"Referenced agent '{ref}' not found as .agent.md file")

    return result


# ---------------------------------------------------------------------------
# Plugin tools validation
# ---------------------------------------------------------------------------

def _parse_tools_list(raw: str) -> set[str]:
    """Parse a tools field value into a set (delegates to parse_list_value)."""
    return set(parse_list_value(raw))


def validate_plugin_tools(agents_dir: Path) -> list[ValidationResult]:
    """Validate that plugin agent tools are a subset of core agent tools.

    Core agents are those directly under agents_dir (not in _plugins/).
    Plugin agents are those under agents_dir/_plugins/**.

    Returns a list of ValidationResult for each plugin with violations.
    """
    results: list[ValidationResult] = []

    plugins_dir = agents_dir / "_plugins"
    if not plugins_dir.is_dir():
        return results

    # Tools that are valid for plugins even if not used by any core agent
    # (external APIs and platform-specific integrations)
    PLUGIN_TOOL_ALLOWLIST: set[str] = {"replicate/*"}

    # Collect the union of all tools declared by core agents
    core_tools: set[str] = set()
    for core_file in sorted(agents_dir.glob("*.agent.md")):
        try:
            text = core_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, _ = parse_frontmatter(text)
        if fm and "tools" in fm:
            core_tools |= _parse_tools_list(fm["tools"])

    if not core_tools:
        log.warning("No tools found in core agents — plugin tools validation skipped")
        return results

    # Check each plugin agent
    plugin_files = sorted(plugins_dir.rglob("*.agent.md"))
    for plugin_file in plugin_files:
        fm_text = plugin_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(fm_text)
        if not fm or "tools" not in fm:
            continue

        plugin_tools = _parse_tools_list(fm["tools"])
        unauthorized = plugin_tools - core_tools - PLUGIN_TOOL_ALLOWLIST
        if unauthorized:
            result = ValidationResult(filename=str(plugin_file.relative_to(agents_dir)))
            result.warn(
                f"Plugin declares tools not in core agent pool: "
                f"{', '.join(sorted(unauthorized))}"
            )
            results.append(result)

    return results


# ---------------------------------------------------------------------------
# Skill validation
# ---------------------------------------------------------------------------

SKILL_REQUIRED_FIELDS: set[str] = {"name", "description"}
SKILL_KNOWN_FIELDS: set[str] = {
    "name", "description", "argument-hint", "user-invocable",
    "disable-model-invocation",
}


def validate_skill_file(filepath: Path) -> ValidationResult:
    """Validate a single SKILL.md file."""
    skill_name = filepath.parent.name
    result = ValidationResult(filename=f"skills/{skill_name}/SKILL.md")

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        result.error(f"Cannot read file: {exc}")
        return result

    frontmatter, body = parse_frontmatter(text)

    if frontmatter is None:
        result.error("Invalid or missing YAML frontmatter (no --- delimiters)")
        return result

    if not frontmatter:
        result.error("YAML frontmatter is empty")
        return result

    # Required fields
    for req in sorted(SKILL_REQUIRED_FIELDS):
        if req not in frontmatter:
            result.error(f"Missing required field: {req}")
        elif not frontmatter[req].strip():
            result.error(f"Required field '{req}' is empty")

    # name must match directory name
    fm_name = frontmatter.get("name", "").strip()
    if fm_name and fm_name != skill_name:
        result.error(
            f"Skill name '{fm_name}' does not match directory name '{skill_name}'"
        )

    # Schema constraints on name
    if fm_name:
        if not re.match(r'^[a-z][a-z0-9-]*$', fm_name):
            result.error(
                f"Skill name '{fm_name}' does not match pattern ^[a-z][a-z0-9-]*$"
            )
        if len(fm_name) > 64:
            result.error(
                f"Skill name exceeds 64 characters ({len(fm_name)})"
            )

    # Schema constraints on description
    desc = frontmatter.get("description", "").strip()
    if desc:
        if len(desc) < 10:
            result.warn(
                f"Description is very short ({len(desc)} chars, minimum recommended: 10)"
            )
        if len(desc) > 1024:
            result.error(
                f"Description exceeds 1024 characters ({len(desc)})"
            )

    # Schema constraints on argument-hint
    hint = frontmatter.get("argument-hint", "").strip()
    if hint and len(hint) > 200:
        result.warn(
            f"argument-hint exceeds 200 characters ({len(hint)})"
        )

    # Unknown fields
    unknown = set(frontmatter.keys()) - SKILL_KNOWN_FIELDS
    if unknown:
        result.warn(f"Unknown frontmatter fields: {', '.join(sorted(unknown))}")

    # Body must not be empty
    if not body or not body.strip():
        result.warn("SKILL.md body is empty — add instructions for the skill")

    return result


def validate_skill_references(
    agents_dir: Path,
    known_skill_names: set[str],
) -> list[ValidationResult]:
    """Cross-validate that agent skill references point to existing skills."""
    results: list[ValidationResult] = []

    # Scan root-level agents and plugin agents
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    plugin_dir = agents_dir / "_plugins"
    if plugin_dir.is_dir():
        agent_files.extend(sorted(plugin_dir.rglob("*.agent.md")))

    for agent_file in agent_files:
        fm_text = agent_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(fm_text)
        if not fm or "skills" not in fm:
            continue

        skills_list = parse_list_value(fm["skills"])
        for skill in skills_list:
            if skill not in known_skill_names:
                rel_name = agent_file.relative_to(agents_dir).as_posix()
                result = ValidationResult(filename=rel_name)
                result.warn(
                    f"Referenced skill '{skill}' not found in .github/skills/"
                )
                results.append(result)

    return results


# ---------------------------------------------------------------------------
# Config waiver validation
# ---------------------------------------------------------------------------

def validate_config_waivers(root_dir: Path) -> list[ValidationResult]:
    """Validate waivers in .renga.yml configuration file."""
    results: list[ValidationResult] = []
    config_path = root_dir / ".renga.yml"
    if not config_path.exists():
        config_path = root_dir / ".renga.example.yml"
    if not config_path.exists():
        log.info("No .renga.yml or .renga.example.yml found — waiver validation skipped")
        return results

    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        log.info("PyYAML not installed — waiver validation skipped (pip install pyyaml)")
        return results

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("⚠️  Cannot parse %s: %s", config_path.name, exc)
        return results

    if not isinstance(config, dict):
        return results

    waivers = config.get("waivers")
    if not waivers or not isinstance(waivers, list):
        return results

    from datetime import date, timedelta  # noqa: PLC0415

    today = date.today()
    max_future = today + timedelta(days=365)

    log.info("Validating %d waiver(s) from %s…", len(waivers), config_path.name)

    for i, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            log.warning("⚠️  Waiver #%d: not a valid mapping", i + 1)
            continue

        label = waiver.get("rule", f"#{i + 1}")

        rule = waiver.get("rule", "")
        if not rule or not str(rule).strip():
            log.warning("⚠️  Waiver #%d: missing or empty 'rule'", i + 1)

        reason = waiver.get("reason", "")
        if not reason or not str(reason).strip():
            log.warning("⚠️  Waiver '%s': missing or empty 'reason'", label)

        expires_raw = waiver.get("expires", "")
        if expires_raw:
            try:
                expires = date.fromisoformat(str(expires_raw))
                if expires < today:
                    log.warning("⚠️  Waiver '%s': expired on %s", label, expires)
                elif expires > max_future:
                    log.warning(
                        "⚠️  Waiver '%s': expires too far in future (%s, max 1 year)",
                        label, expires,
                    )
            except ValueError:
                log.warning(
                    "⚠️  Waiver '%s': 'expires' is not a valid ISO date: %s",
                    label, expires_raw,
                )
        else:
            log.warning("⚠️  Waiver '%s': missing 'expires' field", label)

        approved_by = waiver.get("approved_by", "")
        if not approved_by or not str(approved_by).strip():
            log.warning("⚠️  Waiver '%s': missing or empty 'approved_by'", label)

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(agents_dir: Path | None = None) -> int:
    """Run validation on all .agent.md files.

    Args:
        agents_dir: Path to the agents directory. Defaults to .github/agents/
                    relative to the script's parent's parent.

    Returns:
        Exit code: 0 (OK), 1 (warnings), 2 (errors).
    """
    if agents_dir is None:
        # Resolve relative to the repo root (script is in scripts/)
        repo_root = Path(__file__).resolve().parent.parent
        agents_dir = repo_root / ".github" / "agents"
    else:
        # Derive repo root from the provided agents dir (.github/agents -> project root)
        repo_root = agents_dir.resolve().parent.parent

    if not agents_dir.is_dir():
        log.error("❌ Agents directory not found: %s", agents_dir)
        return 2

    agent_files = sorted(agents_dir.rglob("*.agent.md"))

    if not agent_files:
        log.error("❌ No .agent.md files found in %s", agents_dir)
        return 2

    # Build index of known agent names (from filenames)
    known_agent_names: set[str] = set()
    for f in agent_files:
        # e.g. backend-dev.agent.md -> backend-dev
        stem = f.name.removesuffix(".agent.md")
        known_agent_names.add(stem)

    # Auto-discover valid filières from orchestrator-*.agent.md files
    known_filieres = discover_filieres(agents_dir)
    if known_filieres:
        log.info(
            "Discovered filières: %s",
            ", ".join(sorted(known_filieres)),
        )
    else:
        log.warning("No orchestrator-*.agent.md files found — filière validation skipped")

    # Validate each file
    results: list[ValidationResult] = []
    for filepath in agent_files:
        result = validate_agent_file(filepath, known_agent_names, known_filieres)
        results.append(result)

    # Output
    ok_count = 0
    warn_count = 0
    error_count = 0

    for r in results:
        match r.severity:
            case Severity.OK:
                ok_count += 1
                log.info("✅ %s — OK", r.filename)
            case Severity.WARNING:
                warn_count += 1
                log.warning("⚠️  %s — Warnings:", r.filename)
                for msg in r.messages:
                    log.warning("   %s", msg)
            case Severity.ERROR:
                error_count += 1
                log.error("❌ %s — ERRORS:", r.filename)
                for msg in r.messages:
                    log.error("   %s", msg)

    # --- Plugin tools validation ---
    plugin_results = validate_plugin_tools(agents_dir)
    for r in plugin_results:
        match r.severity:
            case Severity.WARNING:
                warn_count += 1
                log.warning("⚠️  %s — Warnings:", r.filename)
                for msg in r.messages:
                    log.warning("   %s", msg)
            case Severity.ERROR:
                error_count += 1
                log.error("❌ %s — ERRORS:", r.filename)
                for msg in r.messages:
                    log.error("   %s", msg)
    results.extend(plugin_results)

    # --- Skill validation ---
    skills_dir = repo_root / ".github" / "skills"
    if skills_dir.is_dir():
        skill_files = sorted(skills_dir.rglob("SKILL.md"))
        known_skill_names: set[str] = set()
        for sf in skill_files:
            # Skip _local/ skills
            if "_local" in sf.parts:
                continue
            known_skill_names.add(sf.parent.name)

        for sf in skill_files:
            if "_local" in sf.parts:
                continue
            sr = validate_skill_file(sf)
            match sr.severity:
                case Severity.OK:
                    ok_count += 1
                    log.info("✅ %s — OK", sr.filename)
                case Severity.WARNING:
                    warn_count += 1
                    log.warning("⚠️  %s — Warnings:", sr.filename)
                    for msg in sr.messages:
                        log.warning("   %s", msg)
                case Severity.ERROR:
                    error_count += 1
                    log.error("❌ %s — ERRORS:", sr.filename)
                    for msg in sr.messages:
                        log.error("   %s", msg)
            results.append(sr)

        # Cross-ref: agent skills → existing skills
        skill_ref_results = validate_skill_references(agents_dir, known_skill_names)
        for r in skill_ref_results:
            warn_count += 1
            log.warning("⚠️  %s — Warnings:", r.filename)
            for msg in r.messages:
                log.warning("   %s", msg)
        results.extend(skill_ref_results)

    # --- Waiver validation ---
    waiver_results = validate_config_waivers(repo_root)
    results.extend(waiver_results)

    total = len(results)
    log.info("")
    log.info(
        "Summary: %d agents checked, %d OK, %d warnings, %d errors",
        total,
        ok_count,
        warn_count,
        error_count,
    )

    if error_count > 0:
        return 2
    if warn_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate .agent.md files")
    parser.add_argument("--agents-dir", type=Path, default=None, help="Path to agents directory")
    args = parser.parse_args()
    sys.exit(main(args.agents_dir))
