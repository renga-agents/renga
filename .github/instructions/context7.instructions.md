---
description: "context7 MCP usage convention — verify library versions before using any framework API"
applyTo: "**/*.ts,**/*.tsx,**/*.py,**/*.js,**/*.jsx"
---
# context7 Usage Convention

Before using any framework, library, or tool API, verify the current version and API surface via the context7 MCP tool. Never assume versions or APIs from training data — they may be outdated.

Use `resolve-library-id` first, then `get-library-docs` with a focused topic.
