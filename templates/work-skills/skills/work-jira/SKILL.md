---
name: work-jira
description: Read and update Jira tickets and link code to them. Use when starting work on a ticket, moving a ticket between statuses, adding a comment, or creating a ticket.
---

# Jira

## Access

<How the agent reaches Jira: an approved MCP server, the `acli` CLI, or not at all. If there is no approved access, draft the text and ask the user to paste it.>

## The team's workflow

| Status | Meaning | Who moves it |
|---|---|---|
| <To Do> | <...> | <...> |
| <In Progress> | <...> | <...> |
| <In Review> | <...> | <...> |
| <Done> | <...> | <...> |

## Rules

- Ticket key format: `<PROJECT>-<number>`. Use it in branch names and commit messages (see work-git).
- Ask the user before moving a ticket's status, assigning it, or creating a ticket.
- Comments are factual: what changed, the PR link, how it was verified.
- Required fields when creating a ticket: `<list>`.
