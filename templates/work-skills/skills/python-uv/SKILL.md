---
name: python-uv
description: Manage Python versions, virtual environments and dependencies with uv. Use when creating an environment, adding or upgrading a dependency, running Python code or tests outside a just recipe, or when a command would use pip.
---

# Python with uv

The team uses uv for all Python tooling. Never call `pip`, `pip install` or `python -m venv` directly.

## Rules

- Prefer the team's `just` recipes (see the work-just skill). Use the commands below only when no recipe covers the task.
- Python version: <version>, pinned in `<.python-version / pyproject.toml>`.
- Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Commit both together.
- Do not edit `uv.lock` by hand.
- Adding or upgrading a dependency is a <tier or approval rule>. Say why it is needed.

## Commands

| Task | Command |
|---|---|
| Create or update the environment from the lock file | `uv sync` |
| Run a command in the environment | `uv run <command>` |
| Run the tests | `uv run pytest` |
| Add a dependency | `uv add <package>` |
| Add a dev dependency | `uv add --dev <package>` |
| Remove a dependency | `uv remove <package>` |
| Upgrade one package | `uv lock --upgrade-package <package>` then `uv sync` |
| Install a Python version | `uv python install <version>` |

## Package index

<The internal package index URL and how uv is configured to use it, if any.>
