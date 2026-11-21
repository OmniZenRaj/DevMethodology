---
name: ai-peer-review
description: Run an independent AI peer review of a design spec by a model from a second vendor, by default GPT through the Codex CLI. Fills a human-first review document from review-template.md, runs Codex read-only in the background, renders its structured answer, opens the result in VS Code. Use when a spec has passed QC and is ready for independent peer review before approval.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

# AI Peer Review via Codex CLI

Independent peer review of design specs by a model from a second vendor, by default GPT through the Codex CLI (`codex exec`). If the second vendor is not available or not approved, run the review in a fresh same-vendor context and record in the review document's `{reviewer_tool}` slot that it was not cross-vendor. The result is a review document a person reads top-down: rating, findings counts, reviewer signals, a scorecard by area, collapsible findings, and the reviewer's instructions in an appendix.

## When to Use

- After Claude QC review passes on a spec (Long Review Step 5)
- Quick QC step 4b, in targeted mode, for a Standard spec with `[NOVEL]` elements
- When the user requests peer review of any design document

## How It Works

Two authors, one document, one writer:

1. **The author** (a background sub-agent) copies `review-template.md`, fills every `{slot}` from deterministic sources, and runs `review_tools.py signals` and `lint`.
2. **Codex** reads the authored document and the files it lists, in a **read-only sandbox**, and answers with **one JSON object** shaped by `fill-schema.json` (`codex exec --output-schema … -o fill.json`). It never edits a file.
3. **`review_tools.py render`** puts each answer into its `<!-- REVIEWER:id | … -->` slot and derives the finding counts from the finding ids, so the header can never disagree with the body.

Because Codex never writes the document, nothing outside a slot can change, and a missing or malformed answer is a clean failure rather than a half-edited file.

## How to Invoke

**Do NOT wrap codex in a Task agent that waits on it** — the agent's stream watchdog kills silent long-running children (see "Why detached + medium effort" below). Either:

- **Preferred**: run the detached `nohup` command from Step 2 directly, then poll the PID. Simple, no wrapper, no watchdog.
- **Alternative**: a background sub-agent that *itself* launches detached and polls the PID rather than waiting on the process.

Launch as a background sub-agent via the Task tool:

```
Task tool:
  subagent_type: general-purpose
  run_in_background: true
  description: "AI peer review of spec"
  prompt: [see Agent Prompt Template below, filled with spec details]
```

After launching, tell the user:
> "Codex peer review running in background. You'll be notified when it's done and the review will open in VS Code."

Do NOT block-wait with TaskOutput. The system sends a `<task-notification>` when the agent completes.

## Paths

Defined once. `spec_stem` is `spec_filename` without `.md`; `round` is empty for the first review of a spec and `-vX.Y` for a later spec version (`review-spec-YYYY-MM-DD-HHMM-v1.4.md`). `review_tools.py` has `review_paths(spec_filename, round)` for the same names.

| Name | Path |
|---|---|
| `review_path` | `temp/.planning/ai-peers/review-{spec_stem}{round}.md` |
| `authored_path` | `temp/.planning/ai-peers/review-{spec_stem}{round}.authored.md` |
| `fill_path` | `temp/.planning/ai-peers/review-{spec_stem}{round}.fill.json` |
| `log_path` | `temp/.planning/ai-peers/codex-run-{spec_stem}{round}.log` |
| `pid_path` | `temp/.planning/ai-peers/codex-run-{spec_stem}{round}.pid` |

If `review_path` already exists, stop and ask rather than overwrite.

Every Bash call is a fresh shell, so **start every call with this block** (values from the launch prompt):

```bash
spec_path=temp/.planning/spec-YYYY-MM-DD-HHMM.md; round=""        # or round="-v1.4"
stem=$(basename "$spec_path" .md)$round; d=temp/.planning/ai-peers
authored_path=$d/review-$stem.authored.md; fill_path=$d/review-$stem.fill.json
review_path=$d/review-$stem.md; log_path=$d/codex-run-$stem.log; pid_path=$d/codex-run-$stem.pid
```

## Agent Prompt Template

The sub-agent runs in the background with no session, so the parent passes everything that needs judgement: `{spec_path}`, `{round}`, `{stage}`, `{author_model}`, `{purpose}`, `{focus_areas}`, `{scope}` (`full`, or the targeted-mode sentence from the rubric with the element headings filled in) and the file list (6 or fewer, the file the fix lands in first).

