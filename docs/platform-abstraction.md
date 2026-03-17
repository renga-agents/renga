# Platform Abstraction Layer

> **Audience**: framework contributors and teams who want to port renga to another runtime
> **Prerequisite**: read [agent-format.md](agent-format.md)
> **Last updated**: 2026-03-17
> **Estimated reading time**: 15 min
>
> **Goal**: document renga's dependencies on GitHub Copilot and define the extension points required to port the framework to other AI runtimes.

---

## 1. Minimal Runtime Contract

A runtime compatible with the renga framework must support these 4 capabilities:

| # | Capability | Description | Required |
| --- | --- | --- | --- |
| C1 | **Agent format** | YAML frontmatter + Markdown body. The runtime loads the agent and respects the `name`, `description`, `tools`, and `model` fields | Yes |
| C2 | **Subagent delegation** | Invoke another agent by name with a text prompt and retrieve its response | Yes |
| C3 | **Basic tools** | File read/write, terminal execution, workspace search | Yes |
| C4 | **MCP (Model Context Protocol)** | Connect to external MCP servers such as context7 or chrome-devtools | No, fallback possible |

---

## 2. GitHub Copilot Dependency Inventory

### 2.1 Agent File Format

| Dependency | Detail | Coupling |
| --- | --- | --- |
| Location `.github/agents/*.agent.md` | Folder convention imposed by Copilot | **High** |
| YAML frontmatter between `---` | `name`, `description`, `tools`, `agents`, `model`, `user-invocable` fields | **High** |
| `tools` field with short names | `execute`, `read`, `edit`, `search`, `web/fetch`, `agent/runSubagent`, `todo` | **High** |
| `agents: ["*"]` field | Allows invoking all subagents | **High** |
| `model` field | Specific format `['Claude Opus 4.6 (copilot)']` | **Medium** |
| `user-invocable` field | Controls visibility in the mode selector | **Medium** |
| Free-form Markdown body | No format constraint beyond frontmatter | Low |

### 2.2 Inter-Agent Delegation

| Dependency | Detail | Coupling |
| --- | --- | --- |
| `agent/runSubagent` | Native Copilot tool to invoke a subagent by name | **High** |
| Text prompt transfer | The prompt is a free-form string sent to the subagent | Low |
| Synchronous response retrieval | The orchestrator waits for the response before continuing | **Medium** |
| No native shared context | Each subagent starts without history, so the prompt must be self-sufficient | **Medium** |

### 2.3 Native Tools

| Copilot tool | Use in the framework | Coupling |
| --- | --- | --- |
| `read_file` | Reading source files, memory, and config | **High** |
| `create_file` | Creating files | **High** |
| `replace_string_in_file` | Surgical file editing | **High** |
| `run_in_terminal` | Running shell commands such as git, build, and test | **High** |
| `semantic_search` | Semantic search in the workspace | **Medium** |
| `grep_search` | Text or regex search in the workspace | **Medium** |
| `file_search` | File search by glob | **Medium** |
| `list_dir` | Directory listing | Low |
| `get_errors` | Retrieving compile or lint errors | **Medium** |
| `manage_todo_list` | Task management in VS Code | Low |
| `fetch_webpage` | Fetching web content | Low |

### 2.4 MCP (Model Context Protocol)

| MCP server | Usage | Alternative without MCP |
| --- | --- | --- |
| `io.github.upstash/context7` | Up-to-date library documentation | Manual web search or `fetch_webpage` against the official docs |
| `io.github.chromedevtools/chrome-devtools-mcp` | Browser inspection, screenshots, performance traces | CLI commands such as Lighthouse CLI or Playwright |

---

## 3. Extension Points and Alternatives

### 3.1 Agent Format — Per-Platform Adaptation

The Markdown body content is **portable as-is**. Only the frontmatter requires adaptation:

| Copilot field | Universal meaning | Notes |
| --- | --- | --- |
| `name` | Unique agent identifier | Universal |
| `description` | Short description for dispatch | Universal |
| `tools` | List of allowed capabilities | Platform-specific mapping required |
| `agents` | Invokable agents | Specific to the delegation mechanism |
| `model` | Target LLM model | Configurable by platform |
| `user-invocable` | User visibility | UI-specific |

### 3.2 Delegation — Alternative Patterns

| Pattern | Description | Best fit when |
| --- | --- | --- |
| **Native** (Copilot `runSubagent`) | Direct invocation with isolated context | GitHub Copilot runtime |
| **Prompt chaining** | The orchestrator chains prompts in a single conversation | Runtime without native multi-agent support, Cursor or ChatGPT |
| **File convention** | The orchestrator writes a `.task.md` file and an external script dispatches it to the target agent | CI/CD automation |
| **Multi-turn API** | Sequential API calls with context passed explicitly | Custom backend, LangChain or CrewAI |

### 3.3 Tools — Universal Mapping

