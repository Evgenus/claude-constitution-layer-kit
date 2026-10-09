---
name: carry-audit
description: The kit's closing audit before a human yes — fresh readers check that every ruling of the decision records in scope is stated in a current-state document, that no document relies on a record, and that the change did not un-carry an older ruling. Use at the end of a module's development, before accepting any decision record, on a kernel change, and before publication. Kit development tooling; never shipped in a module.
---

# Carry audit

**Advisory procedure, mandatory step.** Whether a sentence states a rule is judgment, so the audit is
run by readers and is no gate. What a script can hold — that every ruling item names a home, and
that an acceptance names its audit — is `scripts/check-carry-lists.py`, and this procedure ends by
running it. The rule this serves: an applied ruling lives in the current-state documents it changed,
and a record is provenance, never authority ([kernel §5](../../../kernel/CONVENTIONS.md#k5)); the
kit's own reading of it is rule 2 of [plc-0004-decision-records](../../../docs/policies/plc-0004-decision-records.md#r2).

## When

1. At the end of a module's development, as the second pass of the fresh-context validation — step 6
   of "Developing a module" in [CLAUDE.md](../../../CLAUDE.md).
2. Before the yes on any decision record written outside a module's development; for a `product`
   record, which has no yes, on the commit that holds it.
3. In full — every record — on any change to the kernel, and once before publication.

## Steps

1. **Commit first, then pin.** The tree is clean; the pin is `git rev-parse --short HEAD`. Every
   reader is told the pin and reports the commit it started and ended on. A reader whose commit moved
   reports which of its files changed.
2. **Compute the scope, never choose it.** `python3 scripts/check-carry-lists.py --scope <base> [<module>]`,
   where `<base>` is the commit the change started from. It prints two lists:
   - `full` — the records the change adds or edits, and those the module's decisions section cites,
     each printed with its reason: added, edited or cited;
   - `regression` — every other record that cites a file the change touched. Editing such a file is
     how an older ruling gets un-carried.
   A full audit skips this step and takes every record as `full`.
3. **Partition.** At most five `full` records to a reader, at most ten `regression` records to a
   reader. Readers are fresh subagents, started together, holding nothing of the authoring reasoning.
   A regression reader is the `regression-reader` agent of `.claude/agents/`, and the confirming
   reader of step 7 the `confirming-reader` agent there; each fixes its model and its read-only tools
   and carries the standing part of its prompt (B, D); the full and blind readers and the reader of
   wording edits (prompt E) run on the session's model.
4. **Give each reader its prompt**, below, with its record list filled in — check that it is filled
   in before sending: a prompt has gone out with its list still a placeholder.
5. **Run the blind pass** on each record the change adds: one more reader, prompt C, with one
   question per carried item — a "pending" or "history only" item has nothing to answer from.
   Where the change makes wording edits in accepted records or frozen comparisons, run one more
   reader, prompt E, on every such edit.
6. **Consolidate, and verify before acting.** A reader can be wrong: check every finding you mean to
   act on against the tree yourself. Give every finding a handle. Each is fixed, or justified in a
   commit message of the change, the merge commit included — never only in the pull request's
   description, which git does not keep.
7. **Read the fixes again.** Fixes made in a hurry break things. Commit them,
   pin a confirming reader to that commit — prompt D — and, when the fixes make or change wording
   edits in accepted records or frozen comparisons, a reader of prompt E beside it; repeat while a pass finds a defect. Until
   its yes the fixes may correct the record in place, and the commit says so
   ([kernel §5](../../../kernel/CONVENTIONS.md#k5)); a `product` record has no such window and is not
   edited beyond the same section's mechanical edits — its findings go into the documents or a
   further record
   ([rule 15 of plc-0004-decision-records](../../../docs/policies/plc-0004-decision-records.md#r15)).
8. **Write the receipt.** The commit that names the yes — the merge commit of the change's pull
   request, written with `gh pr merge <n> --merge --subject "Work: <name>" --body "…"` — carries two
   trailers in its last paragraph, beside the attribution line:
   `Accepted: <record id>` — one per record, or several ids separated by commas;
   `Carry-Audit: at <pin>; <n> records; <f> findings, <x> fixed, <j> justified` — where the pin is
   the last round's, an ancestor at which the record already existed; `n` counts `full` and
   `regression` records together and is above zero; `f` counts the findings of every round, and
   `x + j = f`. For a `product` record, which has no yes, the `Carry-Audit:` trailer stands alone on the merge
   commit of the change that holds the fixes. The newest acceptance of a record is the one that counts: a
   wrong receipt is mended by accepting again, in the merge commit of a new pull request.
9. **Run the gate:** `python3 scripts/check-carry-lists.py`. Red is fixed before the turn ends.

## Prompt A — a reader of `full` records

> STRICTLY READ-ONLY. Create, edit, move or delete no file; run no git command that changes state and
> no script that writes. The audit is pinned to commit `<pin>`: report `git rev-parse --short HEAD` and
> `git status --short` at the start and at the end.
>
> Read sections 1, 2 and 5 of `kernel/CONVENTIONS.md`, and rules 1, 2, 5 and 7 of
> `docs/policies/plc-0004-decision-records.md`. The question: could each record below be deleted without
> anyone losing a rule they must follow? Records: `<list>`.
>
> For each record: (1) read it whole and split what it rules into items — every rule, definition,
> step, dial, exception, obligation, measurement, fallback and deferred trigger. Hunt outside the
> ruling section too: a binding sentence under Context, Options, Recommendation, Choice or Reasoning is
> an item, and it is the kind most often left out of a carry list. (2) For each item find where it is stated today in
> current-state text or code: `kernel/`, `CLAUDE.md`, `INTENT.md`, `constitution.yaml`,
> `docs/policies/`, `docs/requirements.md`, `module-template/`, `shared/`, `modules/`, `scripts/`,
> `pyproject.toml`, `.claude/skills/`. Not current-state: `docs/rollout-plan.md` — though intent that is not yet real
> lives there legitimately, say so — `docs/research/`, `README.md`, a module's `README.md`, commit messages, other records.
> Judge each item CARRIED (file and line, verified), PARTIAL (what exactly is missing), MISSING,
> SUPERSEDED (by which record; does the text match the later ruling?) or CONTRADICTED. Rationale and
> one-time acts living only in the record are history, not a gap. (3) If the record has a carry list,
> verify every entry: does the linked text state the item in full; is anything marked "history only"
> that binds someone in future; does the task-record a "pending" entry links hold the item — and if
> that task-record has closed, or the item is real already, does current-state text now state it? A
> gap there is a finding against the documents, never against the list, which is not rewritten. (4) Find every mention of the record's id outside `docs/decisions/` —
> scripts, error texts, tests, schemas, comments — and classify each PROVENANCE (the sentence is
> complete without it) or RELIANCE (quote it; say what text would have to be inlined). (5) Does
> `status` match reality? Verdict per record: REMOVABLE-NOW, REMOVABLE-AFTER-FIXES (the exact fixes),
> or NOT-REMOVABLE.
>
> Trust no record's claim that something was applied — verify it in the target file. Report tersely,
> every item and link with a handle such as `0031-R2` or `0031-L1`, then the fixes, then the two git
> readings.

## Prompt B — a reader of `regression` records

Sent to the `regression-reader` agent, whose definition already holds the read-only rule, the two
git readings and the kernel reading; the message still states them, since a reader run on another
agent must hear them too.

> STRICTLY READ-ONLY, pinned to `<pin>`, as in prompt A. The change under audit touched these files:
> `<touched files>`; `git diff <base> <pin> -- <touched files>` shows what changed, and a sentence the
> diff deleted or reworded is where to look first. For each record below, find the ruling items whose home is in one of those files
> and check that the file still states each of them in full, at the pin. Report only what is no longer
> stated, weakened or contradicted, with the record's id, the item, and the file and line where it
> used to stand or should. Records, each with the touched files it cites: `<list>`.

## Prompt C — the blind pass on an added record

> STRICTLY READ-ONLY, pinned to `<pin>`, with the two git readings, as in prompt A. You may not open
> anything under `docs/decisions/`. Holding only the current-state documents — the places prompt A
> lists — answer each question with the file and line that states the answer, and a
> verdict ANSWERABLE, PARTLY or NOT-ANSWERABLE; say where two texts disagree or a sentence reads two
> ways. An item you cannot answer is a finding. Questions: `<one question per carried item, written
> by the author from the carry list>`.

## Prompt D — a confirming reader, after fixes

Sent to the `confirming-reader` agent, whose definition already holds the read-only rule, the two
git readings and the kernel reading; the message still states them, since a reader run on another
agent must hear them too.

> STRICTLY READ-ONLY, pinned to `<pin of the fixes>`, with the two git readings, as in prompt A. A
> first audit produced the fixes in `git diff <earlier pin> <pin>`. Fixes made in a hurry introduce
> defects; find those, and do not audit the rest again. Check that the texts the diff touched still
> agree with each other and with the kernel — quote both sides where they do not; that every ruling
> item of the record still appears once in its carry list and that the linked text states it; that
> every code path the diff changed does what its message says, and that every fix a message teaches
> would turn the check green. Say of each finding whether it is a defect to fix before the yes, or a
> nicety.

## Prompt E — a reader of wording edits

> STRICTLY READ-ONLY, pinned to `<pin>`, with the two git readings, as in prompt A. Read the kinds
> of wording edit that rule 14 of `docs/policies/plc-0004-decision-records.md` allows in an
> accepted record and rule 7 of `docs/policies/plc-0005-research.md` in a frozen comparison, and
> the mechanical edits of section 5 of `kernel/CONVENTIONS.md`. Then read every edit in
> `git diff <base> <pin> -- <the frozen documents the change edits>`, with `--word-diff` too. For
> each changed spot, say which kind it is, whether it is that kind exactly as the rule words it,
> and whether the text still says what it said: no ruling, fact, number, scope or speaker moved,
> no clause attached to another subject, no fragment that reads differently. Report each finding
> with the file, the line, the text before and after, and whether it is a defect to fix before
> the yes or a nicety.

## What this audit cannot do

1. It is as good as its readers: a reader can miss an item or assert a false one. Step 6 exists for
   the second; only a second reader helps with the first, and step 7 is one.
2. The receipt records that an audit was declared, at a real commit, with its findings accounted
   for. It cannot show that the readers were run. That stays a matter of honesty and review.
3. The `regression` list is wide when a change touches a document most records cite. It is kept
   affordable by the narrow question of prompt B, never by dropping records from the list.
