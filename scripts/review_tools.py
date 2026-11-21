#!/usr/bin/env python3
"""
Script Name: review_tools.py
Purpose: Tools for the ai-peer-review skill's review document. `signals` runs a regex secret scan
         on a spec and prints the 🔐 table; `lint` checks the author's fill of review-template.md;
         `render` puts Codex's JSON answer into the document and derives the finding counts.
         Nothing here ever prints spec text: only check names and line numbers. Standard library only.

Usage:
    python3 scripts/review_tools.py signals temp/.planning/spec-X.md
    python3 scripts/review_tools.py lint temp/.planning/ai-peers/review-spec-X.authored.md
    python3 scripts/review_tools.py render AUTHORED.md FILL.json -o review-spec-X.md
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "ai-peer-review"
DEFAULT_SCHEMA = SKILL_DIR / "fill-schema.json"
AI_PEERS = Path("temp/.planning/ai-peers")
REVIEWER = re.compile(r"<!-- REVIEWER:([a-z_]+) \| [^\n]*? -->")
AUTHOR_SLOT = re.compile(r"\{([a-z_]+)\}")
CODE_SPAN = re.compile(r"`[^`\n]*`")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")       # a fenced code block opens or closes
FINDING_ID = re.compile(r"<summary>(🛑|⚠️|💡) <b>([HML])(\d+)\. ")
LOOSE_FINDING = re.compile(r"<summary>[^<\n]*?(?:🛑|⚠|💡|<b>[HML]\d+\b)")   # looks like a finding
ICON_FOR = {"H": "🛑", "M": "⚠️", "L": "💡"}
RATINGS = ("🚀", "☑️", "🚧", "⛔")
LATE_SLOTS = {"reviewer_model", "reviewer_tool"}        # filled after the Codex run
DERIVED_SLOTS = {"findings_counts", "summary_counts", "rating_icon"}
UNSAFE_IN_VALUE = re.compile(r"<!--|<script", re.IGNORECASE)   # the answer is data, never markup
FORBIDDEN_IN_CELL = str.maketrans({"|": "/", "<": "(", ">": ")", "{": "(", "}": ")"})

# Obvious credential shapes only. A clean result is not proof that the text holds no secret.
SECRET_CHECKS: dict[str, re.Pattern[str]] = {
    "Private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "Azure storage key": re.compile(r"AccountKey=[A-Za-z0-9+/]{40,}={0,2}"),
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Password assignment": re.compile(
        r"""(?i)(?<![a-z])(?:password|passwd|pwd)\w*["']?\s*[:=]\s*(?:"[^"\s]{6,}"|'[^'\s]{6,}'"""
        r"""|(?![<${(])[^\s"',;]{6,}\s*$)"""),
}


# ---- signals

def secret_hits(text: str) -> dict[str, list[int]]:
    """1-based line numbers per secret check. The matched text is never returned."""
    lines = text.split("\n")
    return {name: [n for n, line in enumerate(lines, 1) if rx.search(line)]
            for name, rx in SECRET_CHECKS.items()}


def signals_table(hits: dict[str, list[int]]) -> tuple[str, str]:
    """(Markdown table for {scan_table}, one-token summary for {signals_scan})."""
    rows = [(name, "✅ None" if not found
             else f"❌ {len(found)} line(s) at " + ", ".join(map(str, found)))
            for name, found in hits.items()]
    table = "| Check | Result |\n|---|---|\n" + "\n".join(
        f"| {c} | {r.translate(FORBIDDEN_IN_CELL)} |" for c, r in rows)
    summary = "❌ secrets" if any(hits.values()) else "✅ pass"
    return table, summary


# ---- lint

