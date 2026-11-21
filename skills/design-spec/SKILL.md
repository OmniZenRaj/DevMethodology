---
name: design-spec
description: Manage the full lifecycle of design specifications. Create new specs, update existing specs, run QC reviews, sync to docs/.planning/, and track status transitions. Use when starting a new feature, reviewing a spec, or preparing a spec for implementation.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, AskUserQuestion
effort: medium
---

# Design Specification Lifecycle Manager

Manage design specs from creation through approval to implementation.

This skill cites "design-spec.md" sections. That file is the design-spec rules (the project's `.claude/.ai-rules/design-spec.md` if it exists, otherwise `~/.devmethodology/rules/design-spec.md`).

## When to Use

- Starting a new feature that requires a spec
- Reviewing or updating an existing spec
- Running QC review on a spec
- Moving a spec from `temp/` to `docs/.planning/`
- Changing spec status (Design Review → Approved)
- Preparing a spec for `/add-issue`

## Spec Header Format (MANDATORY)

Every spec MUST have this exact three-line header (design-spec.md "Header Format"):

```markdown
# [Feature Name] Specification
Date: YYYY-MM-DD · **Last Updated**: YYYY-MM-DD HH:MM · **Version**: vX.Y · <Author> with Claude Code AI Assistant
**Tier**: Standard | Critical · **Status**: Design Review · **Reviews**: 🤖 QC n · 🧠 Codex n · **Issue**: none yet
```

**Field rules:**
- `Date:` — Creation date, never changes; opens its line
- `**Last Updated**:` — Filesystem modified time of the spec file. Update on every edit.
- `**Version**:` — The version in the last row of `## Spec Version History`. Update with it.
- `**Tier**:` — Standard or Critical (design-spec.md "Review Tiers"). Only the user lowers it, from Critical to Standard, for a named scope that is recorded.
- `**Status**:` — See Status Transitions below
- `**Reviews**:` — Count of QC rows and of peer-review rows in `## Spec Version History`. Update with them.
- `**Issue**:` — `none yet` until `/add-issue` fills it.

## Status Transitions

| From | To | Trigger |
|---|---|---|
| `Design Review` | `Design Review` | QC fixes, peer review feedback, content updates (stays in review) |
| `Design Review` | `Design Approved for Implementation on {Date/Time}` | User approves AFTER the tier's review completes (peer review per tier) |
| `Design Approved...` | `Implementation Complete on {Date/Time}` | All code changes committed (same format as approval) |

**Rules:**
- Initial status is ALWAYS `Design Review`
- Never change to Approved without explicit user approval
- **CRITICAL**: Update status to `Implementation Complete on {Date/Time}` BEFORE committing the implementation — include the spec in the same commit so the committed version reflects the final status
- The `temp/.planning/` copy should already be removed by `/add-issue` — `docs/.planning/` is the canonical record
- **At Implementation Complete on {Date/Time}**: list the spec's [NOVEL] elements, recommend which recur, and ask the user which to promote to a row in the project's own `docs/PatternsLibrary.md` (copy the kit's library there first if the project has none), with `Origin: <spec> §x.y` in Ref / See also. Include the library edit in the implementation commit. Never promote without explicit user choice.
- Every stage appends a Spec Version History row (Version, Timestamp, Stage, Findings, Change).
- When approving, use exact format: `Design Approved for Implementation on February 8, 2026 14:30`
- **After approval, before implementation**: consider running the **Greenfield Rewrite** workflow (below) if the spec accumulated 5+ revision rounds. Strips inline `(v12.X — fixed)` annotations and consolidates QC/peer-review tables into a single Appendix at the back, so implementers and future reviewers see a clean design document instead of a tracked-changes log.

## Design Principles (MANDATORY)

All specs and implementations MUST follow these principles:

- **KISS** — Keep It Simple, Stupid. Prefer the simplest solution that works. Don't over-architect.

- **DRY** — Don't Repeat Yourself. Avoid duplicating logic. If the same pattern appears 3+ times, extract it.

- **YAGNI** — You Aren't Gonna Need It. Don't build for hypothetical future requirements. Only implement what's needed now.

- **SOLID** — Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion.

**Apply during spec review:**
- Challenge any section that adds complexity without clear justification
- Flag over-engineering (custom exception hierarchies, premature abstractions, feature flags for one-time changes)
- Prefer additive changes over modifications to existing code
- Three similar lines of code is better than a premature abstraction

## Workflow Commands

### Create New Spec

**Trigger**: User requests a new feature, architectural change, or significant refactoring.

0. Choose the tier: list the files the change will touch and state the tier with a one-line reason (design-spec.md "Review Tiers"). Trivial changes need no spec.
1. Verify current date from environment
2. Generate filename: `spec-{YYYY-MM-DD-HHMM}.md`
3. Create in `temp/.planning/` with full header (no Issue field yet)
4. Follow all required sections from design-spec.md:
   - Original Request
   - Executive Summary
   - Current State Analysis
   - Technical Specification (read the pattern library (the project's `docs/PatternsLibrary.md` if it exists, otherwise `~/.devmethodology/patterns/PatternsLibrary.md`) first; stamp each ### design element — design-spec.md "Pattern Stamping")
   - Breaking Change Analysis
   - Files to be Modified
   - Testing Checklist
   - Rollback Plan
   - Success Criteria
   - Codebase Analysis
   (Critical: all ten sections. Standard: the six in design-spec.md "Required Sections".)
5. Output clickable link: `Specification: temp/.planning/spec-YYYY-MM-DD-HHMM.md`

### Update Existing Spec

**Trigger**: User requests changes to a spec, or QC issues need fixing.

1. Read the spec file
2. Make requested changes
2a. If a ### design element is added, split or redesigned, add or refresh its stamp (design-spec.md "Pattern Stamping")
2b. Classify the update. Material (design, files or behaviour): repeat tier selection, reset Status to Design Review, run that tier's review, get a fresh approval before implementation continues. Editorial: keep the approval and append an "editorial" history row.
3. Update `**Last Updated**:` to current datetime (YYYY-MM-DD HH:MM)
4. Update whichever copy exists (`temp/` during design, `docs/` after issue creation)
5. Output: brief summary of what changed

**Getting Last Updated time:**
```bash
# Get filesystem modified time for Last Updated field
date -r "path/to/spec.md" "+%Y-%m-%d %H:%M"   # macOS and Linux
```

### Long Review (Critical tier)

**Trigger**: Critical-tier specs.

The tier sets the review: Critical gets Long Review, Standard gets Quick QC plus targeted Codex. Do not ask which review to run. The user may raise the tier or lower Critical to Standard for a named scope (design-spec.md "Review Tiers").

**Why Long Review exists**: on an earlier project, two rounds of same-vendor QC passed a spec for a job-processing change. The cross-vendor peer review in Step 5 then found a failure path both rounds had missed: one class of failed jobs was never marked processed, so the queue would have retried those jobs forever. Single-model review has blind spots, and Long Review is the minimum safety net for changes to critical processing paths.

#### Step 1: Metadata Verification

Check the spec header for completeness and accuracy:

1. Read the full spec file
2. Verify `**Last Updated**:` field exists — get actual time: `date -r "path/to/spec.md" "+%Y-%m-%d %H:%M"`
3. Search for linked GitHub issue: `gh issue list --search "<keywords>" --limit 5`
4. If an issue exists but the header's `**Issue**:` field still says `none yet`, fill it
5. Verify spec exists in expected location (`temp/.planning/` during design, `docs/.planning/` after issue creation)

#### Step 2: Code Reference Verification (parallel with Step 1)

Launch an Explore agent to verify ALL code line numbers and claims in the spec:

- Does each referenced function/code exist at or near the specified line number?
- If line numbers have shifted, what are the correct current line numbers?
- Are all callers of modified functions listed in the spec?
- Are all consumers of modified return values listed?
- Do dataclass/model fields match what the spec claims?

Fix any stale references, off-by-one errors, or missing callers directly in the spec.

#### Step 3: Claude QC Review

**Round limit first**: after 3 QC rounds on this spec without convergence, stop and ask the user before another round.

Launch quality-control-enforcer agent with a detailed prompt covering:

1. **Breaking changes** — What existing code will break?
2. **Data integrity risks** — Race conditions, double-writes, orphaned records
3. **Business logic breakage** — Does the change handle ALL edge cases?
4. **Integration points** — All consumers of modified interfaces
5. **Edge cases & failure modes** — What happens when things go wrong?
6. **Testing gaps** — Scenarios missing from the testing checklist
7. **Code flow dependencies** — Trace execution paths end-to-end
8. **Spec completeness** — All required sections present per project standards
9. **Pattern stamps** — apply design-spec.md "Pattern Stamping → Review checks" (a)–(f); report NOVEL: n of m

**CRITICAL**: The QC agent must READ actual source files to verify claims, not just review the spec text.

#### Step 4: Fix QC Issues

1. Fix all CRITICAL, HIGH and MEDIUM issues directly in the spec, or record the user's decision not to act
2. Document findings in `## QC Review Results` section
3. Update `**Last Updated**:` timestamp
4. Increment version in `## Spec Version History`
5. Spec stays in `temp/` during review (not yet committed)

If QC found issues, the spec status stays as `Design Review`.

#### Step 5: AI Peer Review (background)

**Purpose**: Independent review by a model from a second vendor, by default GPT through the Codex CLI, to catch blind spots and groupthink. If the second vendor is not available or not approved, the skill runs the review in a fresh same-vendor context and records in the review document that it was not cross-vendor.

Launch the `ai-peer-review` skill as a background agent:

1. Authors the review document in `temp/.planning/ai-peers/` from `ai-peer-review/review-template.md`
2. Runs Codex CLI (`codex exec`) detached in a read-only sandbox with the spec and source file references
3. Renders Codex's JSON answer into the review document (`review_tools.py render`)
4. Opens the review file in VS Code
5. Returns summary (triggers audio hook notification)

**User keeps working** — the sub-agent runs in background via `run_in_background: true` on the Task tool.

**Typical duration**: Codex peer reviews take 3-7 minutes depending on spec complexity and number of source files referenced. Complex specs with 10+ source files may take up to 10 minutes. Codex reads all referenced files before writing findings.

Do NOT block-wait with TaskOutput. The system sends a `<task-notification>` when the agent completes.

#### Step 6: Address Peer Review Findings

When the peer review notification arrives:

1. **Verify HIGH findings** against actual source code before accepting — read the referenced files
2. Fix confirmed HIGH and MEDIUM issues directly in the spec, or record the user's decision not to act
3. Document ALL findings in `## AI Peer Review Results` with a resolution table:

```markdown
| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| H1 | HIGH | [description] | ✅ Fixed in vN: [what changed] |
| M1 | MEDIUM | [description] | ✅ Accepted risk: [rationale] |
| L1 | LOW | [description] | Deferred (YAGNI): [rationale] |
```

4. Update `**Last Updated**:`, `**Version**:` and `**Reviews**:`, and append the peer-review row (`n high / n medium / n low`) to `## Spec Version History`

**Rules**:
- Claude authors the spec AND runs QC — peer review breaks this single-model dependency
- Peer review is informational, not blocking — user makes final call on disputed feedback
- Document ALL peer feedback even if not adopted (rationale required for rejected suggestions)

#### Step 7: Approval — follow the shared Approval step.

### Quick QC Review

**Trigger**: Standard-tier specs. A Critical spec may get Quick QC as an extra pass, but it never replaces Long Review unless the user lowers the tier (design-spec.md "Review Tiers").

1. Verify spec has all required sections for its tier
2. Apply the round limit (as in Long Review Step 3), then launch quality-control-enforcer agent with the spec (include dimension 9, Pattern stamps, and check (c) on every stamped element).
3. Document findings in the spec's `## QC Review Results` section
4. Fix all CRITICAL, HIGH and MEDIUM issues, or record the user's decision not to act.
4b. Derive targets: headings whose opening stamp starts with [NOVEL] in the current spec (or "the whole Technical Specification" when it has no ###). If any, run ai-peer-review in targeted mode; verify and handle findings the same way; re-review a target that changes materially.
5. Update `**Last Updated**:` after fixes
6. Append a version-history row for every stage, including the first pass.
7. Approval: follow the shared Approval step.

**Note**: Quick QC skips metadata and code-reference verification and runs Codex only on [NOVEL] elements (targeted mode).

### Approval (both tiers; only when the user explicitly approves)

0. Verify the effective tier and that this tier's review stages are complete for the current revision, and that no HIGH stamp finding from QC (design-spec.md "Pattern Stamping → Review checks") is unresolved without the user's decision.
1. Update status: `Design Approved for Implementation on {current date/time}`
2. Update `**Last Updated**:`
3. Spec stays in `temp/.planning/` until `/add-issue` moves it to `docs/.planning/`
4. Remind user to run `/add-issue` if no issue exists yet

### Greenfield Rewrite

**Trigger**: A spec has gone through 5+ revision rounds (Long Review iterations, business-model pivots, QC + peer-review cycles) and is now Approved or close to it. The main body has accumulated inline annotations like `(v12.12.3 — resolves QC Finding F3)`, `Earlier v12.9 ambiguity is removed in v12.12 — see version history`, `v12.5 drafts used X; restored to v12.1 phrasing`, etc. A first-time reader has to mentally context-switch into "what was the prior wrong version?" mode every few paragraphs.

**Why**: Specs that read greenfield are dramatically faster to review. Implementers shouldn't need to reconstruct intent from a tracked-changes log — they should see the final design statement plain, with audit trail available *if needed* in a single appendix.

**When to do it**:
- AFTER user approval (the shared Approval step complete) — design intent is locked, so consolidation is safe
- BEFORE implementation begins in earnest — implementers benefit most from clean prose
- IMMEDIATELY AFTER a major business-model pivot that obsoletes prior architecture (e.g., dropping a quota mechanism leaves the queue-deferral machinery as dead spec — sweep it out instead of marking each piece "deprecated in vN.M")

**The rewrite**:

1. **Strip dead architecture entirely.** When a feature is removed, don't mark it "deprecated, do not implement." Delete it. Add one bullet to the Appendix's "Superseded / reversed design elements" list with the rationale. Remove the corresponding §, sub-§, code blocks, file-list entries, testing items, and success criteria — everything tied to that feature.

2. **Strip inline version annotations from main body prose.** Remove `(v12.X — fixed)`, `(QC Finding F#)`, `Earlier v12.X said Y but now Z`, `restored to v12.X phrasing`, `v12.X scope`, `v12.X mandate`, etc. The main body should read as if written today. Anyone wanting "what changed in v12.11.2" can read the appendix or git log.

3. **Drop the section "v12.X Business Model Override" / "Architectural Notice" header blocks** if they exist. Those are bridges between old and new; in the greenfield form, the new IS the design.

4. **Consolidate iteration history into a single Appendix at the back.** Replace separate sections like `## QC Review Results — v12.12.3`, `## QC Review Results — v12.11`, `## AI Peer Review Results — v12.11.2`, `## Appendix A — Iteration History Summary` with ONE `## Appendix A — Review History` containing:

   - **Milestone timeline** — 6–10 row table grouping iterations by major stage (initial design, KISS pass, business pivot, UX lockdown, peer-review cycles, greenfield rewrite). Don't list every v12.11.1, v12.11.2, v12.11.3 — group them as "v12.11–v12.12 — Checkout UI" or similar.

   - **Review-round summary** — single table with one row per review round: who reviewed, finding counts by severity, resolution count. The full per-finding tables live in git history; the appendix points readers there.

   - **Superseded / reversed design elements** — bullet list of architectural decisions that were tried and abandoned, with one-line rationale each. Especially valuable for the "we considered X but rejected it" knowledge that future engineers will otherwise rediscover the hard way.

   - **Review artifacts pointer** — paths to Codex peer review documents in `temp/.planning/ai-peers/` and a note that full QC + peer review tables are preserved in git log on the spec file.

5. **Update the version history** with one entry: `Greenfield rewrite — removed dead [feature] architecture, consolidated review history to Appendix. Spec now reads greenfield.`

6. **Update `**Last Updated**:`** to current datetime.

**Discipline rules**:

- Keep every Spec Version History row and its timestamp; consolidate prose only.
- Stamps are design content: keep each stamp block verbatim as the first block of its element; delete a stamp only with its element; never move stamps to the Appendix; strip only (vN — …) annotations inside it.
- Do NOT delete the audit trail — preserve it in the consolidated Appendix and git history. Greenfield rewrite is about **signal-to-noise**, not erasure.
- Do NOT change design decisions during the rewrite. If you discover an issue, fix it as a separate edit with its own version-history entry.
- Do NOT compress so aggressively that the appendix loses load-bearing context (e.g., "we explicitly rejected X for reason Y" must survive — that's the kind of context that prevents future regressions).
- Migration numbers in the spec are HINTS, not contracts. Use placeholders like `NNNN_descriptive_name.py` when the actual number isn't yet allocated. The implementer's `makemigrations` will pick the next free number.

**When NOT to greenfield-rewrite**:

- Spec is still in active design iteration (status `Design Review`, fewer than ~3 review rounds). The version churn is the design conversation; flattening it prematurely loses signal.
- Spec just got a single QC pass and is otherwise stable. No need.
- Reviewers are actively walking the iteration history (e.g., new team member reading the spec for context). Wait until that pass is done.

**Net effect**: Main body line count typically drops 5–15%; the *signal-to-noise ratio* improves dramatically. A reviewer can now read the spec front-to-back as a single coherent design statement instead of unpacking 18 version annotations along the way.

### Move to docs/.planning/

**Trigger**: Spec is ready to be committed (after QC passes, typically via `/add-issue`).

```bash
# Move from temp to tracked location — removes temp copy
mkdir -p docs/.planning
mv temp/.planning/<spec-file>.md docs/.planning/
```

**Rule**: After moving, only `docs/.planning/<spec-file>.md` exists. The `temp/` copy is gone. This prevents stale duplicates. The `/add-issue` skill handles this automatically.

## Prototypes

**Location**: `temp/.prototypes/`

**Purpose**: Quick feasibility tests before committing to a full spec. Prototypes validate that an integration, API, or approach works before investing in spec creation and QC review.

**Convention**:
- Name files descriptively: `vendor_api_probe.py`, `payment_webhook_probe.py`
- Include a docstring header with usage examples
- Save raw API results to JSON in the same directory for analysis
- Add `Spec: (prototype - spec to be created after feasibility confirmed)` in the docstring
- After feasibility is confirmed and spec is created, update to `Spec: temp/.planning/spec-YYYY-MM-DD-HHMM.md`

**Workflow**: Prototype in `temp/.prototypes/` → Confirm feasibility → Create spec in `temp/.planning/` → Link prototype to spec

## File Locations

| Location | Purpose | Git Tracked |
|---|---|---|
| `temp/.prototypes/` | Feasibility prototypes and test scripts | No (gitignored) |
| `temp/.planning/` | Working drafts during design | No (gitignored) |
| `temp/.planning/ai-peers/` | Peer review documents (rendered from `ai-peer-review/review-template.md`) | No (gitignored) |
| `~/.claude/skills/ai-peer-review/review-template.md`, `fill-schema.json` | Review document template and the schema for Codex's answer | kit |
| `~/.devmethodology/scripts/review_tools.py` | `signals`, `lint`, `render` for the review document | kit |
| `docs/.planning/` | Committed specs linked to issues (**canonical — always supersedes `temp/`**) | Yes |
| `docs/PatternsLibrary.md` | The project's pattern vocabulary for spec stamps, if it keeps its own; otherwise `~/.devmethodology/patterns/PatternsLibrary.md` | Yes (project copy) |

**Precedence rule**: `docs/.planning/` always supersedes `temp/.planning/`. If a spec exists in both locations, the `docs/` version is the authoritative source. The `temp/` copy is stale and should be deleted.

**Flow**: Prototype in `temp/.prototypes/` (optional) → Choose tier → Spec in `temp/` → Review by tier (Quick QC + targeted Codex, or Long Review) → Approval → `/add-issue` moves to `docs/` → implement → floor → commit

## Finding Specs

**CRITICAL: `docs/.planning/` is the canonical source.** When the same spec filename exists in both `docs/.planning/` and `temp/.planning/`, **always use the `docs/` version** — it is the latest, committed, authoritative copy. The `temp/` copy is a stale working draft that should have been removed by `/add-issue`. Never read, review, or update a `temp/` spec if a `docs/` version of the same file exists.

**Lookup order**: Search `docs/.planning/` first. Only fall back to `temp/.planning/` if no match is found in `docs/`.

```bash
# Find spec by keyword — search docs/ first (canonical), then temp/ (drafts only)
grep -rl "keyword" docs/.planning/spec-*.md 2>/dev/null || grep -rl "keyword" temp/.planning/spec-*.md 2>/dev/null

# Find spec by issue number — docs/ first
grep -rl "#114" docs/.planning/spec-*.md 2>/dev/null || grep -rl "#114" temp/.planning/spec-*.md 2>/dev/null

# List all specs by date (most recent first) — docs/ specs take precedence
ls -lt docs/.planning/spec-*.md temp/.planning/spec-*.md 2>/dev/null
```

## Integration with Other Skills

| Skill / Tool | Handoff |
|---|---|
| `/add-issue` | After spec is QC-approved → create issue, commit spec, link |
| `/commit` | After spec updates → commit to docs/.planning/ |
| quality-control-enforcer | During QC review phase |
| `ai-peer-review` | Cross-vendor peer review — Codex runs in background, read-only; `review_tools.py render` writes `temp/.planning/ai-peers/` |

## Checklist: Spec Ready for /add-issue

Before handing off to `/add-issue`, verify:

- [ ] All required sections present

- [ ] Code line number references verified against current source (Critical tier)

- [ ] Pattern stamps valid for an applicable spec; [NOVEL] elements reviewed by QC and peer review (Critical: full peer review; Standard: targeted review of [NOVEL] elements)

- [ ] Claude QC review completed — all CRITICAL and HIGH issues resolved

- [ ] AI Peer Review completed — second-vendor feedback documented, or a same-vendor fresh-context review recorded as not cross-vendor (Critical, or a Standard spec with [NOVEL] elements)

- [ ] Peer review findings verified against source code and addressed (adopted or deferred with rationale) (Critical, or a Standard spec with [NOVEL] elements)

- [ ] `**Issue**:` field filled if an issue already exists

- [ ] `**Status**:` is `Design Approved for Implementation` (the shared Approval step is done; add-issue preserves Status and Tier)

- [ ] `**Last Updated**:` reflects latest edit

- [ ] `## Spec Version History` documents all review rounds

- [ ] Spec is in `temp/.planning/` ready for `/add-issue` to move to `docs/.planning/`

---

*Skill created: 2026-02-08*
*Long Review workflow added: 2026-02-08*
