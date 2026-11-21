"""scripts/review_tools.py: signals, lint and render for the review document."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import review_tools as rt

# Assembled at run time so this repository never contains a credential-shaped string.
FAKE_AWS_KEY = "AKIA" + "Q" * 16

SKILL = Path(__file__).resolve().parent.parent / "skills" / "ai-peer-review"
TEMPLATE = (SKILL / "review-template.md").read_text(encoding="utf-8")
SCHEMA = json.loads((SKILL / "fill-schema.json").read_text(encoding="utf-8"))
AUTHOR_SLOTS = {
    "spec_title", "spec_filename", "relative_path_to_spec", "spec_version", "tier", "today",
    "stage", "author_model", "purpose", "history", "signals_qc", "qc_model", "qc_summary",
    "signals_scan", "scan_table", "signals_external", "novel", "numbered_file_list",
    "scope", "focus_areas", "rubric", "reviewer_model", "reviewer_tool",
}


def authored(**overrides: str) -> str:
    """The template with every author slot filled, late slots included."""
    values = {slot: f"[{slot}]" for slot in AUTHOR_SLOTS}
    values["rubric"] = "**Dimensions:** one. **Rating scale:** 🚀 ☑️ 🚧 ⛔."
    values.update(overrides)
    text = TEMPLATE
    for slot, value in values.items():
        text = text.replace("{" + slot + "}", value)
    return text


def fill(**overrides: str) -> dict[str, str]:
    values = {slot: "✅ Good" if slot.endswith("_rating") else "none"
              for slot in SCHEMA["required"]}
    values.update({
        "rating": "🚧 **Needs work.** One gap.", "signal": "🚧 needs work",
        "bottom_line": "Holds up.\n\nOne gap.", "files_read": "the spec, `scan.py`",
        "findings": (
            "### 🛡️ Safety and trust\n\n<details open>\n<summary>🛑 <b>H1. A gap</b></summary>\n\n"
            "- **Problem:** x\n\n</details>\n\n### 🧩 Patterns\n\n<details>\n"
            "<summary>⚠️ <b>M1. Stamp</b></summary>\n\n- x\n\n</details>\n\n<details>\n"
            "<summary>✅ <b>Pattern audit (a)–(f)</b></summary>\n\n- pass\n\n</details>\n\n"
            "### 📚 DDD compliance\n\n<details>\n<summary>➖ <b>Nothing found</b></summary>"
            "\n\n</details>\n"),
        "strengths": "- one\n- two\n- three",
    })
    values.update(overrides)
    return values


# ---- template and schema

def test_template_slots_match_schema():
    ids = re.findall(r"<!-- REVIEWER:([a-z_]+) \| ", TEMPLATE)
    assert len(ids) == len(set(ids))
    assert set(ids) == set(SCHEMA["required"]) == set(SCHEMA["properties"])
    assert SCHEMA["additionalProperties"] is False


def test_template_author_slots_are_exactly_the_documented_ones():
    found = set(re.findall(r"\{([a-z_]+)\}", TEMPLATE))
    assert found == AUTHOR_SLOTS | rt.DERIVED_SLOTS


def test_single_line_slots_are_the_ones_in_cells_and_summaries():
    inline = {i for line in TEMPLATE.splitlines() if not rt.REVIEWER.fullmatch(line.strip())
              for i in re.findall(r"<!-- REVIEWER:([a-z_]+) \| ", line)}
    with_pattern = {i for i, rule in SCHEMA["properties"].items() if "pattern" in rule}
    multiline = {"bottom_line", "findings", "strengths"}   # bottom_line follows its bold prefix
    assert inline - {"bottom_line"} == with_pattern == set(SCHEMA["required"]) - multiline


def test_reviewer_comments_are_single_line_and_rules_line_has_no_token():
    for line in TEMPLATE.splitlines():
        assert line.count("<!-- REVIEWER:") == line.count("-->")
    rules = next(ln for ln in TEMPLATE.splitlines() if ln.startswith("**Rules:**"))
    assert "<!--" not in rules


# ---- signals

def test_secret_scan_reports_line_numbers_not_text():
    text = "# Spec\n\nkey = " + FAKE_AWS_KEY + "\n"
    hits = rt.secret_hits(text)
    assert hits["AWS access key"] == [3]
    table, summary = rt.signals_table(hits)
    assert FAKE_AWS_KEY not in table and "❌ 1 line(s) at 3" in table and summary == "❌ secrets"


@pytest.mark.parametrize(("line", "check"), [
    ("-----BEGIN RSA " + "PRIVATE KEY-----", "Private key block"),
    ("conn = 'AccountKey=" + "A" * 86 + "=='", "Azure storage key"),
    ("OPENAI_API_KEY=sk-" + "a" * 32, "OpenAI-style API key"),
    ("token: ghp_" + "b" * 36, "GitHub token"),
    ('password = "' + "hunter2x" + '"', "Password assignment"),
    ("DB_PASSWORD=" + "supersecret", "Password assignment"),
])
def test_each_secret_check_fires(line, check):
    hits = rt.secret_hits("# Spec\n" + line + "\n")
    assert hits[check] == [2]
    assert [name for name, found in hits.items() if found] == [check]


@pytest.mark.parametrize("line", [
    'password = config("DB_PASSWORD")',
    "PASSWORD=${DB_PASS}",
    "pwd: <your-password>",
    "the password field is required",
    'password="x"',
])
def test_placeholders_and_prose_are_not_secrets(line):
    assert not any(rt.secret_hits(line).values())


def test_clean_spec_passes():
    table, summary = rt.signals_table(rt.secret_hits("# Spec\n\nnothing here\n"))
    assert table.count("✅") == len(rt.SECRET_CHECKS) and summary == "✅ pass"


def test_table_cells_never_carry_forbidden_characters():
    table, _ = rt.signals_table(rt.secret_hits("x\nk = " + FAKE_AWS_KEY + "\n"))
    rows = table.splitlines()[2:]
    assert len(rows) == len(rt.SECRET_CHECKS)
    for row in rows:
        cells = row.strip("|").split("|")
        assert len(cells) == 2 and all("<" not in c and "{" not in c for c in cells)


def test_signals_main_exit_codes(tmp_path, capsys):
    clean = tmp_path / "a.md"
    clean.write_text("# Spec\n\nfine\n", encoding="utf-8")
    assert rt.main(["signals", str(clean)]) == 0
    assert "✅" in capsys.readouterr().out
    secret = tmp_path / "b.md"
    secret.write_text("k = " + FAKE_AWS_KEY + "\n", encoding="utf-8")
    assert rt.main(["signals", str(secret)]) == 1
    captured = capsys.readouterr()
    assert FAKE_AWS_KEY not in captured.out + captured.err
    assert "{signals_scan}: ❌ secrets" in captured.out
    assert rt.main(["signals", str(tmp_path / "missing.md")]) == 2
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff\xfe not utf-8")
    assert rt.main(["signals", str(bad)]) == 2


# ---- lint

def test_lint_passes_full_and_targeted_authored_documents():
    assert rt.lint_authored(authored(), SCHEMA) == []
    targeted = authored(scope="Review these design elements: 4.2. Apply items 5, 8, 9 and 10.")
    assert rt.lint_authored(targeted, SCHEMA) == []


def test_lint_allows_late_slots_and_backticks_but_not_leftovers():
    late = TEMPLATE
    for slot in AUTHOR_SLOTS - {"reviewer_model", "reviewer_tool"}:
        late = late.replace("{" + slot + "}", "v")
    assert rt.lint_authored(late, SCHEMA) == []
    assert rt.lint_authored(authored(purpose="see `{spec_title}` in code"), SCHEMA) == []
    problems = rt.lint_authored(authored(purpose="{purpose}"), SCHEMA)
    line = next(n for n, ln in enumerate(TEMPLATE.splitlines(), 1) if "{purpose}" in ln)
    assert problems == [f"line {line}: author slot {{purpose}} not filled"]
    fenced = authored(history="```\nf'{name}'\n```")
    assert rt.lint_authored(fenced, SCHEMA) == []


def test_lint_rejects_multiline_comment_and_id_drift():
    broken = authored().replace("<!-- REVIEWER:strengths | three to six Markdown bullets -->",
                                "<!-- REVIEWER:strengths | three\nbullets -->")
    assert any("single" in p for p in rt.lint_authored(broken, SCHEMA))
    missing = authored().replace(
        "<!-- REVIEWER:files_read | the files you actually read, on one line -->", "x")
    assert any("files_read" in p for p in rt.lint_authored(missing, SCHEMA))


# ---- render

def test_render_fills_every_slot_and_derives_counts():
    out, problems = rt.render(authored(), fill(), SCHEMA)
    assert problems == []
    assert "<!-- REVIEWER" not in out and not re.search(r"\{[a-z_]+\}", out)
    assert "🛑 1 must-fix (HIGH) · ⚠️ 1 should-fix (MEDIUM) · 💡 0 suggestions (LOW)" in out
    assert "🚧 · 🛑 1 · ⚠️ 1 · 💡 0</summary>" in out
    assert "**Bottom line.** Holds up.\n\nOne gap." in out


def test_render_golden(tmp_path):
    out, _ = rt.render(authored(), fill(), SCHEMA)
    golden = Path(__file__).parent / "fixtures" / "review_tools" / "rendered.md"
    assert out == golden.read_text(encoding="utf-8")


@pytest.mark.parametrize(("change", "message"), [
    (lambda f: f.pop("strengths"), "missing"),
    (lambda f: f.update(extra="x"), "unknown"),
    (lambda f: f.update(signal="a|b"), "single"),
    (lambda f: f.update(files_read="a\nb"), "single"),
    (lambda f: f.update(rating="🚀 **Ready.**"), "rating"),
    (lambda f: f.update(findings=f["findings"].replace("H1.", "H3.")), "H1"),
    (lambda f: f.update(findings=f["findings"].replace("M1.", "H1.")), "duplicate"),
    (lambda f: f.update(findings=f["findings"].replace("⚠️ <b>M1", "🛑 <b>M1")), "icon"),
    (lambda f: f.update(findings=f["findings"].replace("H1.", "H1:")), "summary must read"),
    (lambda f: f.update(findings=f["findings"].replace("⚠️ <b>M1", "⚠ <b>M1")), "summary must read"),
    (lambda f: f.update(findings=f["findings"].replace("</details>", "", 1)), "balanced"),
    (lambda f: f.update(signal="🚀 ready"), "signal"),
    (lambda f: f.update(rating="🚧" + "x" * 200), "longer"),
    (lambda f: f.update(files_read="a\rb"), "schema pattern"),
    (lambda f: f.update(strengths="- ok <!-- REVIEWER:rating | x -->"), "HTML comments"),
    (lambda f: f.update(bottom_line="fine <SCRIPT>alert(1)</script>"), "HTML comments"),
])
def test_render_rejects_bad_fills(change, message):
    f = fill()
    change(f)
    _, problems = rt.render(authored(), f, SCHEMA)
    assert problems and any(message in p for p in problems), problems


def test_render_ignores_fenced_examples_and_unnumbered_blocks():
    f = fill()
    f["findings"] += "\n```markdown\n<summary>🛑 <b>H9. example</b></summary>\n```\n"
    out, problems = rt.render(authored(), f, SCHEMA)
    assert problems == [] and "🛑 1 must-fix" in out


def test_render_zero_findings():
    audit = ("### 🧩 Patterns\n\n<details>\n<summary>✅ <b>Pattern audit (a)–(f)</b></summary>"
             "\n\n</details>\n\n")
    ddd = ("### 📚 DDD compliance\n\n<details>\n<summary>➖ <b>Nothing found</b></summary>"
           "\n\n</details>\n")
    f = fill(rating="🚀 **Ready.**", signal="🚀 ready", findings=audit + ddd)
    out, problems = rt.render(authored(), f, SCHEMA)
    assert problems == []
    assert "🛑 0 must-fix (HIGH) · ⚠️ 0 should-fix (MEDIUM) · 💡 0 suggestions (LOW)" in out


def test_render_rejects_leftover_author_slot_but_allows_braces_in_answers():
    _, problems = rt.render(authored(stage="{stage}"), fill(), SCHEMA)
    assert any("{stage}" in p for p in problems)
    out, problems = rt.render(authored(), fill(strengths="- handles `{slot}` and {x} well"), SCHEMA)
    assert problems == [] and "{x} well" in out


def test_render_rating_icon_without_space_and_checkbox_selector():
    high = ("<details open>\n<summary>🛑 <b>H1. A gap</b></summary>\n\n- **Problem:** x\n\n"
            "</details>\n\n")
    f = fill(rating="☑️**Ready with notes.**", signal="☑️ ok")
    f["findings"] = f["findings"].replace(high, "")
    out, problems = rt.render(authored(), f, SCHEMA)
    assert problems == [] and "<code>[reviewer_model]</code> · ☑️ · 🛑 0" in out


def test_render_rejects_non_object_fill(tmp_path):
    _, problems = rt.render(authored(), ["x"], SCHEMA)
    assert problems == ["the answer is not a JSON object; Codex did not answer in shape"]


def test_render_preserves_crlf_and_missing_final_newline(tmp_path):
    src = authored().replace("\n", "\r\n").rstrip("\r\n")
    a = tmp_path / "a.md"
    a.write_bytes(src.encode("utf-8"))
    j = tmp_path / "f.json"
    j.write_text(json.dumps(fill()), encoding="utf-8")
    out = tmp_path / "r.md"
    assert rt.main(["render", str(a), str(j), "-o", str(out)]) == 0
    data = out.read_bytes()
    assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b"") and not data.endswith(b"\n")


def test_render_main_failure_keeps_inputs(tmp_path):
    a = tmp_path / "a.md"
    a.write_text(authored(), encoding="utf-8")
    j = tmp_path / "f.json"
    j.write_text("not json", encoding="utf-8")
    assert rt.main(["render", str(a), str(j), "-o", str(tmp_path / "r.md")]) == 1
    assert a.exists() and j.exists() and not (tmp_path / "r.md").exists()


def test_paths_for_rounds():
    first = rt.review_paths("spec-2025-01-22-1430.md", "")
    later = rt.review_paths("spec-2025-01-22-1430.md", "-v1.4")
    assert first["review"].name == "review-spec-2025-01-22-1430.md"
    assert later["review"].name == "review-spec-2025-01-22-1430-v1.4.md"
    assert later["log"].name == "codex-run-spec-2025-01-22-1430-v1.4.log"
    assert ".md.md" not in str(first["authored"]) and first["authored"].suffix == ".md"
    assert len({p for d in (first, later) for p in d.values()}) == 10
