# IDE Setup — renga

> **Target audience**: developers preparing their editor before using renga
> **Prerequisites**: VS Code installed, access to GitHub Copilot
> **Last updated**: 2026-03-17
> **Estimated reading time**: 8 min

---

## Table of Contents

- [Why This Page Exists](#why-this-page-exists)
- [Minimum Setup](#minimum-setup)
- [Optional MCP Servers](#optional-mcp-servers)
- [VS Code MCP Example](#vs-code-mcp-example)
- [What Happens If a Tool Is Missing?](#what-happens-if-a-tool-is-missing)

---

## Why This Page Exists

The quickstart should stay short. This page covers the editor and tool setup that is useful before deeper adoption.

If you only want to try renga on a first task, go back to [getting-started.md](getting-started.md).

---

## Minimum Setup

You only need three things to start:

1. VS Code.
2. The GitHub Copilot extension, enabled in agent mode.
3. The repository opened locally as a workspace.

That is enough to use the Lite profile and call agents directly in chat.

---

## Optional MCP Servers

renga can use MCP servers (Model Context Protocol) to access external tools such as documentation lookup, browser automation, SQL diagnostics, or GitHub data.

> [!IMPORTANT]
> MCP servers are optional. Install only the ones required by the agents you activate in `.renga.yml`.

### Which MCP servers matter first?

| MCP server | `tools:` identifier | Purpose | Main agents |
| --- | --- | --- | --- |
| context7 | `io.github.upstash/context7/*` | Up-to-date framework and library documentation | Most technical agents |
| chrome-devtools | `io.github.chromedevtools/chrome-devtools-mcp/*` | DOM inspection, network debugging, performance and accessibility checks | Most technical agents |
| playwright | `playwright/*` | Browser automation, E2E tests, screenshots, UI verification | frontend-dev, qa-engineer, security-engineer, accessibility-engineer |
| postgresql | project-specific | Read-only SQL execution, schema checks, query diagnostics | database-engineer, backend-dev, data-engineer |
| github | project-specific | Pull requests, issues, commit history, repository metadata | git-expert, code-reviewer, debugger, tech-writer |

---

## VS Code MCP Example

Declare MCP servers in `.vscode/mcp.json`:

```json

{
  "servers": {
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/chrome-devtools-mcp@latest"]
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/playwright-mcp@latest"]
    },
    "postgresql": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/postgresql-mcp@latest"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/mydb"
      }
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/github-mcp@latest"],
      "env": {
        "GITHUB_TOKEN": "${input:githubToken}"
      }
    }
  }
}

```

> [!TIP]
> Do not commit secrets in `.vscode/mcp.json`. Use environment variables or VS Code inputs.

### Official references

| MCP server | Documentation |
| --- | --- |
| context7 | [github.com/upstash/context7](https://github.com/upstash/context7) |
| chrome-devtools | [github.com/anthropics/chrome-devtools-mcp](https://github.com/anthropics/chrome-devtools-mcp) |
| playwright | [github.com/anthropics/playwright-mcp](https://github.com/anthropics/playwright-mcp) |
| postgresql | [github.com/anthropics/postgresql-mcp](https://github.com/anthropics/postgresql-mcp) |
| github | [github.com/anthropics/github-mcp](https://github.com/anthropics/github-mcp) |

---

## What Happens If a Tool Is Missing?

The agent still works. It simply loses access to that tool.

Examples:

- `@database-engineer` can still read SQL files without a PostgreSQL MCP server, but cannot run a live `EXPLAIN ANALYZE`.
- `@frontend-dev` can still edit components without Playwright, but cannot validate the UI in a browser.
- `@tech-writer` can still write docs without GitHub MCP, but cannot inspect pull requests or issues directly.
