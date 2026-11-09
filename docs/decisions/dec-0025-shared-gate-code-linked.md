---
id: dec-0025-shared-gate-code-linked
type: task-record
title: The shared gate code has one source in the kit and each module links to it; the interface is drawn from the second module's forced edits
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The shared gate code has one source, and each module links to it

## Context

[dec-0023-shared-gate-code-at-module-two](dec-0023-shared-gate-code-at-module-two.md) ruled that the shared code is extracted at the end of the second module's authoring, from the edits its verbatim copies could not avoid, and fixed the outcome in its item 3: source in the kit, vendored into each module, a kit gate on copy equality, the intent page amended, [law 3 of CLAUDE.md](../../CLAUDE.md#law-3) reworded. The second module, [`const-decision-records`](../requirements.md#const-decision-records), is authored; the evidence is below; what remained open was the form of the copy.

## Evidence — the forced edits and what each shows

Against the zero-edit commit of the copies (`errors`, `preflight`, `output`, `repository`, `territory`, `events`, `index`, `cli`, `consumer`: no edit):

1. `model` — `NAMESPACE` and `GATE`; the `Key` enum holds the module's finding keys; `Dials` gains `record_policies`; the module's vocabulary (`Stakes`, `RECORD_FIELDS`, `ROUTINE`) added. Reason: the module's identity and vocabulary sit in one file with the shared types, and `Dials` is a closed dataclass. Seam: shared types apart from module constants; a module extends the dials it reads.
2. `envelope` — `READ_FIELDS` extended by `stakes` and `decider`. Reason: the parse keeps five named fields and drops the rest, so an extension field is invisible. Seam: the parse keeps every field, or takes the wanted names from its caller; the first module's field validation (`envelope_errors`) is dead code in the second and belongs with the first module's checks.
3. `dials` — reads and validates `record_policies`. Reason: `_parse` builds the whole `Dials` from exactly two own dials. Seam: the shared reader returns the kernel-owned keys, the policy namespaces, the two fixed dials and the module's raw namespace; the module parses its own dials.
4. `messages` — the first module's findings removed, the record findings, two skip reasons, one note and one dial failure added, the scan's count line reworded to count records. Reason: gate-script rule 2 of [template §6](../../module-template/MODULE.md#t6) wants one messages module, and the file mixes shared texts with module texts. Seam: a shared messages module beside the module's own, and rule 2 reworded to allow exactly that.
5. `harness` — the two entry-point names, the scratch prefix, the package import. Reason: they are literals. Seam: the harness takes them as parameters. Two more seams met without an edit: the green half of a case is recognized by the literal `1 document examined, governed by`, so the second module's green line was worded to match; the runner must import the harness before the package, which the first module got from alphabetical order and the second had to pin.
6. Written again by hand, not copied, because the first module's file mixes them with its own logic: the helpers `_skip`, `_route_log` and `_report` of `modes` (verbatim), the pipeline of both modes up to the check (event, path, repository, dials, log, index), and the candidate policies of a document, which re-derive the resolution of [kernel §3](../constitution/CONVENTIONS.md#k3) because the first module's `resolve` returns its own findings. Seams: a pipeline skeleton that takes the module's examine function; a resolution that returns a typed result and leaves the messages to the module. The fixture `consumer` has no record policy; the second module adds one through each case's setup, with no edit.

7. Found by the second module's fresh-context validation in shared code, fixed at the source in the first module and copied again, so the copies stay equal: `repository` (a tracked file deleted from the working tree made the scan fail), `events` (an `Edit` that creates a file passed unexamined), `cli` (an abbreviated flag ran the scan logged as a hook run). Seam: a defect in shared code is one fix, which is what the extraction is for.
8. `messages`, a second edit: the fix lines of three shared dial failures (own namespace, `severity`, `log_dir`) showed an example that replaces the whole namespace, which in the second module drops `record_policies` and switches the gate off. Seam: a shared message about a module's namespace cannot show that module's dials; it names the key and leaves the example to the module.
9. Dead in the second module, carried by the copies until the extraction: `envelope.envelope_errors` with its six field messages and `TITLE_MAX`; `Index.governed`, `id_owners`, `void_namespaces_claiming`, `void` with `_collect_void_namespaces` (one git process per void namespace on every run, read by nothing); three skip and note messages about void territories. Seam: the index builds what its caller asks for. Also met: the harness's `Edit` cannot express `replace_all`, so that fixture builds its event by hand.

10. The per-write cost of two hook processes, measured in this repository on 2026-09-19 (nine policies, 51 Markdown files, macOS, Python 3.12.4, fifteen runs each, medians): a record write costs 320 ms through the first gate alone, 309 ms through the second alone, 367 ms through both started together, since the platform runs matching hooks in parallel; a write of a non-Markdown file costs 112 ms, 111 ms, and 118 ms. The second gate adds about 50 ms of wall-clock time to a governed write and nothing measurable to any other; most of a governed write's cost is one git process per policy, paid by each gate.

## Options

- **A. One shared package, copied whole into each module under one name,** a sync script, a kit gate on copy equality.
  - **Pros:** an explicit interface — identity passed in, the pipeline called by the module, a typed resolution, the module's own dials handed over; an installed module is self-contained wherever its folder goes; no dependence on how the platform treats links.
  - **Cons:** every shared change appears three times in the diff under review; a sync step to remember, with a gate to catch forgetting it.
- **A′. The same package and interface, reached through a relative symbolic link** from each module's `scripts/const_gate`, and from its `tests/` for the harness; a kit gate on the links.
  - **Pros:** one source in git and single diffs; drift impossible; links are the platform's own documented way to share files across the plugins of one marketplace, which copies what such a link points at into the installed plugin.
  - **Cons:** the documentation says a link leading outside a plugin is skipped when the plugin is loaded from a local path in copy mode — the kit's own path until rollout Phase D — though on Claude Code 2.1.251 a plugin loaded with `--plugin-dir` runs in place and the link resolves (experiment of 2026-09-19); a module's folder copied out of the repository without following links is not self-contained; a checkout without symlink support leaves a text file.
- **B. Shared files copied into each module's own package,** equality checked file by file.
  - **Pros:** small change; imports stay relative.
  - **Cons:** the interface stays implicit — every module's `model` must export whatever the shared files import; the four mixed files cannot be shared as they stand; the hand-made duplicates stay.
- **C. Extract only the eight unedited files now.**
  - **Pros:** least work.
  - **Cons:** against the timing the earlier record chose; most of the duplication survives, including the code where this validation found three defects.

Recommendation: first A; after the decider asked how the failure of A′ could be made deterministic, A′ with its mitigations — with them the failure is loud and of the same class as a missing library, and the choice is cheap to reverse in either direction. Chosen A′ by the decider in chat on 2026-09-19.

## Ruling

1. **One source.** `shared/const_gate/` for the gates, `shared/tests/` for the harness, the consumer and the acceptance items of shared behaviour. Admission stays as ruled: code that implements a kernel section literally, or a gate-script rule of the template, needed by two or more modules.
2. **Linked, not copied.** A module's `scripts/const_gate`, and `harness.py`, `consumer.py` and `shared_items.py` in its `tests/`, are relative symbolic links to the source. This replaces the form of item 3 of the earlier record — "vendored into each module, a kit gate on copy equality"; its principle stands for an installed plugin: what the platform installs carries everything it runs.
3. **The kit gate is on the links:** `scripts/check-shared-links.py`, red for a copy, a plain file, a dangling, absolute or misdirected link, with `--self-test` as its red→green fixture.
4. **A missing link fails loudly.** Each module's entry file turns a failed import of the shared package into one designed `BROKEN` line and exit 1, with an absence fixture. It does not block: a configuration failure that blocks would change the exit-code contract of [template §9](../../module-template/MODULE.md#t9) for every gate, which is a separate decision nobody has asked for.
5. **The interface** is the one the evidence draws: identity declared by the entry point; the module's two modes loaded after the preflight; the pipeline called by the module and calling nothing back; the module's namespace handed over as read; resolution as a typed result; shared messages in the shared package and the module's own beside them, so gate-script rule 2 reads "one messages module per package".
6. **The shared texts have one home,** the governed page beside the source, under its own policy ([dec-0011-one-policy-per-kind](dec-0011-one-policy-per-kind.md)); a module's document links to it.
7. **If the link fails in practice** — the consumer-live proof of rollout Phase B, or a platform update, shows it skipped — the fallback is option A: replace the links by copies, swap the link gate for an equality gate. No module code changes.

## Applied

In the commits that land this record: the code (the commit before this one); [kit-shared-gate-code](../../shared/GATE.md) and its policy [plc-0009-shared-code](../policies/plc-0009-shared-code.md) with its territory in `constitution.yaml`; both module documents; gate-script rules 1, 2, 14 and 15 and the skeleton of the [template](../../module-template/MODULE.md); [law 3](../../CLAUDE.md#law-3) and step 4 of "Developing a module" in [CLAUDE.md](../guide/developing-a-module.md#s4); the architecture section of [INTENT.md](../../INTENT.md); Phase A step 3 of the [rollout plan](../rollout-plan.md). [dec-0023-shared-gate-code-at-module-two](dec-0023-shared-gate-code-at-module-two.md) is set `inactive`: its ruling is applied. This record is born `inactive`.
