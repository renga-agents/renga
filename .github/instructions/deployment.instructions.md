---
description: "Use when deploying, debugging production issues, modifying Docker/Ansible config, or troubleshooting VPS. Covers the full deployment pipeline, SSH access, and common pitfalls."
---
# Deployment & Infrastructure Guidelines

## Deployment Pipeline

Push code → GitHub Actions → SSH to VPS → git pull → docker compose build → up

### Deploy Commands

Project-specific deploy commands (repos, branches, paths) are defined in `.github/instructions/project/`.

For manual deploy and Ansible commands, see `.copilot/memory/vps-access.md`.

## VPS Access

SSH details and debug commands are stored in `.copilot/memory/vps-access.md`.

## Critical Reminders

1. **Strapi extensions**: Must be copied from `src/` to `dist/` in Dockerfile
2. **Branch mapping**: Check project-specific instructions for the correct deployment branch
3. **GitHub SSH key**: Add SSH key before pushing (see `.copilot/memory/vps-access.md`)
4. **Env vars on VPS**: Managed by Ansible template — check project-specific paths
5. **Reverse proxy**: Configuration managed by Ansible — check project-specific paths