| Capability | Copilot | CLI alternative | API alternative |
| --- | --- | --- | --- |
| Read a file | `read_file` | `cat`, `head`, `tail` | `fs.readFile()` |
| Write a file | `create_file` | `echo > file`, `tee` | `fs.writeFile()` |
| Edit a file | `replace_string_in_file` | `sed`, `awk`, `patch` | Programmatic diff/patch |
| Terminal | `run_in_terminal` | Direct execution | `child_process.exec()` |
| Semantic search | `semantic_search` | `ripgrep` + fuzzy matching | Local embeddings |
| Text search | `grep_search` | `grep`, `rg` | Grep API |
| List files | `file_search`, `list_dir` | `find`, `fd`, `ls` | `fs.readdir()` |
| Compile errors | `get_errors` | Build stderr output | Parse build output |
| Web fetch | `fetch_webpage` | `curl`, `wget` | `fetch()`, `axios` |

---

## 4. Platform Mapping Table

> State as of 2026-03. Runtimes evolve quickly, so check the official docs before porting.

| Capability | GitHub Copilot (VS Code) | Cursor | Cline | Windsurf |
| --- | --- | --- | --- | --- |
| **Agent format** | `.github/agents/*.agent.md` (YAML frontmatter) | `.cursor/rules/*.mdc` (YAML frontmatter, MDC format) | Single `.clinerules` file or `.clinerules/*.md` | Single `.windsurfrules` file |
| **Location** | `.github/agents/` | `.cursor/rules/` | Project root | Project root |
| **Frontmatter** | `name`, `tools`, `agents`, `model`, `description` | `description`, `globs`, `alwaysApply` | N/A (texte libre) | N/A (texte libre) |
| **Multi-agent** | Yes, native `runSubagent` | Not native, manual prompt chaining | Not native, prompt chaining | Not native, prompt chaining |
| **Agent selection** | `@name` in chat or automatic mode | Rules applied by glob and matching | Single file read on every request | Single file read on every request |
| **File tools** | `read_file`, `create_file`, `replace_string_in_file` | Similar built-in tools | `read_file`, `write_to_file`, `replace_in_file` | Similar built-in tools |
| **Terminal** | `run_in_terminal` | `run_terminal_command` | `execute_command` | Integrated terminal |
| **Search** | `semantic_search`, `grep_search`, `file_search` | Built-in search | `search_files`, `list_files` | Built-in search |
| **MCP** | Yes, through `settings.json` | Yes, through `mcp.json` | Yes, through `cline_mcp_settings.json` | Yes, native configuration |
| **Model configurable** | Yes, `model` field in frontmatter | Yes, UI selector | Yes, UI selector + API key | Yes, UI selector |

---

## 5. Porting Guide

### 5.1 Porting to Cursor

1. **Convert the frontmatter**: rename `name` to the rule identifier, add `globs` if applicable, and `alwaysApply` if the rule must apply everywhere
2. **Merge agents**: Cursor does not support native multi-agent orchestration, so merge critical instructions into a hierarchy of rules
3. **Adapt tools**: tool names are similar but not identical, check the Cursor documentation
4. **Delegation**: replace `runSubagent` with explicit prompt instructions, such as "apply the rules of X"
5. **MCP**: configure it in `.cursor/mcp.json`, same protocol, different config format

### 5.2 Porting to Cline

1. **Format**: convert each agent into a section in `.clinerules` or separate `.md` files inside `.clinerules/`
2. **No frontmatter**: move tool constraints into the text body
3. **Delegation**: not supported natively, use explicit prompt-based mode switching
4. **Tools**: direct mapping, for example `read_file` → `read_file`, `replace_string_in_file` → `replace_in_file`
5. **MCP**: configure it in `cline_mcp_settings.json`

### 5.3 Porting to Windsurf

1. **Format**: concatenate critical instructions into `.windsurfrules`
2. **No multi-agent support**: `.windsurfrules` is a single system prompt file
3. **Strategy**: extract shared rules such as engineering principles, security, and conventions, then merge them
4. **Size**: watch the file-size limit, prioritize the highest-impact rules

### 5.4 Porting to a Custom Framework (LangChain, CrewAI, AutoGen)

1. **Parse** the YAML frontmatter to extract metadata
2. **Use** the Markdown body as the system prompt for each agent
3. **Map** `tools` to the framework's tool system, such as LangChain Tools or CrewAI Tools
4. **Implement** delegation through the framework's native mechanism, such as CrewAI Crew or AutoGen GroupChat
5. **Conversion script**: a YAML + Markdown parser is sufficient, the schema lives in `schemas/agent.schema.json`

---

## 6. Decision Diagram

```text

Does the project use GitHub Copilot?
├─ Yes → Use the framework as-is
└─ No → Identify the target runtime
         ├─ Cursor       → §5.1 — Convert to .mdc rules
         ├─ Cline        → §5.2 — Convert to .clinerules
         ├─ Windsurf     → §5.3 — Merge into .windsurfrules
         └─ Custom/API   → §5.4 — Parser + orchestration framework

```

---

## 7. Known Limitations

| Limitation | Impact | Mitigation |
| --- | --- | --- |
| No native multi-agent support outside Copilot | Multi-agent orchestration degrades to prompt chaining | Document delegation prompts as reusable templates |
| Context window varies by runtime | A 500-line agent can exceed some runtimes' limits | Target < 300 lines per agent and externalize content to `_references/` |
| Tool names are not standardized | Each platform exposes different tool names | Keep table §4 up to date |
| MCP is not yet universal | Some runtimes do not implement MCP | Always document a CLI fallback |
| Configuration format is not portable | `.renga.yml` is only read by the Copilot orchestrator | The file remains human-readable and can be adapted manually |
