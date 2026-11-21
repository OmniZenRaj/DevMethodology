# <Project name>

<One paragraph: what the project is and who uses it.>

## Setup and checks

- Language and version: <e.g. Python 3.12>
- Install: `<command>`
- Tests: `<command>`
- Lint: `<command>`
- Type check: `<command>`

## Design process

This project follows the dev methodology (`~/.devmethodology`).

- Every change has a tier: Trivial (no specification), Standard (six-section specification, Quick QC, cross-vendor review of `[NOVEL]` elements) or Critical (full specification, Long Review). If you cannot tell, the tier is Critical. Only a person lowers a tier.
- Specifications are drafted in `temp/.planning/spec-YYYY-MM-DD-HHMM.md` and moved to `docs/.planning/` when approved.
- Every design element is stamped from the pattern library or marked `[NOVEL]` with a reason.
- Before any commit: the tests, lint and type checks above, and QC review.

## Critical paths

A change to any of these is Critical:

- Agent configuration: `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.codex/`, `.agents/`
- CI and deployment: `.github/`, <deploy scripts>
- Dependency manifests and lock files: <e.g. pyproject.toml, uv.lock>
- Environment files: `.env*`
- Code that handles secrets, untrusted input or subprocesses: <paths>
- Public interfaces: <API, CLI, schema paths>
- Any change over 5 files or 200 lines

## Project board (optional)

Issues go to <GitHub project name or number>, used by the add-issue skill.

## Git

- Do not commit or push unless asked.
- Do not change a critical path without approval.
