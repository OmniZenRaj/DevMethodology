## Peer Review: {spec_title}

📄 [{spec_filename}]({relative_path_to_spec}) · **v{spec_version}** · {tier} tier · {today}

| | |
|---|---|
| **Rating** | <!-- REVIEWER:rating | one of 🚀 Ready · ☑️ Ready with notes · 🚧 Needs work · ⛔ Not ready, in bold, then one sentence --> |
| **Findings** | {findings_counts} · ✨ NOVEL: {novel} |
| **Signals** | 🧠 Peer review: <!-- REVIEWER:signal | the rating icon and two words --> · 🤖 Claude QC: {signals_qc} · 🔐 Secret scan: {signals_scan} · 🐇 External reviewers: {signals_external} |
| **Stage** | {stage} · spec by Claude {author_model} |

**What this spec is for.** {purpose}

**Bottom line.** <!-- REVIEWER:bottom_line | two to five sentences: what holds up, what must change, whether a redesign is needed -->

<details>
<summary><b>How we got here</b> (session history)</summary>

{history}

</details>

## 📊 Scorecard

| Area | Rating | Findings |
|---|---|---|
| 🧱 Design and architecture | <!-- REVIEWER:design_rating | one of ✅ Good · 🚧 Gaps · ⛔ Broken · ➖ Not assessed --> | <!-- REVIEWER:design_ids | finding ids grouped by severity icon, e.g. "🛑 H1 · ⚠️ M2, M3", or "none" --> |
| 🛡️ Safety and trust | <!-- REVIEWER:safety_rating | rating as above --> | <!-- REVIEWER:safety_ids | ids or none --> |
| 🎯 Correctness against the code | <!-- REVIEWER:correctness_rating | rating as above --> | <!-- REVIEWER:correctness_ids | ids or none --> |
| 🔌 Integration and operations | <!-- REVIEWER:integration_rating | rating as above --> | <!-- REVIEWER:integration_ids | ids or none --> |
| 🧩 Patterns | <!-- REVIEWER:patterns_rating | rating as above --> | <!-- REVIEWER:patterns_ids | ids or none --> |
| 📚 DDD compliance | <!-- REVIEWER:ddd_rating | rating as above --> | <!-- REVIEWER:ddd_ids | ids or none --> |
| 🧪 Testing and evaluation | <!-- REVIEWER:testing_rating | rating as above --> | <!-- REVIEWER:testing_ids | ids or none --> |
| ✂️ Scope (YAGNI) | <!-- REVIEWER:scope_rating | rating as above --> | <!-- REVIEWER:scope_ids | ids or none --> |

---

## 👥 Reviewers

<details>
<summary>🧠 <b>Independent peer review</b>: <code>{reviewer_model}</code> · {rating_icon} · {summary_counts}</summary>

- **Tool:** {reviewer_tool}.
- **Read:** <!-- REVIEWER:files_read | the files you actually read, on one line -->
- **Did not:** modify any file.
- **Every finding below is from this reviewer** unless marked otherwise.

</details>

<details>
<summary>🤖 <b>Internal QC</b>: Claude {qc_model} · {signals_qc}</summary>

{qc_summary}

</details>

<details>
<summary>🔐 <b>Secret scan</b>: no model · {signals_scan}</summary>

{scan_table}

- A regex scan for obvious credential shapes, run before the spec text goes to the second vendor. A clean result does not prove the spec holds no secret.

</details>

<details>
<summary>🐇 <b>External AI reviewers</b> (CodeRabbit, Greptile, Cursor Bugbot): {signals_external}</summary>

- These tools review pull requests. A spec in `temp/.planning/` is first seen when `/add-issue` commits it, or when the implementation PR opens.

</details>

---

## 🔍 Findings by area

<!-- REVIEWER:findings | Markdown. One "### <icon> <area>" heading per area that has findings, in scorecard order. Each finding is a <details> block whose summary line is exactly "<summary>🛑 <b>H1. Title</b></summary>" (⚠️ and M1… for MEDIUM, 💡 and L1… for LOW), numbered from 1 within each letter; must-fix findings use <details open>. Each block has Problem, Where (file:line or spec line) and Fix. The 🧩 Patterns area always ends with a "<summary>✅ <b>Pattern audit (a)–(f)</b></summary>" block and the 📚 DDD compliance area always has one block, even when it reports nothing wrong; neither carries a finding id. In targeted mode, cover only the listed elements and mark the other scorecard rows ➖. -->

---

## ✅ What the spec does well

<!-- REVIEWER:strengths | three to six Markdown bullets -->

---

## 📝 Resolution

Decisions on every finding are recorded in the spec's `## AI Peer Review Results` section, not here.

<details>
<summary><b>Appendix: instructions given to the reviewer</b></summary>

**Files:**

{numbered_file_list}

**Scope:** {scope}

**Focus areas:** {focus_areas}

{rubric}

**Rules:** do not modify any file. Answer with one JSON object whose property names are the slot ids in this document's reviewer comments, each holding the content that comment asks for; the author renders your answer into this document.

</details>
