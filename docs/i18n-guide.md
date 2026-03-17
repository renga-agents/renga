# Internationalization Guide (i18n)

> **Audience**: framework contributors, potential translators, and international teams
> **Prerequisite**: read [getting-started.md](getting-started.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 6 min

---

## Table of Contents

- [Why this guide](#why-this-guide)
- [Current language policy](#current-language-policy)
- [Bilingual convention](#bilingual-convention)
- [French-English glossary](#french-english-glossary)
- [i18n roadmap](#i18n-roadmap)
- [Contributing to translation](#contributing-to-translation)

---

## Why This Guide

The renga framework was initially written **entirely in French**. That matched the founding team, but it limited adoption by non-French-speaking developers.

Rather than attempting a massive and expensive translation effort all at once, this guide defines the foundations of a **progressive and controlled** internationalization strategy:

- Define which language to use and where
- Create a reference glossary to ensure consistent terminology
- Define a realistic 3-phase roadmap

---

## Current Language Policy

### Default language: English

| Content | Language | Rationale |
| --- | --- | --- |
| `.agent.md` files (body) | English | Core content now translated |
| YAML frontmatter (`name`, `tools`) | English | Technical identifiers, universal convention |
| Documentation (`docs/`) | English | Shared contributor language |
| Instructions (`.instructions.md`) | English | Core guidance language |
| Internal references (`_references/`) | English | Shared internal reference |
| File and directory names | English | Universal technical convention |
| Code comments (scripts) | English | International accessibility |
| Commit messages | English | Standard Git convention |
| Root README.md | English | Main entry point |

### General Rule

> ### If it is a technical identifier, file name, or code, use English.
>
> ### If it is narrative content, instructions, or documentation, also use English by default in this repository.

---

## Bilingual Convention

### Technical Terms: Always in English

Some technical terms do not have a useful French equivalent or are universally understood in English across the industry. They should **always** remain in English, even inside localized documents:

- **Workflow terms**: handoff, dispatch, dry-run, fast-track, commit, merge, push, pull request, review, rollback, deploy, worktree
- **Architecture terms**: DAG, endpoint, middleware, proxy, pipeline, webhook, API, SDK, CLI
- **AI/ML terms**: prompt, fine-tuning, embedding, RAG, LLM, token, few-shot, chain-of-thought
- **Tooling terms**: frontmatter, slug, linter, formatter, bundler, runtime

### Framework-Specific Terms: Keep a Documented English Equivalent

Framework-specific concepts such as lane, wave, or project lead must keep a **documented English equivalent** in the glossary below so translations remain consistent.

### Formatting in Text

```markdown

<!-- ✅ Correct: technical term kept in English -->
The orchestrator builds the DAG, then launches the dispatch in parallel waves.

<!-- ✅ Correct: first occurrence with an explicit equivalent -->
The technical lane groups development agents.

<!-- ❌ Incorrect: forced translation of a universal technical term -->
The orchestrator builds the directed acyclic graph, then launches the distribution.

<!-- ❌ Incorrect: arbitrary mixing without consistency -->
The project lead does the dispatch of tasks in the waves.

```

---

## French-English Glossary

> **Convention**: grouped by category, then alphabetically. Terms marked ★ are specific to the renga framework.

### Orchestration and Steering

| French | English | Notes |
| --- | --- | --- |
| Orchestrateur ★ | Orchestrator | Central steering agent — `orchestrator.agent.md` |
| Maître d'œuvre (MOE) ★ | Project lead / Orchestrator | Role of the orchestrator in the framework |
| Filière ★ | Lane | Functional grouping of agents, technical, product, data, governance |
| Vague ★ | Wave | Execution step in the DAG — group of agents dispatched in parallel |
| Dispatch ★ | Dispatch | Sending a task to a specialized agent |
| Délégation ★ | Delegation | Transfer of responsibility from the orchestrator to an agent |
| Boucle de contrôle ★ | Control loop | Cycle INITIALIZATION → DECOMPOSITION → PLANNING → DISPATCH → CONTROL → SYNTHESIS |
| Journalisation ★ | Logging / Journaling | Trace of decisions in `decisions-<slug>.md` |
| Scratchpad ★ | Scratchpad | Temporary working space for the orchestrator |
| Plan de fichiers ★ | File plan | List of paths + owner before parallel dispatch |

### Complexity and Classification

| Français | English | Notes |
| --- | --- | --- |
| Niveau de tâche ★ | Task level | L0 to L4 — complexity classification |
| Fast-track ★ | Fast-track | Direct execution without DAG, L0 tasks |
| Porte de passage ★ | Gate / Checkpoint | Mandatory condition before progressing |
| Seuil ★ | Threshold | Configurable limit in `.renga.yml` |
| Dérogation ★ | Waiver | Justified exception to a governance rule |
| Incident de gouvernance ★ | Governance incident | Violation of a steering rule |

### Agents and Roles

| Français | English | Notes |
| --- | --- | --- |
| Agent spécialisé | Specialized agent | Agent dedicated to a domain, backend, security, and so on |
| Sous-agent | Subagent | Agent invoked by another via `runSubagent` |
| Profil de filière ★ | Lane profile | Specialized orchestrator by lane, `orchestrator-tech`, etc. |
| Référentiel interne ★ | Internal reference | Non-invocable `.agent.md` file, `user-invocable: false` |
| Catalogue d'erreurs ★ | Error catalog | `_references/error-catalog.md` — rules ERR-001 to ERR-025 |

### Execution and Workflow

| Français | English | Notes |
| --- | --- | --- |
| DAG | DAG | Directed Acyclic Graph — task dependency graph |
| Worktree | Worktree | Isolated Git tree for parallel work |
| Handoff | Handoff | Structured transfer from one agent to another |
| Dry-run | Dry-run | Preview mode without execution |
| Lot de commit ★ | Commit batch | Grouping of changes by wave |
| Checkpoint ★ | Checkpoint | Intermediate control point, commit between waves |
| Critères d'acceptation | Acceptance criteria | Success conditions for a subtask |

### Security and Compliance

| Français | English | Notes |
| --- | --- | --- |
| Audit | Audit | Systematic review, security, code, compliance |
| Escalade | Escalation | Raising an issue to a higher level |
| Escalade HITL | HITL escalation | Human-In-The-Loop — human validation required |
| Garde-fou | Guardrail | Security constraint built into the prompt |
| Injection de prompt | Prompt injection | Attack that manipulates the behavior of an LLM |

### Documentation and Deliverables

| Français | English | Notes |
| --- | --- | --- |
| Aide-mémoire | Cheat sheet | `docs/cheat-sheet.md` |
| Guide de démarrage | Getting started | `docs/getting-started.md` |
| Format d'agent | Agent format | `docs/agent-format.md` |
| Profils de complexité | Complexity profiles | `docs/complexity-profiles.md` |
| Abstraction plateforme | Platform abstraction | `docs/platform-abstraction.md` |

---

## i18n Roadmap

### Phase 1 — Glossary and Conventions

> **Status**: completed foundation
> **Deliverable**: this document, [docs/i18n-guide.md](docs/i18n-guide.md)

**Goal**: define the terminology rules without destabilizing the repository.

- [x] Language policy documented
- [x] Bilingual convention defined
- [x] French-English glossary for 40+ key terms
- [ ] Validate the glossary with contributors
- [ ] Add the glossary to the documentation linter, optional

### Phase 2 — Translate Core Documents

> **Status**: completed in this repository
> **Scope**: core docs, instructions, and references

**Goal**: make the framework accessible to non-French-speaking users.

**Scope**:

1. Public documentation (`docs/*.md`) — full EN translation
2. Root README.md — bilingual FR/EN version
3. Cheat sheet — version EN
4. Most referenced `.instructions.md` files

**Approach**:

- Create a `docs/en/` directory for English versions
- Keep FR versions as the source of truth
- No automatic translation without human review

**Out of scope for Phase 2**:

- The 52 core `.agent.md` agents, too large, Phase 3
- Internal references in `_references/`

### Phase 3 — Full Locale System

> **Status**: future vision
> **Prerequisite**: stable demand for multi-locale maintenance

**Goal**: natively support multiple languages in the framework.

**Ideas under consideration**:

- `agents/en/`, `agents/fr/` structure with fallback
- `locale:` key in YAML frontmatter
- Cross-locale validation script, same structure, same frontmatter
- CI check: any FR agent modified must have an EN translation ticket

**Open questions**:

- Does an LLM understand a prompt better in its dominant training language, EN? → benchmark needed
- Should agent names be translated, `orchestrateur.agent.md` → `orchestrator.agent.md`? → risk of breaking references
- What is the impact on repository size? → evaluate duplicated content vs maintainability

---

## Contributing to Translation

### Rules for Translators

1. **Never translate the technical terms** listed in the bilingual convention
2. **Preserve the same Markdown structure**: headings, tables, and code fences
3. **Check anchors** because heading slugs change with the language
4. **Test internal links** because a link to a French anchor will not work in English
5. **Mark translations as draft** until reviewed by a native speaker when possible

### Contribution Process

```text

1. Choose an untranslated or outdated document in `docs/`
2. Create or update the English file with the same structure
3. Translate it using the rules above
4. Open a PR with the `i18n` label
5. Request review from a fluent English speaker when possible

```

### Terms That Must NOT Be Translated

> handoff, dispatch, dry-run, fast-track, commit, merge, push, pull request, review, rollback, deploy, worktree, DAG, endpoint, middleware, proxy, pipeline, webhook, API, SDK, CLI, prompt, fine-tuning, embedding, RAG, LLM, token, few-shot, chain-of-thought, frontmatter, slug, linter, formatter, bundler, runtime, scratchpad
