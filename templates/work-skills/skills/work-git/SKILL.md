---
name: work-git
description: Create branches, write commits and open pull requests the way the team does. Use when starting work on a ticket, committing, pushing, or opening or updating a pull request.
---

# Git and pull requests

## Branches

- Name: `<type>/<TICKET-KEY>-<short-description>`, for example `<feature/ABC-123-add-retry>`.
- Branch from `<main / develop>`.
- Protected branches: `<list>`. Never push to them directly.

## Commits

- Format: `<format, e.g. "ABC-123: imperative summary">`.
- <Signing requirement, if any.>
- Do not commit or push unless the user asks.

## Pull requests

- Use the template in `<.github/pull_request_template.md>`.
- Title: `<format>`.
- Link the ticket: `<how>`.
- Required reviewers: `<rule>`. Required checks: `<list>`.
- Merge method: `<squash / rebase / merge>`. Delete the branch after merging: `<yes/no>`.

## Never

- Force-push to a shared branch.
- Rewrite history that others have pulled.
- Bypass required checks or reviews.