---

You are running an automated AI peer review of a design specification.

**Spec file**: `{spec_path}` (e.g., `temp/.planning/spec-YYYY-MM-DD-HHMM.md`)

Follow these steps exactly.

### Step 1: Author the review document

```bash
mkdir -p temp/.planning/ai-peers
cp ~/.claude/skills/ai-peer-review/review-template.md "$authored_path"
```

Fill every `{slot}` except `{reviewer_model}` and `{reviewer_tool}` (filled after the run) and the derived cells `{findings_counts}`, `{summary_counts}`, `{rating_icon}` (filled by `render`). Slot content in a table cell or a `<summary>` line is one line with no `|`.

| Author slot | Source |
|---|---|
| `{spec_title}`, `{spec_filename}`, `{relative_path_to_spec}`, `{tier}` | spec `# Title` and header; path arithmetic (`../spec-….md` for temp specs, `../../../docs/.planning/spec-….md` for committed specs) |
| `{spec_version}` | last row of the spec's Spec Version History |
| `{today}` | `date +%Y-%m-%d` |
| `{stage}`, `{author_model}`, `{purpose}`, `{focus_areas}`, `{scope}` | the launch prompt |
| `{history}` | the spec's Spec Version History rows, one numbered line each |
| `{signals_qc}`, `{qc_model}`, `{qc_summary}` | the spec's QC Review Results, naming the round (`v1.0 ✅ fixed in v1.1`; `➖ not yet run` if absent); `{qc_model}` is the `model:` in the quality-control-enforcer agent's frontmatter (`~/.claude/agents/quality-control-enforcer.md`, or the project's `.claude/agents/` copy), written as `opus (configured)` |
| `{signals_scan}`, `{scan_table}` | Step 1b |
| `{signals_external}` | `➖ no PR yet` until an implementation PR exists |
| `{novel}` | the `NOVEL: n of m` line that opens the spec's QC Review Results (`➖ not yet run` if absent) |
| `{numbered_file_list}` | the file list; name optional follow-up reads separately |
| `{rubric}` | the `## Reviewer rubric` section below, copied verbatim |

**Step 1b: signals.**

```bash
python3 ~/.devmethodology/scripts/review_tools.py signals "$spec_path"
```

The scan checks the spec for obvious secrets (private key blocks, AWS, Azure, OpenAI-style and GitHub keys, password assignments) and prints ✅ or ❌ per check with line numbers only. Paste the table into `{scan_table}` and the summary into `{signals_scan}`. **A ❌ result stops the review here**: the next step sends the spec text to the second vendor.

**Step 1c: lint.**

```bash
python3 ~/.devmethodology/scripts/review_tools.py lint "$authored_path"    # exit 0 required before launch
```

**Key principle**: Do NOT embed file contents — Codex has full repo access. Only provide file paths.

### Step 2: Run Codex CLI

**Round limit first**: after 3 peer-review rounds on this spec without convergence, stop and ask the user before another round.

**Launch DETACHED, read-only, with structured output — do NOT wait on the process.**

```bash
nohup codex exec -C "$(git rev-parse --show-toplevel)" -s read-only \
  -c model_reasoning_effort='"medium"' \
  --output-schema ~/.claude/skills/ai-peer-review/fill-schema.json -o "$fill_path" \
  "Read the peer review document at $authored_path and every file listed in its Appendix. Review the spec against the dimensions, areas, severities and rating scale in the Appendix. Answer with one JSON object: for each reviewer comment <!-- REVIEWER:id | instruction --> in the document, the property named id holds the content the instruction asks for. Do NOT modify any file." \
  > "$log_path" 2>&1 < /dev/null &
echo $! > "$pid_path"; disown
```

Then poll the PID (never block on the process). A foreground Bash call is capped at 600 s and runs take up to about 12 minutes, so run the poll as a **background** Bash call (`run_in_background: true`), which notifies you when it ends, with a 40-minute ceiling:

```bash
end=$((SECONDS + 2400)); pid=$(cat "$pid_path")
while kill -0 "$pid" 2>/dev/null && [ $SECONDS -lt $end ]; do sleep 15; done
if kill -0 "$pid" 2>/dev/null && ps -p "$pid" -o command= | grep -q "codex exec"; then
  kill "$pid"; echo "TIMEOUT: see $log_path"; else echo "codex finished"; fi
```

Without background calls, poll in chunks of at most 9 minutes. On a timeout the authored document is untouched, so a retry is a relaunch. Keep the log.

### Why detached + medium effort (learned after 4 consecutive failures)

Four different launch methods all failed on one spec, and the diagnosis took several attempts. Record it so nobody re-derives it:

| Attempt | Result | Actual cause |
|---|---|---|
| Task agent, foreground | killed at 600s | agent stream watchdog — codex emits no output while thinking |
| `run_in_background: true` | killed | harness reaped the child process |
| Bash foreground, 600s | timed out | genuinely slower than the ceiling |
| `setsid nohup ...` | never started | **`setsid` does not exist on macOS** |

Two root causes, both fixable:

1. **`~/.codex/config.toml` sets `model_reasoning_effort = "high"`.** On a large spec with 6-12 source files that pushes a run past every available execution window. Baseline check: a no-file-read prompt at `low` effort returns in ~6s, so the CLI itself is fast — the effort setting is the cost. Override to `medium` per-invocation with `-c model_reasoning_effort='"medium"'`. Do not edit the global config; other workflows may want `high`.

2. **Never make codex a child of a tool call.** Every wrapper in this environment has a timeout or watchdog, and codex is silent while reasoning so watchdogs read it as hung. `nohup ... &` + `disown` detaches it (macOS has `nohup`, not `setsid`). Poll the PID file. The success signal is `render` accepting `fill_path`: a zero exit code does not guarantee Codex answered in shape.

**Keep the file list to 6 or fewer**, ordered by importance. Codex reads them serially; each large file adds minutes. Prioritize the file the fix lands in, then its immediate collaborators.

**Verify the answer, not the exit code.** Codex can exit 0 having read everything and written nothing. A missing or empty `fill_path`, or one `render` rejects, is a failed review, not a clean one.

### Step 3: Render

Read `model:`, `reasoning effort:` and the version line (`OpenAI Codex vX`) from `log_path`; write them into `{reviewer_model}` and `{reviewer_tool}` in `authored_path`. Then:

```bash
python3 ~/.devmethodology/scripts/review_tools.py render "$authored_path" "$fill_path" -o "$review_path"
```

`render` exits 0 only when the answer has exactly the schema's properties, every cell value is single-line without `|`, the finding ids are unique and run from 1 within each severity with matching icons, the rating is not 🚀 or ☑️ while a HIGH exists, and no `{slot}` remains. On success delete `authored_path`, `fill_path` and `pid_path`; on failure keep them and report the problems it printed.

### Step 4: Open in VS Code

```bash
code --goto "$review_path"
```

### Step 5: Return summary

Return a concise summary in this format:

```
AI PEER REVIEW COMPLETE

Spec: {spec_path} v{spec_version}
Review file: {review_path}

Rating: {🚀|☑️|🚧|⛔} {one sentence}
Findings: 🛑 n HIGH · ⚠️ n MEDIUM · 💡 n LOW · ✨ NOVEL {novel}
Signals: 🧠 … · 🤖 … · 🔐 … · 🐇 …

Must-fix:
- [one line each]
```

---

## Reviewer rubric

Copied verbatim into the review document's Appendix as `{rubric}`, so Codex sees every rule it is graded against. Finding areas, severities and the rating scale are the vocabulary of every review.

**Dimensions** (items 1–9 keep their numbers; the targeted-mode sentence cites them):

1. **Field mapping correctness** — Do mappings match actual model fields?
2. **Feature parity gaps** — Any features missed from existing services?
3. **Interface compliance** — All abstract methods accounted for?
4. **Edge cases** — Error handling, empty responses, rate limiting
5. **Integration risks** — Will changes break existing code?
6. **External constraints** — Will output satisfy any downstream format/platform constraints?
7. **Cost/scalability concerns** — Any issues with projections?
8. **Alternative approaches** — Better ways to solve any part?
9. **Pattern stamps** — Read the "Pattern Stamping" section of the design-spec rules (the project's `.claude/.ai-rules/design-spec.md` if it exists, otherwise `~/.devmethodology/rules/design-spec.md`) and apply its Review checks (a)–(f), with its severities, to every design element.
10. **DDD compliance** — Are the spec's new terms defined once and used consistently? Do they collide with the project's existing vocabulary (its README, glossary, architecture rules and the field names of its core data types)? Do the proposed module boundaries follow the terms? When the project has a domain model, do its bounded contexts and rules apply? When nothing is wrong, say so under 📚 DDD compliance rather than leaving the area out.

**Areas** (every finding is filed under exactly one): 🧱 Design and architecture · 🛡️ Safety and trust · 🎯 Correctness against the code · 🔌 Integration and operations · 🧩 Patterns · 📚 DDD compliance · 🧪 Testing and evaluation · ✂️ Scope (YAGNI). Dimension 9 reports under 🧩, dimension 10 under 📚; the rest go where the finding's consequence lands.

**Severities and ids**: 🛑 HIGH `H1…` (must fix before approval) · ⚠️ MEDIUM `M1…` (fix, or record a decision not to) · 💡 LOW `L1…` (suggestion). Peer review has no CRITICAL level: a finding that invalidates the design is HIGH and sets the rating to ⛔.

**Rating scale**:

| Rating | Meaning | Rule |
|---|---|---|
| 🚀 Ready | approve as is | no HIGH, no MEDIUM |
| ☑️ Ready with notes | approve; the notes can be fixed during implementation | no HIGH; MEDIUM only |
| 🚧 Needs work | fix and re-review the changed parts | any HIGH |
| ⛔ Not ready | the design itself does not hold; rewrite before re-review | a HIGH that needs a redesign, or a Pattern check (a) structural failure |
| ➖ Not assessed | Scorecard cells and the Signals row only | the reviewer was not asked, or could not check |

Any HIGH caps the rating at 🚧. The header counts are derived from the finding ids, never typed.

**Targeted mode** (Standard-tier specs) is expressed only through the review document's Scope line. For a full review it reads `full`. For a targeted review the parent renders this sentence into `{scope}`, with the verbatim headings of the elements whose opening stamp starts with `[NOVEL]` (or "the whole Technical Specification" when it has no `###`) in place of the variable: "Review these design elements: `targeted_elements`. Apply items 5, 8, 9 and 10 to them; for each, list failure modes and whether a library pattern fits. Report any interaction elsewhere in the spec or code that makes a listed element unsafe." The file list keeps the design-spec rules file and the pattern library (the project's `docs/PatternsLibrary.md` if it exists, otherwise `~/.devmethodology/patterns/PatternsLibrary.md`). Findings are handled as in a full review.

---

## Integration with design-spec Skill

After the sub-agent returns its summary:

1. Present the summary to the user
2. Ask if they want to address the findings in the spec
3. If yes, read the review file and update the spec:
   - Fix HIGH and MEDIUM issues in the spec, or record the user's decision not to act
   - Add `## AI Peer Review Results` with the resolution table — this is the only copy; the review document carries a pointer to it
   - Append a peer-review row to the Spec Version History as `n high / n medium / n low`
   - Update `**Last Updated**:` and `**Reviews**:` in the header
4. Deferred items get rationale (e.g., "YAGNI — will address if real failures occur")

## File Locations

| Location | Purpose |
|---|---|
| `~/.claude/skills/ai-peer-review/SKILL.md` | This skill definition |
| `~/.claude/skills/ai-peer-review/review-template.md` | The review document template (author `{slots}` and `<!-- REVIEWER:id \| … -->` slots) |
| `~/.claude/skills/ai-peer-review/fill-schema.json` | JSON Schema for Codex's answer; a test keeps it equal to the template's slot ids |
| `~/.devmethodology/scripts/review_tools.py` | `signals`, `lint`, `render` (tests: `tests/test_review_tools.py` in the kit) |
| `temp/.planning/ai-peers/review-{spec_stem}{round}.md` | The rendered review |
| `temp/.planning/ai-peers/codex-run-{spec_stem}{round}.log` | Codex log for that round (model, effort, version on its first lines) |

## Prerequisites

- Codex CLI on PATH (0.163.0 or later: `--output-schema`, `-o`, `-s read-only`)
- Codex authenticated (`codex login`)
- VS Code `code` CLI available in PATH
- Python 3.10 or later for `review_tools.py` (standard library only)

---

*Layout: human-first document, structured Codex fill.*