def _prose_lines(text: str) -> list[tuple[int, str]]:
    """(line number, line) outside code fences; closers carry no info string."""
    out: list[tuple[int, str]] = []
    fence: str | None = None
    for n, line in enumerate(text.split("\n"), 1):
        opener = FENCE.match(line)
        if fence is not None:
            if (opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence)
                    and not line.strip()[len(opener.group(1)):].strip()):
                fence = None
            continue
        if opener:
            fence = opener.group(1)
            continue
        out.append((n, line))
    return out


def _leftover_slots(text: str, allowed: set[str]) -> list[str]:
    problems = []
    for n, line in _prose_lines(text):
        for slot in AUTHOR_SLOT.findall(CODE_SPAN.sub("", line)):
            if slot not in allowed:
                problems.append(f"line {n}: author slot {{{slot}}} not filled")
    return problems


def lint_authored(text: str, schema: dict[str, Any]) -> list[str]:
    """The author's document before launch: slots filled, reviewer comments intact."""
    problems = _leftover_slots(text, LATE_SLOTS | DERIVED_SLOTS)
    for n, line in enumerate(text.split("\n"), 1):
        if line.count("<!-- REVIEWER:") != len(REVIEWER.findall(line)):
            problems.append(f"line {n}: reviewer comment is not single-line")
    ids = REVIEWER.findall(text)
    if len(ids) != len(set(ids)):
        problems.append("duplicate reviewer slot id")
    if set(ids) != set(schema["required"]):
        problems.append("reviewer slot ids differ from fill-schema.json: "
                        + ", ".join(sorted(set(ids) ^ set(schema["required"]))))
    return problems


# ---- render

def finding_ids(findings: str) -> tuple[dict[str, list[int]], list[str]]:
    """Ids per severity letter from the summary lines, fenced examples skipped.

    A summary that looks like a finding but is not in the exact form is an error, never a
    silent zero: the derived counts and the rating rule depend on every finding being seen.
    """
    found: dict[str, list[int]] = {"H": [], "M": [], "L": []}
    problems: list[str] = []
    for n, line in _prose_lines(findings):
        strict = FINDING_ID.findall(line)
        if LOOSE_FINDING.search(line) and not strict:
            problems.append(f"findings line {n}: summary must read "
                            "'<summary>🛑 <b>H1. Title</b></summary>' (icon, letter, number, dot)")
        for icon, letter, num in strict:
            if ICON_FOR[letter] != icon:
                problems.append(f"finding {letter}{num}: icon {icon} does not match severity")
            found[letter].append(int(num))
    for letter, nums in found.items():
        if len(nums) != len(set(nums)):
            problems.append(f"duplicate finding id in {letter}")
        elif sorted(nums) != list(range(1, len(nums) + 1)):
            problems.append(f"{letter} ids must run from {letter}1 without gaps: "
                            + ", ".join(f"{letter}{n}" for n in sorted(nums)))
    if findings.count("<details") != findings.count("</details>"):
        problems.append("findings: <details> and </details> are not balanced")
    return found, problems


