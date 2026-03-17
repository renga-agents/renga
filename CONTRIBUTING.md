# Contributing to renga

Thanks for contributing. Keep changes focused, easy to review, and aligned with the project's existing conventions.

## Quick Start

1. Fork the repository.
2. Pick an issue or open one before starting larger work.
3. Make one logical change per branch.
4. Run validation locally.
5. Open a pull request that explains why the change matters.

## Types of Contributions

| Contribution | Difficulty | Typical Time |
| --- | --- | --- |
| Bug reports | Easy | 5 minutes |
| Documentation fixes | Easy | 15 minutes |
| Translation work | Easy | 30-60 minutes |
| Custom agent plugins | Medium | 1-3 hours |
| Platform ports | Medium | 1-2 hours |
| Tutorials and guides | Medium | 2-4 hours |
| CLI or script improvements | Medium | 2-4 hours |
| New core agents | Advanced | 1-2 days |
| Core framework changes | Advanced | 2-5 days |

## Development Environment Setup

1. Fork and clone your fork.
1. Open the repository in VS Code.
1. Run the test suite:

```bash

python3 -m pytest tests/

```

1. Validate agents and related metadata:

```bash

python3 scripts/validate_agents.py

```

No additional runtime services are required for local development.

## Translation Work

Use [docs/i18n-guide.md](docs/i18n-guide.md) as the glossary source of truth.
Prefer small PRs for translation work. One file or one coherent batch per PR is ideal.

## Creating a Custom Agent Plugin

Plugin work should start from the conventions documented in [docs/plugin-system.md](docs/plugin-system.md).
Keep plugins narrowly scoped, reusable, and easy to validate.

## Pull Request Guidelines

- One logical change per PR.
- Keep diffs small when possible.
- Use commit prefixes such as `feat:`, `fix:`, `docs:`, or `chore:`.
- Make sure all CI checks pass before requesting review.
- Explain why the change is needed, not only what changed.
- If a change affects user-facing behavior, update the relevant documentation in the same PR.

## Review Process

- CI runs automatically on pull requests.
- The maintainer reviews PRs on a best-effort basis, usually within 72 hours.
- Plugin and documentation contributions usually have a lighter review path.
- Core changes, validation changes, and schema changes receive a stricter review.
- Large or breaking changes may be redirected to a GitHub Discussion or RFC first.

## Reporting Bugs and Proposing Features

If you found a bug, include reproduction steps, expected behavior, and actual behavior.
If you are proposing a feature, explain the problem first, then the proposed solution.

## Code of Conduct

Participation in this project is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By submitting a pull request, you agree that your contribution will be licensed under the project's [MIT License](LICENSE).
