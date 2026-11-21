# Design Specification Standards and Safety Protocol

## Overview
This document establishes mandatory standards for creating design specifications before any Standard or Critical implementation work. These rules exist to prevent production disasters caused by incomplete design analysis.

---

## CRITICAL: Choose the Review Tier Before Implementation

**MANDATORY RULE**: Choose the review tier first. For a Standard or Critical change, before making ANY file or code changes:

1. **MUST create a specification document** in `temp/.planning/spec-{YYYY-MM-DD-HHMM}.md`
2. **MUST complete all safety checks** defined in this document
3. **MUST run QC review** using the quality-control-enforcer agent
4. **MUST get user approval** before proceeding to implementation

**Forbidden Actions**:
- ❌ Starting a Standard or Critical implementation without its approved spec
- ❌ Making a Standard or Critical change without its spec
- ❌ Choosing a lower tier than the Critical paths, the size limit or an unclear scope allow
- ❌ Writing code before completing safety analysis (Standard and Critical)

### Review Tiers

#### Tiers

| | Trivial | Standard | Critical |
|---|---|---|---|
| **Spec** | None | Six sections: Original Request, Executive Summary, Technical Specification (stamped), Breaking Change Analysis (one line allowed), Files to be Modified, Testing Checklist | All ten sections |
| **Review step** | None before implementation | Quick QC, then targeted Codex review of `[NOVEL]` elements (design-spec skill, Quick QC Review) | Long Review |
| **Approval** | n/a | The shared Approval step | The shared Approval step |

**Trivial** covers:

- documentation;
- comments;
- log message text;
- formatting or lint fixes;
- tests that add or strengthen checks;
- a one-line fix whose cause and correction are both obvious.

Excluded from Trivial:

- removing or weakening a test assertion, which is at least Standard;
- the project's pattern library (`docs/PatternsLibrary.md`) and `docs/.planning/**`;
- any change that touches a Critical path.

#### Tier selection

**Critical paths.** Each project lists its critical paths in its AGENTS.md (or CLAUDE.md). A change is Critical when it touches any of them. The list should cover these categories:

1. **Configuration and supply chain**: CI workflows, dependency manifests and lock files, `.env*` files, and tool or agent server configuration.
2. **Agent instructions and tooling**: agent configuration (`.claude/**`, `.codex/**`, `.agents/**`), `CLAUDE.md`, `AGENTS.md`, and build or release scripts.
3. **Public interfaces**: CLI commands and flags, API endpoints and schemas, and configuration file schemas.
4. **The project's core modules**, as the project names them.
5. **Sensitive runtime behaviour**, wherever it lives:
   - code that handles untrusted input (request bodies, uploaded files, configuration, environment);
   - code that handles secrets;
   - code that runs subprocess or shell calls;
   - code that writes files at runtime.
6. **Domains**: a secure domain or bounded context in a domain model, when the project has one.
7. **Size and scope** (these apply even when the project lists nothing):
   - more than 5 changed files, or more than 200 added plus deleted lines;
   - an external service integration;
   - a data migration;
   - anything the user calls critical.

If the project has no list, treat categories 1, 2, 3, 5 and 7 as its critical paths.

**Counting size.** Count files and lines in the intended change (Lifecycle and floor), not in the process artifacts it produces.

- Not counted: `docs/.planning/**`, `temp/**`, lock files, binary files, and a pattern-library row added by a promotion.
- A rename counts as one file. Its old and new paths are both checked against the Critical paths.
- Tests count.

**The whole change counts.** The tier is judged on the whole intended change, not per commit or per file. Splitting a change into pieces does not lower its tier.

**Procedure.**

1. Before writing anything, the agent lists the files it expects to change and states the tier with a one-line reason. A Critical path or a size over the limit makes the tier Critical. If the agent cannot tell, the tier is Critical.
2. The user may raise the tier at any time.
3. **Lowering.** The user may lower Critical to Standard, and only by naming the scope.
   - The spec header records it, for example `**Tier**: Standard (lowered from Critical by the user for: scripts/foo.py; reason: <reason>)`.
   - The lowering covers only the named paths or criteria.
   - Later checks escalate only on Critical matches outside that scope.
   - A general instruction such as "just do it quickly" lowers nothing. The agent never proposes lowering. Nothing lowers a change to Trivial.
4. **Escalation.** If a change needs more than its tier allows, the agent stops and raises the tier.
   - **A Trivial change** that turns out to need more gets its spec written before the work continues.
   - **A Standard spec** whose review finds an unscoped Critical path is rewritten to ten sections and starts Long Review at Step 1. An earlier QC counts only for the version it reviewed.
   - **Code already written** stays uncommitted until the higher tier's review is approved.
5. **Updates after approval.**
   - **A material update** is any change to the design: the Technical Specification, the files, or the behaviour. It repeats tier selection over behaviour and scope, resets the status to `Design Review`, and needs that tier's review and a fresh approval before implementation continues.
   - **An editorial update** (typos, line references, wording that changes no design) keeps the approval and is recorded as an editorial row in the version history.
   - **A spec approved before this rule** gets its tier chosen on its next material update. Old specs are not retrofitted.

**Header field.** Standard and Critical specs carry `**Tier**:` before `**Status**:` on the header's third line.

#### Lifecycle and floor

1. **Choose the tier** (Tier selection, procedure 1).
2. **Write the spec** for Standard and Critical.
3. **Review**: the tier's procedure. None for Trivial, Quick QC plus targeted Codex for Standard, Long Review for Critical.
4. **Approve**: the shared Approval step, for Standard and Critical.
5. **Implement.**
6. **Floor**: the checks below, which no tier and no lowering can remove.
7. **Commit**: only at the user's request.