def render(authored: str, fill: object, schema: dict[str, Any]) -> tuple[str, list[str]]:
    """Replace each reviewer comment with its answer and fill the derived cells."""
    if not isinstance(fill, dict):
        return "", ["the answer is not a JSON object; Codex did not answer in shape"]
    problems: list[str] = []
    props: dict[str, dict[str, Any]] = schema["properties"]
    if missing := set(schema["required"]) - set(fill):
        problems.append("missing answers: " + ", ".join(sorted(missing)))
    if unknown := set(fill) - set(props):
        problems.append("unknown answers: " + ", ".join(sorted(unknown)))
    for slot, value in fill.items():
        rule = props.get(slot, {})
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{slot}: empty or not a string")
        elif UNSAFE_IN_VALUE.search(value):
            problems.append(f"{slot}: HTML comments and script tags are not allowed")
        elif "pattern" in rule and not re.fullmatch(rule["pattern"], value):
            problems.append(f"{slot}: must be single-line without | (schema pattern)")
        elif len(value) > rule.get("maxLength", len(value)):
            problems.append(f"{slot}: longer than {rule['maxLength']} characters")
    if problems:
        return "", problems
    ids, id_problems = finding_ids(fill["findings"])
    problems += id_problems
    rating_icon = next((r for r in RATINGS if fill["rating"].startswith(r)), None)
    if rating_icon is None:
        problems.append("rating must start with 🚀, ☑️, 🚧 or ⛔")
    elif ids["H"] and rating_icon in ("🚀", "☑️"):
        problems.append("rating cannot be 🚀 or ☑️ with a HIGH finding")
    if rating_icon and not fill["signal"].startswith(rating_icon):
        problems.append("signal must start with the same icon as rating")
    counts = {k: len(v) for k, v in ids.items()}
    derived = {
        "findings_counts": (f"🛑 {counts['H']} must-fix (HIGH) · ⚠️ {counts['M']} should-fix"
                            f" (MEDIUM) · 💡 {counts['L']} suggestions (LOW)"),
        "summary_counts": f"🛑 {counts['H']} · ⚠️ {counts['M']} · 💡 {counts['L']}",
        "rating_icon": rating_icon or "",
    }
    problems += _leftover_slots(authored, DERIVED_SLOTS)     # late slots must be filled by now
    eol = "\r\n" if "\r\n" in authored else "\n"
    out = REVIEWER.sub(lambda m: fill[m.group(1)].strip().replace("\r\n", "\n").replace("\n", eol),
                       authored)
    for slot, value in derived.items():
        out = out.replace("{" + slot + "}", value)
    return out, problems


def review_paths(spec_filename: str, round_suffix: str = "") -> dict[str, Path]:
    """The five per-round files, named once."""
    stem = spec_filename.removesuffix(".md") + round_suffix
    return {"review": AI_PEERS / f"review-{stem}.md",
            "authored": AI_PEERS / f"review-{stem}.authored.md",
            "fill": AI_PEERS / f"review-{stem}.fill.json",
            "log": AI_PEERS / f"codex-run-{stem}.log",
            "pid": AI_PEERS / f"codex-run-{stem}.pid"}


# ---- CLI

def _read(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_signals = sub.add_parser("signals", help="regex secret scan on a spec")
    p_signals.add_argument("spec", type=Path)
    p_lint = sub.add_parser("lint", help="check the authored review document before launch")
    p_lint.add_argument("authored", type=Path)
    p_render = sub.add_parser("render", help="render Codex's JSON answer into the document")
    p_render.add_argument("authored", type=Path)
    p_render.add_argument("fill", type=Path)
    p_render.add_argument("-o", "--output", type=Path, required=True)
    for p in (p_lint, p_render):
        p.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        if args.command == "signals":
            text = _read(args.spec)
            table, summary = signals_table(secret_hits(text))
            print(table)
            print(f"\n{{signals_scan}}: {summary}")
            return 1 if summary.startswith("❌") else 0
        schema = json.loads(_read(args.schema))
        if args.command == "lint":
            problems = lint_authored(_read(args.authored), schema)
        else:
            try:
                fill = json.loads(_read(args.fill))
            except json.JSONDecodeError as exc:
                problems = [f"{args.fill}: not JSON ({exc.msg}); Codex did not answer in shape"]
            else:
                out, problems = render(_read(args.authored), fill, schema)
                if not problems:
                    try:
                        args.output.write_bytes(out.encode("utf-8"))
                    except OSError as exc:
                        logger.error("cannot write %s: %s", args.output, exc)
                        return 2
                    logger.info("rendered %s", args.output)
    except (OSError, ValueError) as exc:         # unreadable file, or not UTF-8 / not JSON schema
        logger.error("cannot read input: %s", exc)
        return 2
    for problem in problems:
        logger.error(problem)
    if problems:
        return 1
    logger.info("%s: ok", args.command)
    return 0


if __name__ == "__main__":
    sys.exit(main())
