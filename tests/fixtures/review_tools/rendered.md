## Peer Review: [spec_title]

📄 [[spec_filename]]([relative_path_to_spec]) · **v[spec_version]** · [tier] tier · [today]

| | |
|---|---|
| **Rating** | 🚧 **Needs work.** One gap. |
| **Findings** | 🛑 1 must-fix (HIGH) · ⚠️ 1 should-fix (MEDIUM) · 💡 0 suggestions (LOW) · ✨ NOVEL: [novel] |
| **Signals** | 🧠 Peer review: 🚧 needs work · 🤖 Claude QC: [signals_qc] · 🔐 Secret scan: [signals_scan] · 🐇 External reviewers: [signals_external] |
| **Stage** | [stage] · spec by Claude [author_model] |

**What this spec is for.** [purpose]

**Bottom line.** Holds up.

One gap.

<details>
<summary><b>How we got here</b> (session history)</summary>

[history]

</details>

## 📊 Scorecard

| Area | Rating | Findings |
|---|---|---|
| 🧱 Design and architecture | ✅ Good | none |
| 🛡️ Safety and trust | ✅ Good | none |
| 🎯 Correctness against the code | ✅ Good | none |
| 🔌 Integration and operations | ✅ Good | none |
| 🧩 Patterns | ✅ Good | none |
| 📚 DDD compliance | ✅ Good | none |
| 🧪 Testing and evaluation | ✅ Good | none |
| ✂️ Scope (YAGNI) | ✅ Good | none |

---

## 👥 Reviewers

<details>
<summary>🧠 <b>Independent peer review</b>: <code>[reviewer_model]</code> · 🚧 · 🛑 1 · ⚠️ 1 · 💡 0</summary>

- **Tool:** [reviewer_tool].
- **Read:** the spec, `scan.py`
- **Did not:** modify any file.
- **Every finding below is from this reviewer** unless marked otherwise.

</details>

<details>
<summary>🤖 <b>Internal QC</b>: Claude [qc_model] · [signals_qc]</summary>

[qc_summary]

</details>

<details>
<summary>🔐 <b>Secret scan</b>: no model · [signals_scan]</summary>

[scan_table]

- A regex scan for obvious credential shapes, run before the spec text goes to the second vendor. A clean result does not prove the spec holds no secret.

</details>

<details>
<summary>🐇 <b>External AI reviewers</b> (CodeRabbit, Greptile, Cursor Bugbot): [signals_external]</summary>

- These tools review pull requests. A spec in `temp/.planning/` is first seen when `/add-issue` commits it, or when the implementation PR opens.

</details>

---

## 🔍 Findings by area

### 🛡️ Safety and trust

<details open>
<summary>🛑 <b>H1. A gap</b></summary>

- **Problem:** x

</details>

### 🧩 Patterns

<details>
<summary>⚠️ <b>M1. Stamp</b></summary>

- x

</details>

<details>
<summary>✅ <b>Pattern audit (a)–(f)</b></summary>

- pass

</details>

### 📚 DDD compliance

<details>
<summary>➖ <b>Nothing found</b></summary>

</details>

---

## ✅ What the spec does well

- one
- two
- three

---

## 📝 Resolution

Decisions on every finding are recorded in the spec's `## AI Peer Review Results` section, not here.

<details>
<summary><b>Appendix: instructions given to the reviewer</b></summary>

**Files:**

[numbered_file_list]

**Scope:** [scope]

**Focus areas:** [focus_areas]

**Dimensions:** one. **Rating scale:** 🚀 ☑️ 🚧 ⛔.

**Rules:** do not modify any file. Answer with one JSON object whose property names are the slot ids in this document's reviewer comments, each holding the content that comment asks for; the author renders your answer into this document.

</details>
