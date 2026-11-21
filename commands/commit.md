# /commit - Formal Commit Command

Creates a clean commit from the current changes, then pushes and checks the workflow run.

## Command Syntax
```bash
/commit                          # commit, then push
/commit "Custom message"         # use this commit message
```

## Workflow

1. **Check the changes**: `git status`, `git diff`, `git log --oneline -5`.
2. **Stage** only this session's files (see Parallel Session Awareness). List any modified file you are leaving out and ask the user to confirm.
3. **Confirm the floor ran** for this change: the project's own test, lint and type commands, its quality gate if it has one, and QC review. If the gate routed the change to a person, the user's acceptance goes in the commit body.
4. **Commit** with a message in the format below.
5. **Push**, then check the run: `gh run list --limit 1`. Report the run's status and URL (`gh run view <run-id> --json url`), or that no run started.

## Commit Message Format

```
<emoji> <subject>

<body>
```

### Types

Begin commit messages with one of these symbols. Do not use `bug:`, `feat:`-style prefixes.

| Symbol | Description                         | Commit change type                    |
|--------|-------------------------------------|---------------------------------------|
| ✅     | White heavy check mark              | Task complete, passed test            |
| ✔️     | Heavy check mark                    | Confirmed, fixed                      |
| ❌     | Cross mark                          | Failure, undo, bug                    |
| 🐛     | Bug                                 | Bugfix                                |
| ✨     | Sparkles                            | New feature                           |
| 🔥     | Fire                                | Code removal/refactor                 |
| 🚑     | Ambulance                           | Hotfix, urgent patch                  |
| 📝     | Memo                                | Documentation                         |
| 🔒     | Lock                                | Security update                       |
| 🚧     | Construction                        | Work in progress                      |
| ⬆️     | Up arrow                            | Dependency/upgrade                    |
| ⬇️     | Down arrow                          | Dependency/downgrade                  |
| 📦     | Package                             | New package/dependency                |
| 🔧     | Wrench                              | Configuration change                  |
| ♻️     | Recycle                             | Code refactor                         |
| 🧪     | Test tube                           | New or updated tests                  |
| 📈     | Chart with up trend                 | Performance improvement               |
| 🏗️     | Building construction               | Infrastructure                        |
| ➕     | Plus sign                           | Add file/feature                      |
| ➖     | Minus sign                          | Remove file/feature                   |
| 💚     | Green heart                         | Build passing/CICD                    |

## Parallel Session Awareness

Multiple AI agent sessions may be working in this project simultaneously. Before staging any files:

1. **Run `git diff --name-only HEAD` and `git status`** — identify ALL modified files
2. **Separate session files**: For each modified file NOT related to the current session's task, check if another session may have changed it
3. **Check for overlap in shared files**: If the current session AND another session both touched the same file (e.g. `settings.py`, `models.py`, a service file), run `git diff <file>` and verify the changes do NOT conflict or stomp each other
4. **Stage only session-relevant files**: Only `git add` files that belong to this session's changes. Leave other sessions' files unstaged unless explicitly told otherwise
5. **Flag unrelated modified files to the user**: Always list any unstaged files you are intentionally skipping and ask the user to confirm they should remain unstaged

**Example check workflow:**
```bash
git status                          # See all modified files
git diff HEAD -- path/to/file.py    # Inspect any shared file before staging
```

If overlap is detected in a shared file, **STOP and report to user** before committing. Do not guess which changes belong to which session.

## Rules

- No attribution such as "Generated with Claude" or "Co-Authored-By: Claude".
- `[skip ci]` only for a commit that changes nothing CI checks (a spec-only commit); never on a commit that also changes code.
- Do not commit temporary files, debug code, personal configuration, large binaries or secrets.
- Suggest splitting large changes into separate commits, each one a logical unit that can be reverted on its own.