**The floor** runs after implementation and again after any later edit before the commit.

1. **Tier audit.** The intended change is everything in the working tree that differs from the merge base with `main`, plus untracked files.

   ```bash
   BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD origin/main)
   git diff -M --name-status "$BASE"; git ls-files --others --exclude-standard   # files, both rename paths
   git diff -M --numstat "$BASE"                                                  # added and deleted lines
   git ls-files --others --exclude-standard -z | xargs -0 -I{} git diff --no-index --numstat /dev/null {}   # lines in untracked files
   git status --porcelain --ignored -- '.env*'                                    # ignored .env files are Critical too
   ```

   - Compare the result with the Critical paths, outside any scope the user lowered, and with the size limit.
   - QC then reads the changed content for the semantic criteria (Critical path 5) and compares it with the spec's Files to be Modified. It reports any file the spec did not declare.
   - A match escalates under Tier selection, procedure 4.
   - Record the result as a `tier audit` row in the version history, or in the commit message for a Trivial change.
2. **Tests, lint and types.** When the change touches code, tests, scripts, workflows or configuration, the project's own test, lint and type commands (named in its AGENTS.md or CLAUDE.md) pass.
3. **The project's quality gate, if it has one,** on the same intended change.
   - **A blocker or a failed gate** stops the commit.
   - **An error** stops the commit until it is resolved.
   - **A check that could not run** (for example, a missing credential) is reported as "not run", never as passed.
4. **No change to a path the project marks as protected without the user's approval.**
5. **QC after implementation** (`quality-control-enforcer`) on the intended change.

**One severity policy.** At every review point, CRITICAL, HIGH and MEDIUM findings are fixed, or the user records a decision not to act on them. LOW findings are fixed or answered.

#### Review timing

- **Version history columns**: `| Version | Timestamp | Stage | Findings | Change |`.
  - **Every stage appends a row**, including the first pass of each. The stages are draft, code-reference check, QC, peer review, approval, editorial, tier audit and implementation.
  - **Findings** take the form `0 critical / 2 high / 6 medium / 1 low`, or "n/a".
- **Status line**: `Implementation Complete on {Month D, YYYY HH:MM}`, in the same form as approval. The agent writes it just before the implementation commit, so the time is approximate.
- **Elapsed time** is wall-clock time, nights and waiting included. It runs from the HHMM in the spec filename to the approval timestamp to the Implementation Complete timestamp.
  - It measures how long a spec takes end to end. It does not measure human effort.
  - Review rounds and finding counts come from the rows.
- **Greenfield Rewrite** keeps every history row and its timestamp. It consolidates the prose only.

---

## Spec Creation Workflow

### 1. Initial Spec Creation

**Location**: `temp/.planning/spec-{YYYY-MM-DD-HHMM}.md`

**Timing**: BEFORE making ANY file or code changes for a Standard or Critical change

**Example**: `temp/.planning/spec-2025-01-22-1430.md`

### 2. Workflow Sequence

```
User Request → Choose Tier → Analyze Codebase → Create Spec → Run QC Review → User Approval → Begin Implementation
```

**CRITICAL**: The spec document is created BEFORE implementation, not during or after.

### 3. Spec File Naming Convention

- **Format**: `spec-YYYY-MM-DD-HHMM.md`
- **Time Format**: 24-hour with leading zeros
- **Examples**:
  - `spec-2025-01-22-0930.md` (9:30 AM)
  - `spec-2025-01-22-1445.md` (2:45 PM)
  - `spec-2025-01-22-2130.md` (9:30 PM)

### 4. CLI Output Requirement

**After creating spec, ALWAYS output clickable link**:

```
Specification: temp/.planning/spec-YYYY-MM-DD-HHMM.md
```

This provides immediate access for user review.

---

## Required Spec Document Structure

### Header Format (MANDATORY)

Three lines, so the first screen of a spec is the Original Request:

```markdown
# [Feature Name] Specification
Date: YYYY-MM-DD · **Last Updated**: YYYY-MM-DD HH:MM · **Version**: vX.Y · <Author> with Claude Code AI Assistant
**Tier**: Standard | Critical · **Status**: Design Review · **Reviews**: 🤖 QC n · 🧠 Codex n · **Issue**: none yet
```

- `Date:` opens its line (the Pattern Stamping applicability test reads it) and never changes.
- `**Version**` is the version in the last row of the Spec Version History. `**Reviews**` counts that table's QC and peer-review rows. Both are derived at every edit, never typed independently.
- `**Issue**` is `none yet` until `/add-issue` fills it with `[#NNN](url)`.

### Status Field Rules

- **Initial Status**: Always "Design Review" when first created
- **Keep as "Design Review"** until user explicitly approves ("OK implement", "looks good", etc.)
- **After Approval**: Change to "Design Approved for Implementation on {Date/Time}"
- **Example**: "Design Approved for Implementation on November 13, 2025 14:30"

### Last Updated Field Rules

- **Format**: `YYYY-MM-DD HH:MM` (24-hour)
- **When to update**: Every time the spec is edited
- **Source**: Use filesystem modified time after saving: `date -r "path/to/spec.md" "+%Y-%m-%d %H:%M"` (works on macOS and Linux)
- **Position**: On the header's second line, after `Date:`

### Required Sections

Standard specs need Original Request, Executive Summary, Technical Specification, Breaking Change Analysis (one line allowed), Files to be Modified and Testing Checklist. Critical specs need all ten.

