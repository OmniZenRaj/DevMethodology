---
name: session-memory-save
description: Save current session context to a session-specific file so work can be resumed after /clear. Session files go to the current repo's temp/.memories/. Captures what was worked on, key decisions, issue numbers, spec links, and file paths. Ends with "I've memorized our work. Let's clear and GO!" Use when wrapping up a session or before /clear.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# Session Memory Save

**Primary use case**: Low on context → save a session file → /clear → resume. Do this fast.

MEMORY.md updates are the **exception**, not the rule. Most sessions just need a session file.

---

## Fast Path (default — use this 90% of the time)

### Step 1: Generate session file

```bash
DIR=temp/.memories
mkdir -p "$DIR"
SESSION_ID=$(date +%Y%m%d-%H%M%S)
```

**Auto-generate slug** from what was worked on (don't ask the user):
- `content-moderation` not `session-20260314`
- `refer-to-fixes` not `general-work`
- Max 30 chars, lowercase, hyphens

File: `$DIR/session-{ID}-{slug}.md`

### Step 2: Write session file

```markdown
# Session — {slug} — {DATE} {TIME}
Saved: {TIMESTAMP}

## Resume From Here
{1-2 sentences: what to do next, where things are at}

## What Was Worked On
{bullet list — be specific, include line numbers and file paths}

## Key Decisions
{bullet list — only decisions that affect future work}

## Files Modified
{full paths, one per line}

## Issues / Specs
{#NNN links and spec paths with current status}

## TODO / Left Unfinished
{anything blocking or in-progress}

## Quick Reopen
code {key file 1}
code {key file 2}
```

Use **absolute paths** everywhere in the file so it can be resumed unambiguously.

### Step 3: Output and done

```
✅ Session saved: {full path to session file}

📋 {2-4 bullet summary of what was captured}

I've memorized our work. Let's clear and GO!
```

**No MEMORY.md update needed** for typical sessions. Skip to done.

---

## When to Also Update MEMORY.md

Only update MEMORY.md if this session produced **genuinely new durable knowledge** — facts that should influence *every future session*, not just resuming this one.

Ask: "Would I need to know this in a session 2 months from now that has nothing to do with today's work?"

- **Yes** → update MEMORY.md (e.g. new rule discovered, new permanent preference, new permanent quirk)
- **No** → session file is enough (e.g. implementation progress, spec status, what was tested)

### MEMORY.md rules (when you do update it)

The current project's memory is `~/.claude/projects/<cwd with / replaced by ->/memory/`, e.g. `~/.claude/projects/-home-me-src-myapp/memory/` for `/home/me/src/myapp`.

**MEMORY.md = index only.** Target: under 80 lines / 4KB. It loads every conversation.

| Content type | Where to write |
|---|---|
| New pending feature / spec | Update `project_pending_work.md` table |
| Detailed implementation notes (>10 lines) | New `project_{feature}.md` + 1-line pointer in MEMORY.md |
| Feedback / behavior correction | New `feedback_{topic}.md` + 1-line pointer in MEMORY.md |
| Short rule/preference (<5 lines) | Inline in MEMORY.md directly |
| Session-specific progress | Session file only — NEVER MEMORY.md |

**Never** append `# currentDate` — the system injects it at runtime.

After any MEMORY.md write: `wc -l ~/.claude/projects/$(pwd | tr / -)/memory/MEMORY.md` — if > 80 lines, extract the largest section to a `project_*.md` file.

---

## Resuming a Session

User pastes a session file path → read it immediately → continue the work described.

```bash
# Recent sessions in this repo
ls -lt temp/.memories/session-*.md | head -10

# Find by topic
ls temp/.memories/*<topic>* 2>/dev/null
```

---

*Skill created: 2026-02-24 | Simplified: 2026-03-14*
