# Dev Methodology

A spec-first method for building software with AI coding agents: Claude Code skills, a QC agent and cross-vendor review, with a VS Code setup to match.

## The method

1. An engineer writes the brief: the objective, user stories with testable acceptance criteria, and the constraints.
2. The agent writes a design specification before any code. Every design element is stamped with the proven patterns it uses, or marked `[NOVEL]` with a reason.
3. The specification is reviewed in proportion to its risk tier:
   - **Trivial:** no specification.
   - **Standard:** a six-section specification, a quick QC pass, and a cross-vendor review of the novel elements.
   - **Critical:** a full specification and the Long Review, ending with a full cross-vendor review.
4. A person approves the specification.
5. The code is built to the specification and checked by the project's own tests, lint and type checks, then QC, before anything is committed.

Tiers only go up automatically. Only a person can lower one.

## What is in the kit

| Path | What it is |
|---|---|
| `skills/design-spec` | The specification lifecycle: create, update, review, approve |
| `skills/ai-peer-review` | Cross-vendor review: runs a second vendor's model (GPT through the Codex CLI by default) read-only and renders a review document |
| `skills/add-issue` | Creates a GitHub issue for an approved specification |
| `skills/session-memory-save` | Saves session context so work survives `/clear` |
| `agents/quality-control-enforcer.md` | Same-vendor QC for specifications and code |
| `commands/commit.md` | `/commit`, the formal commit command |
| `rules/design-spec.md` | The rules: tiers, required specification sections, pattern stamping, build steps |
| `patterns/PatternsLibrary.md` | The pattern library used for stamps |
| `scripts/review_tools.py` | Lints and renders the peer-review document |
| `templates/ProjectAGENTS.md` | A starting `AGENTS.md` for a project that uses the method |
| `vscode/` | Settings, keybindings and extension list |
| `scripts/claude-code.command` | Terminal launcher that returns to a shell when Claude Code exits |

## Install

```bash
git clone <this repo> ~/DEV/DevMethodology
cd ~/DEV/DevMethodology
./install.sh --dry-run --all   # see what would change
./install.sh                   # skills, agent, command and scripts
./install.sh --vscode          # merge VS Code settings and keybindings
```

The installer links one copy of each skill into `~/.claude/skills/`, and into `~/.codex/skills/`, `~/.agents/skills/` and `~/.cursor/skills/` when those folders exist. Edit a skill once and every tool sees the change. Existing files are never overwritten.

In each project, copy `templates/ProjectAGENTS.md` to `AGENTS.md`, fill in its critical paths and commands, and link `CLAUDE.md` to it:

```bash
ln -s AGENTS.md CLAUDE.md
```

Claude Code reads `CLAUDE.md`. Codex, Cursor and most other agent tools read `AGENTS.md`.

## Models

The skills work with any capable model. The QC agent asks for Opus. The cross-vendor review needs a second vendor's model, by default GPT through the [Codex CLI](https://github.com/openai/codex). Where no second vendor is available or approved, the review runs in a fresh same-vendor context and says so in the review document.

## Workplace use

On an employer's machine, the employer's policies come first. Check extensions against the allowlist and use only approved model vendors.