1. **Original Request** (at the front)
   - The exact user prompt/request that initiated the design
   - Provides context for future reference

2. **Executive Summary**
   - Brief overview of changes
   - Problem being solved
   - Proposed solution approach
   - Impact assessment

3. **Current State Analysis**
   - Existing architecture
   - Current code behavior
   - Known limitations/issues
   - Evidence of problems (screenshots, logs, test results)

4. **Technical Specification**
   - Detailed design of solution
   - Architecture diagrams if needed
   - Data model changes
   - API changes
   - Algorithm descriptions
   - **A pattern stamp opening every `###` design element** (see "Pattern Stamping")

5. **Breaking Change Analysis** (see Architectural Safety Protocol below)
   - All files affected by changes
   - What will break in each file
   - Required fixes for each break

6. **Files to be Modified**
   - Complete list with line numbers
   - Categorized by priority (must/should/optional)
   - Actual code changes (not pseudocode)

7. **Testing Checklist**
   - Unit tests required
   - Integration tests required
   - Edge cases to verify
   - Performance tests if applicable

8. **Rollback Plan**
   - How to undo changes if issues arise
   - Data migration reversal steps
   - Backup/restore procedures

9. **Success Criteria**
   - Measurable outcomes
   - Acceptance criteria
   - Performance benchmarks

10. **Codebase Analysis** (at the end)
    - List of ALL files read during analysis
    - Key findings from each file
    - Evidence supporting design decisions

---

## Pattern Stamping (MANDATORY)

