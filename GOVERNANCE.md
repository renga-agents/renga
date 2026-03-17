# Governance

## Current Model

renga currently uses a BDFL model.
The lead maintainer has final authority over technical direction, release decisions, and project scope.

## Roles

### Maintainer

The maintainer:

- Sets project direction and scope
- Reviews and merges pull requests
- Manages releases and roadmap
- Decides when an RFC is required
- Appoints future Champions

### Champions

Champions are trusted contributors with review authority in a specific area.
This is a future role intended for the growth stage of the project.

Initial Champion areas:

- Agents and plugin ecosystem
- Documentation and translation
- Platform ports and distribution

Typical criteria for becoming a Champion:

- At least 5 merged pull requests in the relevant area
- At least 3 months of active contribution
- Nomination by the maintainer

### Contributors

Anyone with a merged pull request is considered a contributor.

## Progression Path

| Stage | Criteria | Governance Model |
| --- | --- | --- |
| Seed | 0-500 stars and fewer than 5 regular contributors | BDFL |
| Growth | 500-2000 stars and 5-15 regular contributors | BDFL + Champions |
| Mature | More than 2000 stars and more than 15 regular contributors | Core Team |

The project may move between stages when the maintainer judges that review load, contributor activity, and community expectations justify it.

## RFC Process

Significant changes should go through an RFC discussion before implementation.
Examples include:

- New core agent categories
- Breaking changes to agent format or config files
- Governance model changes
- Major distribution or CLI changes

Default RFC path:

1. Open a GitHub Discussion.
2. Leave the discussion open for at least 7 days.
3. Gather feedback and refine the proposal.
4. The maintainer makes the final decision.
5. If accepted, record the decision in the relevant documentation or ADR.

## Conflict Resolution

When disagreement happens:

1. Start in the pull request or issue.
2. Move to a GitHub Discussion if the topic needs broader review.
3. The maintainer makes the final call if no consensus is reached.

## Code of Conduct

Community participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
