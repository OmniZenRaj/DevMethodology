---
name: add-issue
description: Create GitHub issues in the current repo and, when the project's AGENTS.md names one, add them to its project board. Use when creating tracked issues for bugs, features, or specs, especially after completing a design specification.
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Add Issue to GitHub Project

Create a GitHub issue in the current repo and, when the project's AGENTS.md (or CLAUDE.md) names a project board, add it to that board.

## When to Use

- Creating tracked issues for bugs, features, or specs
- After completing a design specification that needs implementation tracking

## Pre-Flight: Fix All Spec Issues FIRST (MANDATORY)

**BEFORE creating any issue or committing any spec**, ALL QC issues must be resolved:

1. **Check for open QC issues** — Review the spec's QC Review Results section
2. **Fix ALL CRITICAL, HIGH and MEDIUM issues**, or record the user's decision not to act. Update the spec file directly.
3. **Verify fixes** — Re-read the spec to confirm all issues are addressed
4. **Only then proceed** to Step 1 below

**NEVER**:
- Create an issue with unresolved CRITICAL, HIGH or MEDIUM spec issues (unless the user recorded a decision not to act)
- Commit a spec that has known unfixed issues
- Skip QC review to save time

If QC hasn't been run yet, run it first using the quality-control-enforcer agent.

---

## Workflow

Run the `gh` commands from inside the project's repository; `gh` targets the current repo by default.

### Step 1: Read the project board settings (optional)

If the project's AGENTS.md (or CLAUDE.md) names a GitHub project board, read its owner, project number and, for status updates, the project ID, Status field ID and the option ID for TODO. If it names no board, skip Steps 3 and 3b.

To look the ids up:
```bash
gh project list --owner <owner> --format json
gh project field-list <number> --owner <owner> --format json   # Status field id and option ids
```

### Step 2: Create Issue
```bash
gh issue create --title "<title>" --body "<description>"
```
Returns: the issue URL.

### Step 3: Add to Project Board (if configured)
```bash
gh project item-add <number> --owner <owner> --url <issue-url>
```

### Step 3b: Set Project Status to TODO (if configured)
New issues from specs should be **OPEN** and set to **TODO** (not Done/Closed).
```bash
# Get the item ID from the project
gh project item-list <number> --owner <owner> --format json --limit 10 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    if item.get('content', {}).get('number') == <ISSUE_NUMBER>:
        print(item['id'])
        break
"

# Set status to TODO
gh project item-edit \
  --project-id <project-id> \
  --id <ITEM_ID> \
  --field-id <status-field-id> \
  --single-select-option-id <todo-option-id>
```

### Step 3c: Update Spec Header with Issue Number and URL

**MANDATORY**: After creating the issue, replace `none yet` in the header's `**Issue**:` field with `[#NNN](<issue-url>)`. The header is three lines (design-spec.md "Header Format"):

```markdown
# [Feature Name] Specification
Date: YYYY-MM-DD · **Last Updated**: YYYY-MM-DD HH:MM · **Version**: vX.Y · <Author> with Claude Code AI Assistant
**Tier**: Standard | Critical · **Status**: <keep the current status> · **Reviews**: 🤖 QC n · 🧠 Codex n · **Issue**: none yet
```

Update the spec wherever it is (`temp/.planning/` during design, `docs/.planning/` once promoted).

### Step 4: Move Spec to docs/ and Ask to Commit

**MANDATORY**: Always move the spec and link it when creating an issue from a design specification. Never skip this step.

Once the issue is created, the `temp/.planning/` working copy is no longer needed — `docs/.planning/` is the canonical committed version.

```bash
# Move spec to tracked location (temp/ is gitignored, docs/ is committed)
mkdir -p docs/.planning
mv temp/.planning/<spec-file>.md docs/.planning/
```

**CRITICAL: ASK BEFORE COMMITTING OR PUSHING.** After moving the spec, use AskUserQuestion to confirm:
> "Spec moved to docs/.planning/. Ready to commit and push?"

Only after user confirms, proceed with:
```bash
git add docs/.planning/<spec-file>.md
git commit -m "Add spec: <brief description> [skip ci]"
git push

# Add spec link as comment on the issue
repo_url=$(gh repo view --json url -q .url); branch=$(git branch --show-current)
gh issue comment <issue-number> \
  --body "**Spec**: $repo_url/blob/$branch/docs/.planning/<spec-file>.md"
```

**NOTE**: After this step, only `docs/.planning/<spec-file>.md` exists. The `temp/.planning/` copy is deleted by the `mv` command. This avoids stale duplicate copies.

### Spec-only commits use `[skip ci]`

A spec commit changes nothing CI checks (`docs/.planning/*.md` is not code), so its message ends with `[skip ci]`; GitHub then skips the workflows. Do not use `[skip ci]` when the commit also changes code.

## CRITICAL: Never Auto-Commit or Auto-Push

**NEVER commit or push without explicit user approval.** This applies to:
- Spec files
- Code changes
- Any other files

Always use AskUserQuestion to confirm before any `git commit` or `git push` operation. The user must explicitly say "yes" or equivalent before proceeding.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `gh issue create` | Create issue in the current repo |
| `gh project item-add <number> --owner <owner> --url <url>` | Add to project board (if configured) |
| `gh issue comment <num>` | Add comment |
| `gh issue view <num>` | View issue |

## Notes

- **Project board**: optional; owner, number and field ids come from the project's AGENTS.md (or CLAUDE.md). Never hard-code them in this skill.
- **New issues should be OPEN and TODO** — never create as Closed/Done
- **Specs go in** `docs/.planning/` (not `temp/` which is gitignored)
- **After issue creation**, remove `temp/.planning/` copy — `docs/.planning/` is the canonical version
- **Spec naming**: `spec-YYYY-MM-DD-HHMM.md`

## Example

```bash
# Create issue
gh issue create \
  --title "Fix retry bug for failed jobs" \
  --body "## Summary
Bug: Jobs that fail validation are retried forever.
Fix: Mark them processed with an error result.
**Spec**: _Link to follow_"

# Add to project (only if AGENTS.md names a board)
gh project item-add <number> --owner <owner> --url <issue-url>

# Move spec (safe — no commit yet)
mv temp/.planning/spec-2025-01-22-1430.md docs/.planning/

# >>> ASK USER: "Ready to commit and push?" <<<
# Only after user confirms:

git add docs/.planning/spec-2025-01-22-1430.md
git commit -m "Add job retry fix spec [skip ci]"
git push

# Add spec link
gh issue comment <issue-number> --body "**Spec**: <repo-url>/blob/<branch>/docs/.planning/spec-2025-01-22-1430.md"
```

---

*Skill created: 2026-01-24*