Library: the pattern library (the project's `docs/PatternsLibrary.md` if it exists, otherwise `~/.devmethodology/patterns/PatternsLibrary.md`). Read it before writing Technical Specification; never @-include it.
Every design element in Technical Specification opens with `[PATTERN: <name>]` from the library, or
`[NOVEL] — why no library pattern fits: <reason>`. QC applies the grammar, name and mechanism checks below by reading the spec and the library.

**Applicability.** The rule applies to every spec. A project that adopts it part-way through may name a cutoff date in its AGENTS.md; then the rule applies to specs whose header line starting `Date:` has `YYYY-MM-DD` as its first token (the rest of that line is ignored) on or after that date.
- If the `Date:` line is missing or malformed, the spec is **not** exempt, and the missing date is itself a HIGH finding.
- Exempt specs stay exempt when they are later updated.

**Markdown dialect.**
- Only ATX headings count: one to six `#` followed by a space. Specs do not use setext headings.
- A fence opens with up to three spaces of indentation, then three or more backticks or tildes. It closes at a line with the same character repeated at least as many times.
- Everything inside a fence is ignored. Fences do not nest.

**Section.** Exactly one `##` heading outside fences must match `^## (\d+\. )?Technical Specification\s*$`.
- If none matches, or more than one does, that is a structural error (HIGH).
- The section ends at the next `#` or `##` heading outside a fence.

**Elements.**
- Each `###` heading in the section starts a design element. The element ends at the next `###`, `##` or `#` heading.
- `####` and deeper headings inherit their element's stamp.
- A `####` that appears before the first `###` is a structural error.
- Only design decisions get a `###`. Descriptive material goes as `####` under the design it explains, or outside the section, e.g. in Files to be Modified. Descriptive material means file lists, edits to other files, execution walkthroughs, limits and configuration listings.
- A `###` that mixes two independent designs must be split.
- If the section has no `###` heading, the whole section is one element, and its `####` headings belong to it (the structural error above needs a later `###`).

**Preamble.** Content between the section heading and the first `###` is preamble. It needs no stamp, and it may only introduce or orient the reader. If QC finds a design decision in the preamble, it treats that as a missing stamp (HIGH).

**Stamp location.** The stamp is the first block after the element's heading, skipping blank lines. In a section with no `###`, it is the first block after the section heading. A block is a run of consecutive non-blank lines, joined with single spaces.
- If that first block is a heading, fence, list, table or blockquote, the stamp is missing.
- The **whole** joined block must match `STAMP` below, anchored at both ends.

```text
STAMP    := PATTERN | NOVEL
PATTERN  := "[PATTERN:" WS* NAME ( WS* "," WS* NAME )* WS* "]" ( SEP TEXT )?
NOVEL    := "[NOVEL]" SEP SENTINEL WS+ TEXT
SENTINEL := "why no library pattern fits:"        (case-insensitive)
SEP      := WS+ ( "—" | "–" | "--" | "-" ) WS+
WS       := " " | TAB                             (line breaks are already joined to " ")
NAME     := 1+ characters other than "," "[" "]", not all whitespace; trimmed before matching
TEXT     := 1+ characters including at least one non-whitespace character,
            and not containing "[PATTERN:" or "[NOVEL]"
```

- A `[NOVEL]` stamp needs both a `SEP` and the `SENTINEL`.
- Authors write the em dash `—`, but checkers accept any `SEP`.

**Name matching.** Each `NAME` must equal a Pattern or Alias after normalisation:
1. Unicode NFKC and casefold.
2. Replace each of `-` `–` `—` `_` `/` with a space.
3. Collapse whitespace.
4. Trim.


**Expected outcomes** (reference cases for reviewers):

| Input stamp block | Outcome |
|---|---|
| `[PATTERN: Retry] — bounded backoff on idempotent reads` | valid |
| `[PATTERN: Retry, Circuit Breaker, Timeout]` | valid |
| `[PATTERN: dead-letter channel]` | valid (resolves to AZ-34 by alias) |
| `[PATTERN: Retry] - x` and `[PATTERN: Retry] -- x` | valid |
| `[NOVEL] — why no library pattern fits: closest is Gatekeeper, but …` (wrapped over 3 lines) | valid |
| `[PATTERN: Retry] trailing prose` | **invalid**: text without `SEP` |
| `[PATTERN: Retry] —` | **invalid**: empty `TEXT` |
| `[NOVEL]` | **invalid**: no `SEP` or sentinel (HIGH) |
| `[NOVEL] why no library pattern fits: x` | **invalid**: no `SEP` |
| `[NOVEL] — because` | **invalid**: no sentinel |
| `[PATTERN: N/A]`, `[PATTERN: Transactional Inbox]` | **invalid**: unresolvable name |
| `[PATTERN: Message]` | **invalid**: not stampable |
| `[PATTERN: Retry] — x [NOVEL] — why no library pattern fits: y` | **invalid**: two stamps |
| Prose paragraph, then a stamp | **invalid**: stamp missing (first block is not a stamp) |
| `### X` inside a ``` fence | ignored |

**Semantic rules** (judged by QC and peer review):

1. **Mechanism, not topic.** The element must contain the row's Core mechanism. Where the mechanism is not obvious from the element's first paragraph, the stamp's `TEXT` should say how the element realises it.

2. **Variants.** `TEXT` may narrow the pattern. If the change removes the core mechanism, the element is `[NOVEL]`.

3. **Combinations.** List several names, primary first, only when the element implements each one.

4. **NOVEL reasons.** A reason names the closest library pattern and says why that pattern's mechanism does not apply. The one exception is a reason that says why the problem lies outside every catalog.

5. **Historical judgments.** Stamps are judged against the library as it stood when the element was last stamped. A later review re-judges only the elements that the current revision adds or changes. A row added after an element was stamped never turns that unchanged element's `[NOVEL]` into a "missed match".

Example:

```markdown
### 4.3 Order event publishing

[PATTERN: Transactional Outbox] — outbox row written in the same SQLite transaction as the order.
```

### Review checks

Claude QC applies these as its "Pattern stamps" review dimension (design-spec skill, Long Review Step 3 and Quick QC step 2, and the QC Review Process prompt below); Codex applies them via the ai-peer-review instructions.

> (a) the spec's `Date:` makes it applicable (missing date = applicable and HIGH); exactly one Technical Specification section; no `####` before the first `###`; no design decision in the preamble;
> (b) every element's first block is a stamp that matches the grammar;
> (c) every name resolves in the pattern library, and the element contains that row's Core mechanism;
> (d) every `[NOVEL]` names the closest pattern and why its mechanism does not apply, and no library pattern was missed (check the Ref / See also of near matches). Apply this only to elements added or changed in this revision (Semantic rule 5, Historical judgments);
> (e) each `[NOVEL]` element gets extra failure-mode scrutiny;
> (f) report `NOVEL: n of m elements` on the first line of QC Review Results.
>
> **Severity.** HIGH: (a) or (b) failure, or an unresolvable or not-stampable name. MEDIUM: a misapplied pattern (mechanism missing), a missed match, or a weak NOVEL reason.

---

## One-Shot Editing for Specs

When updating spec files in `temp/.planning/`:

**Best Practice**: Read once, modify in memory, write once

```python
# ✅ Good: One confirmation dialog
content = read(spec_file)
content = update_all_changes(content)
write(spec_file, content)

# ❌ Avoid: Multiple confirmation dialogs
edit(spec_file, "5 min" -> "30 min")      # Dialog 1
edit(spec_file, "5 minutes" -> "30 minutes")  # Dialog 2
edit(spec_file, "faster" -> "consistent")    # Dialog 3
```

**Why**: Minimizes user interruption while allowing review of all changes at once.

---

## Architectural Change Safety Protocol

### When This Protocol Applies

**MANDATORY** for specifications that modify:
- Core data models or relationships
- Database schema or foreign keys
- API contracts or endpoints
- External service integrations (payment providers, messaging APIs, etc.)
- Authentication/authorization flows
- Payment processing logic
- Webhook handlers
- Background job processing

The examples below use one running case from an ordering system: orders are moving from being billed to the user who placed them (`Order.customer_id`) to being billed to a company account (`Order.billing_account_id`).

### 1. Dependency Impact Analysis (REQUIRED)

**Before claiming any code "needs no changes"**, you MUST:

```bash
# Find ALL references to fields, models and functions being changed
grep -rn "customer_id" --include="*.py"
grep -rn "Order.objects" --include="*.py"
grep -rn "charge_order" --include="*.py"
```

**Spec Format (MANDATORY)**:

```markdown
## Breaking Change Analysis

### Field Changed: `Order.customer_id` → `Order.billing_account_id`

**Files Referencing This Field** (verified via grep):

1. ❌ `billing/services/charge_service.py:76`
   - **Current Code**: `payer = payments_client.get_or_create_payer(order.customer)`
   - **What Breaks**: Charges the user who placed the order instead of the account
   - **Required Fix**: [Show actual code changes]

2. ❌ `billing/webhooks.py:179`
   - **Current Code**: `order = Order.objects.get(customer__payer_ref=event["payer_ref"])`
   - **What Breaks**: Lookup fails, because the payer reference now belongs to the account
   - **Required Fix**: [Show actual code changes]

3. ✅ `billing/services/invoice_service.py:248`
   - **Current Code**: `line = {"payer_ref": charge.payer_ref, "amount": charge.amount}`
   - **Why OK**: Reads the payer from the charge record, which the provider sets per charge
   - **Verification**: Tested against the provider's sandbox ✓
```

**Rules**:
- ✅ = Truly safe (show evidence)
- ❌ = Will break (show exact breaking line + required fix)
- Never claim ✅ without reading the actual file

### 2. Execution Path Verification (REQUIRED)

**Must trace end-to-end for these critical paths**:

1. **Order placement** (from user click → payment provider API → database save)
2. **Webhook processing** (from payment provider → handler → database update)
3. **Dashboard display** (from user request → query → render)
4. **Payment processing** (from charge → success/failure → notification)
5. **Background jobs** (cron tasks, queue processors)

**Spec Format (MANDATORY)**:

````markdown
## Execution Path Verification

### Path: Order Placement

**Step 1**: User submits the order - `orders/views.py:212`
```python
# ACTUAL CODE (verified by reading file):
customer = get_customer_for_request(request)
order, client_token = order_service.place_order(customer=customer, cart=cart)
```

**Step 2**: Charge the payer - `billing/services/charge_service.py:75`
```python
# ACTUAL CODE (verified by reading file):
payer = payments_client.get_or_create_payer(customer)
charge = payments_client.create_charge(payer_ref=payer.ref, amount=order.total)
```

**What Breaks With Proposed Changes**:
- Step 2 charges the wrong payer (the user, not the billing account)
- Account-level invoices stay empty

**Required Fix**:
```python
# billing/services/charge_service.py:75-110
def charge_order(order: Order, account: BillingAccount) -> Charge:
    with transaction.atomic():
        account = BillingAccount.objects.select_for_update().get(id=account.id)
        if not account.payer_ref:
            # [Show complete implementation with error handling]
            ...
```
````

**Rules**:
- Show ACTUAL code from files (not pseudocode)
- Include file paths and line numbers
- Trace ALL steps from user action to completion
- Show what breaks at each step

### 3. Never Use Pseudocode For Critical Flows (REQUIRED)

**FORBIDDEN in specs**:

```python
# ❌ FORBIDDEN: Pseudocode for critical implementation
def charge_order(order, account):
    # 1. Get or create the account's payer
    # 2. Charge it
    # 3. Save the charge
```

**REQUIRED in specs**:

```python
# ✅ REQUIRED: Actual code changes with error handling
def charge_order(order: Order, account: BillingAccount) -> Charge:
    """
    Charge an order to its billing account.

    Changes from current implementation:
    - Charges the account's payer, not the user who placed the order
    - Creates the payer once, under a row lock
    - Uses an idempotency key so a retried request cannot charge twice
    """
    # NEW: get or create the account's payer under a row lock
    with transaction.atomic():
        account = BillingAccount.objects.select_for_update().get(id=account.id)
        if not account.payer_ref:
            try:
                payer = payments_client.create_payer(
                    email=account.billing_email, metadata={"account_id": account.id})
            except PaymentsError as e:
                logger.error("Payer creation failed for account %s: %s", account.id, e)
                raise
            account.payer_ref = payer.ref
            account.save(update_fields=["payer_ref"])

    if order.total <= 0:
        raise ValueError(f"Order {order.id} has no amount to charge")

    # CHANGED: charge the account's payer (was: the customer's payer)
    try:
        charge = payments_client.create_charge(
            payer_ref=account.payer_ref,
            amount=order.total,
            currency=order.currency,
            idempotency_key=f"order-{order.id}",
        )
    except PaymentsRateLimited:
        raise  # the caller's retry wrapper handles backoff
    except PaymentsError as e:
        logger.error("Charge failed for order %s: %s", order.id, e)
        order.mark_payment_failed(reason=str(e))
        raise

    Charge.objects.create(order=order, provider_ref=charge.ref, amount=charge.amount)
    return charge
```

**Why This Is Required**:
- Pseudocode hides complexity and edge cases
- Actual code reveals error handling needs
- Shows concurrency controls (select_for_update)
- Documents exact API calls and parameters
- Exposes validation requirements
- Makes implementation complexity obvious

### 4. Breaking Change Checklist (MUST COMPLETE)

Every architectural spec MUST include and verify:

```markdown
## Breaking Change Checklist

**Database & Queries**:
- [ ] Searched for all reads by changed fields (ORM lookups, filters): `grep -rn "Order.objects" --include="*.py"`
- [ ] Verified all raw SQL queries: `grep -rn "SELECT.*orders" --include="*.py"`
- [ ] Checked reverse-relation and related-name usage

**Model Relationships**:
- [ ] Checked all models with a foreign key to the changed model
- [ ] Verified reverse relationship queries
- [ ] Checked many-to-many and one-to-one relationships

**API & External Interfaces**:
- [ ] Listed all API endpoints returning changed data structure
- [ ] Checked API serializers for changed fields
- [ ] Verified external API assumptions (payment provider, messaging APIs, etc.)
- [ ] Checked webhook payload structures

**Admin and Back-Office Tools**:
- [ ] Checked admin screens, filters, search and custom actions for changed models

**Background Processing**:
- [ ] Searched for scripts and management commands using changed fields
- [ ] Checked cron tasks, queue processors and scheduled jobs

**Webhooks & Event Handlers**:
- [ ] Verified all webhook and event handlers referencing changed fields
- [ ] Checked signal or hook handlers

**Concurrent Operations**:
- [ ] Identified race conditions with new code
- [ ] Added database-level locking where needed (select_for_update)
- [ ] Verified idempotency for retry scenarios
- [ ] Checked for duplicate creation possibilities

**Migration Safety**:
- [ ] Verified partial migration failures can be recovered
- [ ] Added transaction boundaries for data changes
- [ ] Implemented rollback procedures
- [ ] Added migration checkpointing for long-running migrations

**Testing**:
- [ ] Identified all test files needing updates
- [ ] Listed new test scenarios required
- [ ] Verified test fixtures need updating
```

**Rules**:
- Must check EVERY box
- Must show grep commands used
- Must list specific files found
- Cannot skip boxes as "not applicable" without justification

### 5. Evidence-Based Claims Only (REQUIRED)

**FORBIDDEN Patterns**:

❌ "NO CHANGES NEEDED" without showing actual code
❌ "Will automatically work" without tracing execution path
❌ "Simple 3-step process" that hides 10+ edge cases
❌ "OR consolidate the invoices somehow" (hand-waving critical decisions)
❌ Any claim about code behavior without reading the actual file
❌ "Should work" or "Probably works" without verification
❌ "Standard pattern" without showing the pattern
❌ Assumptions based on "how it usually works"

**REQUIRED Pattern**:

````markdown
## Code Impact Verification

**Claim**: `invoice_service.py` needs no changes

**Evidence** (file: `billing/services/invoice_service.py:248`):

**Current Code**:
```python
# Lines 245-250 (verified by reading file):
line = {
    "payer_ref": charge.payer_ref,   # read from the charge, not from the order's customer
    "amount": charge.amount,
    "order_id": charge.order_id,
}
```

**Why This Works**:
1. ✅ The code reads `charge.payer_ref`, which the provider sets on each charge
2. ✅ Provider docs checked: a charge always carries the payer it was made against
3. ✅ After the change, new charges carry the account's payer, so invoices group by account
4. ✅ Tested in the provider's sandbox: invoice lines group correctly by account
5. ✅ No reference to `order.customer` in this module

**Related Code Verified**:
- ✅ Line 230: loads charges by invoice period
- ✅ Line 248: uses the charge field, not the order field

**Conclusion**: Verified safe - no changes needed.
````

**Rules**:
- Show actual code snippets
- Include line numbers
- List verification steps performed
- Provide test results if available
- Link to external docs if referenced

### 6. Migration Safety Requirements (MANDATORY)

All data migrations must include:

**Transaction Boundaries**:
```python
# REQUIRED: one transaction per record
for order in orders_to_migrate:
    try:
        with transaction.atomic():
            # Any failure rolls back ALL changes for this record
            account = resolve_billing_account(order)
            order.billing_account = account
            order.save(update_fields=["billing_account"])
    except Exception as e:
        logger.error("Migration failed for order %s: %s", order.id, e, exc_info=True)
        failures.append(order.id)
        continue  # don't raise - continue with the next record
```

**Idempotency Checks**:
```python
# REQUIRED: safe to run multiple times
def migrate_order(order):
    if order.billing_account_id is not None:
        logger.info("Skipping already migrated order %s", order.id)
        return
    # perform migration ...
```

**Checkpointing for Long Migrations**:
```python
# REQUIRED: resume capability
CHECKPOINT = Path("temp/migration_billing_account_checkpoint.json")

def load_checkpoint() -> int:
    return json.loads(CHECKPOINT.read_text())["last_id"] if CHECKPOINT.exists() else 0

def save_checkpoint(last_id: int) -> None:
    CHECKPOINT.write_text(json.dumps({"last_id": last_id, "at": datetime.now().isoformat()}))

for order in orders.filter(id__gt=load_checkpoint()).order_by("id"):
    migrate_order(order)
    save_checkpoint(order.id)
```

**Rollback Documentation**:
```python
# REQUIRED: rollback plan in the migration's docstring
"""
MIGRATION: Move orders to billing accounts

ROLLBACK PROCEDURE:
1. Stop the migration (Ctrl+C, or create temp/STOP_MIGRATION, which the loop checks).
2. Count migrated records: orders with billing_account_id set.
3. Reverse them: run the rollback command from the last checkpoint.
4. Verify: charges and invoices for a sample of orders match the pre-migration state.
5. Clean up payers created at the provider for accounts that no longer need them (dry run first).

TESTING ROLLBACK:
- Run the rollback on 10 records first
- Verify charging works after rollback
- Check for orphaned data

RECOVERY FROM PARTIAL FAILURE:
- The migration is idempotent - safe to re-run
- The checkpoint file tracks progress
"""
```

**Rate Limiting for External APIs**:
```python
# REQUIRED: handle API rate limits
def with_rate_limit_retry(max_retries=3, base_delay=1):
    """Decorator for payment-provider calls with rate-limit handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except PaymentsRateLimited:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)  # exponential backoff
                    logger.warning("Rate limited, waiting %ss (attempt %s)", delay, attempt + 1)
                    time.sleep(delay)
        return wrapper
    return decorator

@with_rate_limit_retry(max_retries=5, base_delay=2)
def create_payer(account):
    return payments_client.create_payer(...)
```

### 7. Pre-Submission Validation Checklist

**Before presenting spec to user, verify**:

```markdown
## Pre-Submission Checklist

**Code Reading Verification**:
- [ ] Did I actually READ every service the change touches? (Not just grep it; for example: models, services, webhooks, dashboards)
- [ ] Did I trace each affected handler line-by-line?
- [ ] Did I follow each affected query or execution path?
- [ ] Can I describe the exact function signatures without looking?

**Breaking Change Verification**:
- [ ] Did I grep for ALL references to changed fields?
- [ ] Did I open and read EVERY file that references changed code?
- [ ] Did I verify what happens in each webhook event type?
- [ ] Did I check admin interface customizations?

**Implementation Completeness**:
- [ ] Did I show ACTUAL code changes (not pseudocode)?
- [ ] Did I include error handling for all failure modes?
- [ ] Did I add transaction boundaries for data changes?
- [ ] Did I document rollback procedures?

**Red Flag Check**:
- [ ] Did I write "NO CHANGES NEEDED" anywhere?
  - If YES: Show the actual code that proves it works
- [ ] Did I use pseudocode for critical flows?
  - If YES: Replace with actual implementation code
- [ ] Did I hand-wave any decisions with "OR" or "maybe"?
  - If YES: Make explicit decision with justification
- [ ] Did I skip any items in the Breaking Change Checklist?
  - If YES: Complete them or justify why not applicable

**Testing Verification**:
- [ ] Did I include tests for all edge cases?
- [ ] Did I include rollback testing procedures?
- [ ] Did I include concurrent operation tests?
- [ ] Did I include migration failure recovery tests?

**QC Review Preparation**:
- [ ] Is the spec ready for quality-control-enforcer review?
- [ ] Have I addressed all CRITICAL items in advance?
- [ ] Are all code examples actual code (not pseudocode)?
- [ ] Are all claims backed by evidence?
```

**Pattern Stamping** (specs the rule applies to):
- [ ] Did I read the pattern library before writing Technical Specification?
- [ ] Does every ### design element (or the section, if it has none) open with a stamp that matches the grammar?
- [ ] Does every [NOVEL] name the closest pattern and why its mechanism does not apply?

**If any applicable checkbox is unchecked, DO NOT present spec to user.** Standard specs complete Code Reading Verification, Pattern Stamping and QC Review Preparation; Critical specs complete every group. An item that does not apply to this project may be marked "n/a: <reason>".

---

## MANDATORY: QC Review Before Presentation

### When to Run QC Review

Run quality-control-enforcer on every Standard and Critical spec before presenting it: Quick QC for Standard, Long Review for Critical (see "Review Tiers").

### QC Review Process

**Step 1**: Complete the spec with all required sections

**Step 2**: Run QC agent review:
```
Use Task tool with quality-control-enforcer agent:

Prompt: "Review the specification at temp/.planning/spec-{timestamp}.md and perform comprehensive quality control focused on:

1. Breaking changes - what existing code will break?
2. Data integrity risks - migration, orphaned data, race conditions
3. Business logic breakage - invoicing, payments, dashboards
4. Integration points - APIs, webhooks, external services
5. Edge cases & failure modes
6. Testing gaps
7. Code flow dependencies
8. Spec completeness - all required sections for the tier
9. Pattern stamps - apply "Pattern Stamping → Review checks" (specs the rule applies to)

Provide:
- List of specific code locations that will break
- Risk severity for each issue
- Required fixes/mitigations
- Additional testing requirements
- Show-stopper issues

Be thorough and critical."
```

**Step 3**: Address ALL CRITICAL and HIGH severity issues found

**Step 4**: Update spec with QC findings:
```markdown
## QC Review Results

**Review Date**: YYYY-MM-DD HH:MM
**Review Agent**: quality-control-enforcer

**Issues Found**: [count] CRITICAL, [count] HIGH, [count] MEDIUM

**Critical Issues** (must fix before implementation):
1. [Issue description]
   - Location: [file:line]
   - Fix: [solution]
   - Status: ✅ Fixed in spec v2 / ⏳ Pending

**Resolution Summary**:
- All CRITICAL issues: ✅ Addressed
- All HIGH issues: ✅ Addressed
- Spec ready for implementation: YES/NO
```

**Step 5**: Only present spec to user AFTER addressing all critical issues

### QC Failure Protocol

**If QC finds critical issues**:
1. DO NOT present incomplete spec to user
2. Create spec v2 addressing the issues
3. Re-run QC review on v2
4. Repeat until QC passes
5. Document iteration history in spec

**Example**:
```markdown
## Spec Version History

| Version | Timestamp | Stage | Findings | Change |
|---|---|---|---|---|
| v1 | 2025-11-13 14:30 | draft | n/a | Initial design |
| v1 | 2025-11-13 15:10 | QC | 3 critical / 1 high / 2 medium / 0 low | Webhook, dashboard and migration breakage found |
| v2 | 2025-11-13 16:45 | QC | 0 critical / 0 high / 1 medium / 2 low | Fixed webhook lookup, dashboard aggregation, migration transaction boundaries |
```

Every stage appends a row; Greenfield Rewrite keeps all rows.

---

## Why These Rules Exist

### Historical Context: A Billing Spec That Skipped These Rules

**What Happened**:
A specification for fixing usage-based billing claimed:
- "NO CHANGES NEEDED ✅" for multiple critical files
- Used pseudocode instead of actual implementation
- Didn't read the code that creates billing records
- Didn't check webhook handlers
- Didn't verify dashboard queries
- Hand-waved invoice consolidation strategy

**What Would Have Broken in Production**:
1. ❌ **Every new billing record** would have had the same bug (wrong payer used)
2. ❌ **All webhooks would fail** (customer lookup query broken)
3. ❌ **All dashboards would show empty** (billing queries broken)
4. ❌ **Data corruption during migration** (no transaction boundaries)
5. ❌ **Revenue loss** (usage recorded during the migration against the wrong payer)
6. ❌ **Debugging nightmare** (failures across 5+ files with no rollback)

**Impact**: Complete production outage affecting payments, billing, and customer experience.

**Root Cause**:
- Tunnel vision on "elegant solution" without checking implementation
- Assumed code would "automatically work" without reading it
- Claimed "NO CHANGES NEEDED" without verification
- Pseudocode hiding complexity and edge cases
- No QC review before presentation

**Prevention**: These rules exist to prevent this disaster from ever happening again.

### Key Lessons

1. **Never trust assumptions** - Always read the actual code
2. **Never use pseudocode** - Show actual implementation with error handling
3. **Never hand-wave** - Make explicit decisions, don't use "OR maybe"
4. **Always run QC** - Independent review catches blind spots
5. **Evidence-based only** - Claims require proof, not assumptions

---

## Benefits of Following This Protocol

**For User**:
- ✅ Prevents production disasters
- ✅ Provides clear implementation roadmap
- ✅ Enables informed decision-making
- ✅ Creates audit trail for changes
- ✅ Facilitates debugging if issues arise

**For AI Assistant**:
- ✅ Forces thorough analysis before claiming solutions
- ✅ Prevents tunnel vision on "elegant" solutions
- ✅ Catches missing edge cases early
- ✅ Documents all decision rationale
- ✅ Creates accountability for design quality

**For Codebase**:
- ✅ Maintains stability through changes
- ✅ Prevents cascading failures
- ✅ Ensures proper error handling
- ✅ Preserves data integrity
- ✅ Enables safe rollbacks

---

## Safe Feature Implementation Process

### Overview

This process ensures new features are added safely without breaking existing functionality. It prioritizes **additive changes** over modifications, **isolation** over integration, and **verification** at every step.

### The 7-Step Safe Feature Process

#### Step 1: Spec + QC + Issue (Before any code, Standard and Critical)

Trivial changes go straight to implementation and the floor ("Review Tiers").

1. Create spec in `temp/.planning/spec-{YYYY-MM-DD-HHMM}.md`
2. Run the tier's review — fix all CRITICAL, HIGH and MEDIUM issues, or record the user's decision not to act
3. Get user approval on spec (the shared Approval step)
4. Create GitHub issue via `/add-issue` skill (links spec, adds to the project board if one is configured, keeps Status and Tier)

**Gate**: No Standard or Critical code changes until the spec is approved.

#### Step 2: Feature Branch

```bash
git checkout -b feature/<issue-number>-<short-name>
# Example: git checkout -b feature/114-carrier-tracking
```

**Never implement directly on main.**

#### Step 3: New Files First (Additive)

Write new code in **new files** before touching existing ones:
- New service class (e.g., `shipping/carriers/acme/service.py`)
- New utility functions (e.g., `shipping/utils/parcel_size.py`)
- New exceptions (e.g., `shipping/carriers/acme/exceptions.py`)

**Why**: New files can't break existing functionality. They can be tested in isolation.

#### Step 4: Unit Test New Code in Isolation

Test the new files work correctly on their own before integrating:
```bash
<project test command> path/to/new/tests
```

Or verify in a REPL:
```python
from new_module import new_function
result = new_function(test_input)
assert result == expected_output
```

**Gate**: New code must work in isolation before integration.

#### Step 5: Integration (Minimal Touchpoints)

Connect new code to existing code with the **smallest possible changes**:
- One import line
- One function call
- One conditional branch

**Example** (adding a new carrier to shipping_service.py):
```python
# BEFORE (existing code - untouched):
elif request.carrier == 'parcelco':
    return self._track_parcelco(request)
elif request.carrier == 'acme':
    raise NotImplementedError("Acme tracking coming soon")

# AFTER (one line changed):
elif request.carrier == 'parcelco':
    return self._track_parcelco(request)
elif request.carrier == 'acme':
    return self._track_acme(request)  # NEW
```

**Rules**:
- Don't refactor existing code "while you're in there"
- Don't rename existing variables or functions
- Don't reorganize imports or file structure
- Keep the diff as small as possible for existing files

#### Step 6: Integration Test

Test the full flow end-to-end:
1. Verify existing features still work (regression)
2. Verify new feature works
3. Test edge cases from the spec

**Gate**: All existing tests must pass. New feature must work.

#### Step 7: PR + Deploy

```bash
git push -u origin feature/<branch-name>
gh pr create --title "..." --body "..."
```

After merge and deployment, verify on production.

### Safe Feature Checklist

Before merging any feature PR, verify:

```markdown
- [ ] Standard and Critical: spec created and QC passed
- [ ] Standard and Critical: GitHub issue created and linked to spec
- [ ] Feature branch used (not direct to main)
- [ ] New code in new files (additive, not modified)
- [ ] New code tested in isolation
- [ ] Integration changes are minimal (count modified lines in existing files)
- [ ] Existing tests still pass
- [ ] New feature tested end-to-end
- [ ] No unrelated changes included in PR
```

### Anti-Patterns to Avoid

- **"While I'm here" refactoring** — Don't clean up unrelated code in a feature PR
- **Big bang integration** — Don't modify 10 existing files at once
- **Skipping isolation testing** — Don't go straight to integration
- **Feature creep** — Don't add features not in the spec
- **Shared utility modification** — Don't change shared utilities to support your feature; extend them or create new ones

---

## Enforcement

**These rules are MANDATORY, not guidelines.**

**Violations that will be rejected**:
- Starting a Standard or Critical implementation without its spec
- Spec missing required sections
- Using pseudocode for critical flows
- Claiming "NO CHANGES NEEDED" without evidence
- Skipping QC review for architectural changes
- Presenting spec with unresolved CRITICAL QC issues

**Consequence of violation**: Spec will be rejected, implementation stopped, must start over with proper protocol.

---

*Originally created after a billing spec failure.*
