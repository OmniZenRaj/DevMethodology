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

## Skill routing

This section decides which skill owns each step. It takes priority over any plugin's own trigger rules, including the Superpowers rule to use a skill whenever there is any chance it applies.

| Step | Skill | Notes |
|---|---|---|
| 1. Brief and acceptance criteria | (the engineer) | Objective, user stories with testable acceptance criteria, constraints |
| 2. Clarifying questions | superpowers `brainstorming` | Questions and options only. Its output feeds the spec. Do not write a separate design doc |
| 3. Specification, tier and pattern stamps | `design-spec` | Owns the design. Trivial changes skip to step 6 |
| 4. Specification review | `quality-control-enforcer`, then `ai-peer-review` | Standard: Quick QC plus cross-vendor review of `[NOVEL]` elements. Critical: Long Review |
| 5. Approval | (the engineer) | Nothing is built before the specification is approved |
| 6. Implementation plan | superpowers `writing-plans` | Plans from the approved specification |
| 7. Build | superpowers `subagent-driven-development` or `executing-plans` | With `test-driven-development`, and `systematic-debugging` for any failure |
| 8. Proof | superpowers `verification-before-completion` | Show evidence for each acceptance criterion in the specification |
| 9. Final review | `quality-control-enforcer` | Use this instead of superpowers `requesting-code-review` |
| 10. Commit | `/commit` | Only when asked |

Work-specific skills, if installed: <e.g. any build, test or lint command: work-just; branches and pull requests: work-git; tickets: work-jira; cluster testing: k8s-test-cluster>.

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
