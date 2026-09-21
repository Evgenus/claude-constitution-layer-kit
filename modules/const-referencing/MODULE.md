---
id: module-const-referencing
type: current-state
title: const-referencing
status: active
---

# MODULE.md — `const-referencing`

*Draft at manifest version `0.0.1`; published at `0.1.0` in rollout Phase D. This document is the module's description ([template](../../module-template/MODULE.md)). Every list and table row carries a handle. Draft state: the design below is ruled; the artifacts of [§6](#t6) and the fixtures of [§10](#t10) are being authored, and [§10](#t10) says which exist.*

<a id="t1"></a>
## 1. Purpose

A document is moved, a heading is reworded, a record is deleted — and every link that pointed there still reads as a link and leads nowhere, or to a neighbouring section that happens to carry the old heading's words. Nobody notices at the edit, because the break is in *other* files; it is found weeks later by a reader who can no longer tell what was meant. Beside the broken link stands the reference that never was one: a bare "see section 4", a row number, an id in backticks — forms that resolve only in the head of whoever wrote them, that no tool can follow, and that a rename cannot find. The kit observed both: its largest rename was repaired by hand, link by link, and one reference form ruled in a record was found uncarried a month later because nothing could search for it. This module makes a reference a thing a machine can follow and keep: one written form per kind, an anchor that does not depend on a heading's wording, a check of the whole tree that turns red on any reference that does not resolve, and a move that repairs what it breaks.

<a id="t2"></a>
## 2. Failure class

**Accumulating.** Every bare handle and every heading-derived anchor written today is one more to convert when the first move breaks them, and a broken reference is found only by the reader it fails. **Entry trigger:** the first cross-reference between two documents — in practice day one of any project with more than one governed document.

<a id="t3"></a>
## 3. Rows

| row | this module's reading |
|---|---|
| [A5.1](../../docs/requirements.md#a5-1) | **The syntax half is the lint (gate), at `PreToolUse` and in the scan**, judging text outside the masked regions — the YAML block that opens the file, fenced and indented code, code spans — and outside links, which are removed whole, so a handle is seen only where it stands bare; a document may therefore *show* a retired form inside code. Three checks need no vocabulary: a governed id in backticks that is not a link (R2; the ids are those of the covered documents' envelopes, the document's own excepted; dial `bare_ids`), a link whose text is a governed id and whose target is not the document carrying that id (R3), an absolute local path or a `file:` link (R4). A project's own bare forms arrive through the dial `lanes` (R1). **The preference half — an id where one exists — is advisory**, the skill's: whether a path link should have been an id link is not judged. |
| [A5.2](../../docs/requirements.md#a5-2) | **Gate, inside the whole-tree check:** a link with a fragment, into a covered Markdown target, whose fragment is not among the target's explicit anchors — an `id` or `name` attribute written in the file, compared exactly, case included — is a finding (R7), although the link checker resolves it through a heading's generated name. The dial `heading_anchors: allow` switches R7 off: the adoption path for a repository whose links go through headings. Choosing a key and placing the anchor is advisory, the skill's. |
| [A5.3](../../docs/requirements.md#a5-3) | **The gate is the scan** — every covered document handed to `lychee` (0.24.2 or newer) offline with fragments, by this module's script, never by the consumer: a target file that does not exist (R5) and a fragment that does not (R6) are two findings. **At write time the same whole-tree check runs after the write**, at `PostToolUse`, as deterministic *feedback*: it reports, in the turn that causes them, the findings that involve the written file — its own links, and other documents' links into it — and cannot block. Coverage decides whose links are judged; a link from a covered document to any file must resolve. **Outside Markdown** a governed id is a reference where the project declares its form: the dial `mentions` (R8), scan only, because the link checker extracts only full URLs from such files. |
| [A5.5](../../docs/requirements.md#a5-5) | Advisory at authoring — the skill teaches the anchor's form: a short fixed key, on its own line before its target or inside the first cell of a table row. The module ships no policy and no template for the consumer's documents: those are the consumer's. A broken anchor is R6, a heading-derived one R7. |
| [A5.6](../../docs/requirements.md#a5-6) | The kit's verbose handles and retired forms are the kit's content ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)): in the module they are entries of `lanes`, and the row's list lives in the kit's dials file. What the module knows unaided is R2–R4. A code location by symbol name and commit hashes only in messages, records and chat are advisory, the skill's. |
| [A5.7](../../docs/requirements.md#a5-7) | Advisory, always-on: the two sentences a `SessionStart` hook prints ([§6](#t6)). Nothing inspects a chat reply ([§12](#t12), item 1). |
| [A5.8](../../docs/requirements.md#a5-8) | A second entry point, a generator and no gate: it moves a document and rewrites the inbound links and the moved file's own relative links; after a move made by hand it does the same from the two paths; with no paths it repairs every id link from the envelopes alone (the fix R3 teaches). Links inside masked regions are not rewritten; mentions of the old path in prose and in code are listed for a human. **Its proof is the gate:** each act ends by running the whole-tree check and exits with its verdict. Changing an `id` is not offered. |

[Requirement A5.4](../../docs/requirements.md#a5-4) is the kernel's and is caught by R5 and R6 when violated.

<a id="t4"></a>
## 4. Decisions

1. The record of this module's authoring rulings, dec-0033 — not yet written; it is written before the module's validation and linked here: the move and repair acts as a row; the scan as the gate with the post-write check as feedback; a second entry point for the mover; coverage by the module's own dial with `governed_only`; heading-derived anchors a finding; the `lanes` dial with the reason fixed; one `severity` for both handlers; `mentions` and the retirement of the kit's interim script; the chat rule through `SessionStart`; no pass-through of `lychee` configuration.
2. [dec-0005-reference-forms](../../docs/decisions/dec-0005-reference-forms.md) — the reference forms [rows A5.5–A5.7](../../docs/requirements.md#a5) state; its note that `lychee` does not parse a heading's `{#id}` attribute no longer holds for 0.24.2, which is one reason for R7.
3. [dec-0015-pre-module-audit-rulings](../../docs/decisions/dec-0015-pre-module-audit-rulings.md) — the runtime, the `severity` dial, the order of the two proofs.
4. [dec-0014-territory-dialect](../../docs/decisions/dec-0014-territory-dialect.md) and [dec-0018-dials-schema](../../docs/decisions/dec-0018-dials-schema.md) — `territories`, a lane's `home` and a mention's `files` are gitignore syntax; every read of the dials file validates the keys read.
5. [dec-0020-gate-script-rules](../../docs/decisions/dec-0020-gate-script-rules.md), [dec-0022-output-log-through-logging](../../docs/decisions/dec-0022-output-log-through-logging.md), [dec-0026-imports-at-the-top](../../docs/decisions/dec-0026-imports-at-the-top.md) and [dec-0025-shared-gate-code-linked](../../docs/decisions/dec-0025-shared-gate-code-linked.md) — the gate-script rules and the linked shared code; this module is its fourth consumer, the first with a second hook event, an external binary and a second entry point.
6. [dec-0010-module-research-per-module](../../docs/decisions/dec-0010-module-research-per-module.md) — the mechanism choices of [§6](#t6) rest on this module's own dated comparison.

<a id="t5"></a>
## 5. Invariant

**In a scanned tree every link of a covered document names a file that exists and, where it carries a fragment into a covered Markdown document, an explicit anchor that exists there; and a covered document written through the platform's file tools cites nothing by a form the lint refuses.** "Covered" is the dials `territories` and `governed_only` of [§7](#t7); territory, `id` and the dials file are the kernel's ([§1](../../kernel/CONVENTIONS.md#k1), [§3](../../kernel/CONVENTIONS.md#k3), [§6](../../kernel/CONVENTIONS.md#k6)); "a scanned tree" and "written through the platform's file tools" are the honest boundaries of [§9](#t9).

The advisory rules beside it, each `advisory` in its own text: (F-a) cite a governed document by its id as link text wherever it has one; (F-b) give every citable unit an explicit anchor with a short fixed key, never rely on a heading's generated name, never change a key once cited; (F-c) cite code by symbol name, file-qualified — a line range only as a pointer that is not meant to last; (F-d) a commit hash belongs in a commit message, a record's body or chat, never in a current-state document; (F-e) move a document with the module's move act, never by hand, and never rewrite a prose mention without reading it; (F-f) in chat, every reference to a file is a link and a local handle names its scope when it crosses it.

<a id="t6"></a>
## 6. Artifacts (rule-to-artifact mapping)

| component | path | carries |
|---|---|---|
| hook | `hooks/hooks.json` | Three handlers, exec form, explicit timeouts. `PreToolUse`, matcher `Write\|Edit`: `sh` with `["${CLAUDE_PLUGIN_ROOT}/scripts/check-references.sh"]` — the lint, the blocking gate. `PostToolUse`, the same matcher and command — the whole-tree check as feedback; the script tells the two apart by the event's `hook_event_name`. `SessionStart`: `sh` with `["${CLAUDE_PLUGIN_ROOT}/scripts/print-chat-rule.sh"]` — advisory. |
| script (sh) | `scripts/check-references.sh`, `scripts/move-document.sh` | POSIX entry points: find `python3`, exit 1 with the fix when it is missing, otherwise hand stdin and arguments on. Read no YAML. |
| script (sh) | `scripts/print-chat-rule.sh` | Prints the always-on lines below and exits 0. Reads nothing; advisory, and its only failure is printing nothing. |
| script (py) | `scripts/check-references.py` | Thin entry point of the gate, parseable by any Python 3: the interpreter floor, the shared package, then the module's `start`. Hook mode (either event) and `--scan [DIR]`. Its docstring is the contract. |
| script (py) | `scripts/move-document.py` | Thin entry point of the generator, the same shape: `OLD NEW` moves with `git mv` and repairs; `--moved OLD NEW` repairs after a move made by hand; `--ids` repairs id links from the envelopes. Each ends with the whole-tree check and exits with its verdict. It rewrites files; the gate's entry point never does — which is why they are two files. |
| package | `scripts/referencing_gate/` | The module's own code: `model`, `messages`, `dials`, `masking` (the regions no check reads and no repair rewrites), `links` (link extraction with positions over masked text), `lint` (R1–R4), `anchors` (explicit anchors of a file; R7), `lychee` (the one place the binary is found, its version read, the invocation built, the report parsed; R5, R6), `mentions` (R8), `repair` (the rewrites), `modes` (pre-write, post-write, scan; move, moved, ids), `start`. Step down from a platform component: none resolves a Markdown link, reads an envelope id, or rewrites a path. Step down to a third-party binary for resolution only: a resolver of the module's own would re-implement a forge's heading-name algorithm, which the comparison's prototype got wrong once; everything the binary cannot tell — which kind of anchor resolved, what a bare handle is, what an id link should point at — is the module's Python. No Markdown parser is declared: none surveyed gives the source position of an inline link, and the masked regular expression agreed with the link checker on all of the kit's links. `mypy --strict` clean. |
| shared code | `scripts/const_gate` → the kit's `shared/const_gate/` | A relative symbolic link to what every gate shares ([kit-shared-gate-code](../../shared/GATE.md)). With `governed_only: false` this gate resolves no policy and matches its own territories with the shared matcher; with `true` it builds the shared index. |
| configuration | `scripts/lychee.toml` | The module's own, empty but for comments: handed to `--config` so that a configuration file in the consumer's tree is never loaded. |
| dependencies | `requirements.txt` | PyYAML. `lychee` is no Python library: the module's own preflight finds it and reads its version, and its absence is X1. |
| skill | `skills/referencing/SKILL.md` | Rules F-a to F-e: the forms, choosing and placing an anchor, moving a document with the move act, repairing after a hand move, reading the list of prose mentions, running the scan after a shell edit. Model-invocable. Advisory. |
| install note | `INSTALL.md` | Requirements with the install command for `lychee`, zero-configuration behaviour, `lanes` with a worked example of a pattern's escaping in YAML, `mentions`, adoption through `severity: warn` and `heading_anchors: allow`, the scan command for CI, what the module does not check, no CLAUDE.md pointer. |
| tests | `tests/run.py`; `harness.py`, `consumer.py`, `shared_items.py` linked from the kit's `shared/tests/` | The fixtures of [§10](#t10). |
| command | none | no act here is one a human types: a move is asked for in words, and the skill carries it. |
| agent | none | a move is one step of the dialog that asked for it, not a delegation. |

- **Always-on content:** printed by the `SessionStart` hook, 297 characters, plus the skill's description in the skill listing: `const-referencing (advisory): in chat, write every reference to a file, a section or a document as a markdown link wherever the file exists. A number, letter or key is a handle local to its message, decision or session: when a cite crosses that boundary, name the message or decision it came from.`
- **Platform facts relied on** (all verified 2026-09-21 against the official documentation; sources in the research comparison, sections 1 and 9):
  1. A `PreToolUse` command hook exiting 2 blocks the tool call and Claude sees stderr as the reason. A `PostToolUse` hook exiting 2 shows stderr to Claude and the tool has already run — observed 2026-09-21 on Claude Code 2.1.251: the message reached the model word for word and its next call followed the fix. Breaks: the lint stops blocking; the feedback stops arriving.
  2. Every hook input carries `hook_event_name`; `PostToolUse` carries `tool_name`, `tool_input` and `cwd` in the format of `PreToolUse`; `file_path` is absolute; `Write|Edit` is an exact-string list. Breaks: telling the two handlers apart; locating the written document.
  3. On exit 0, JSON on stdout is parsed and `hookSpecificOutput.additionalContext` reaches Claude, capped at 10,000 characters; exit 1 is a non-blocking error; a timed-out hook, and one that cannot start, block nothing; the default timeout is 600 s. Breaks: the `warn` channel; the visibility of a configuration failure. The post-write report is bounded — the findings printed are capped and the count line carries the total.
  4. A `SessionStart` hook's stdout is added to the session's context. Breaks: the always-on rule.
  5. All matching hooks run in parallel; the most restrictive answer applies. Breaks: behaviour beside sibling gates.
  6. `${CLAUDE_PLUGIN_ROOT}` is substituted in hook commands and arguments and exported to hook processes; `${CLAUDE_PLUGIN_DATA}` is a persistent per-plugin directory; only `plugin.json` lives in `.claude-plugin/`. Breaks: plugin load; the default log location.
  7. A plugin ships nothing a forge executes: the scan reaches CI as one line of the consumer's own workflow, on a runner where `lychee` is installed. Breaks: where the gate can fire.
  8. `lychee` 0.24.2, by experiment and its documentation: with `--offline --include-fragments --format json` it reports a missing file and a missing fragment apart, each with line and column, in an `error_map` keyed by input; it skips links inside code; it resolves explicit `id` anchors, table cells included, and a heading's generated name, comparing fragments in lower case for Markdown targets and accepting a heading's `{#id}` attribute, which a forge renders as text; it exits 2 on a finding *and* on bad usage, the second with nothing on stdout; it loads a `lychee.toml` from the working directory unasked and honours a `.lycheeignore` there even under `--config`, unless started from another directory; a root-relative link needs `--root-dir`; a document on standard input cannot be resolved faithfully. Breaks: R5 and R6, and the reasons for R7, for the owned invocation and for resolving after the write and never before it.
  9. Cost, medians on the kit's tree (69 documents, about 1,300 links; macOS, Python 3.12.4): the binary over the whole tree about 52 ms, over a synthetic tree of 1,000 documents about 371 ms, its version about 14 ms; the interpreter's start about 52 ms. Breaks: nothing at a 30 s timeout short of a tree two orders of magnitude larger.
- **Research:** [docs/research/const-referencing.md](../../docs/research/const-referencing.md) (2026-09-21). Per row: [A5.3](../../docs/requirements.md#a5-3) `lychee` as the checker and the scan in CI as the gate — **confirmed**, and extended by the post-write check the comparison recommended; the specification's dial "lychee config" — **overturned**: the consumer's file can turn the verdict green unseen, so the module owns the invocation. [A5.1](../../docs/requirements.md#a5-1) and [A5.6](../../docs/requirements.md#a5-6) the syntax lint as a gate — **confirmed**, in the module's own Python, the project's forms through `lanes`. [A5.2](../../docs/requirements.md#a5-2) advisory — **overturned** for its one deterministic slice, R7. [A5.5](../../docs/requirements.md#a5-5) advisory — **confirmed**. [A5.7](../../docs/requirements.md#a5-7) advisory — **confirmed**, its carrier **overturned** from a skill to the `SessionStart` hook. [A5.8](../../docs/requirements.md#a5-8) — no scriptable tool moves a Markdown file and repairs its links, so the act is built here.

**Error messages.** Each row is one function of this module's `messages.py`, under the same key; `{path}` is the document's repository-relative path and `{line}` a line number. Findings are `RED`, three lines each (what failed / why the rule exists / the exact fix), followed by the count line. The texts every gate shares are written out once, in [kit-shared-gate-code §3](../../shared/GATE.md#g3), with `{module}` standing for `const-referencing`.

| key | first line | why | fix |
|---|---|---|---|
| R1 | `RED: {path}:{line}: '{match}' cites {names} by a bare handle` — `names` is the lane's | a bare handle resolves only inside its home document: elsewhere no reader can follow it, no check can test it, and a move cannot find it | `write it as a link: {fix}` — `fix` is the lane's, printed as written |
| R2 | `RED: {path}:{line}: document id '{id}' stands in backticks and is no link` | an id names a document that can move: only a link lets a reader reach it and lets a move repair it | `write [{id}]({relative path to its document}) — the path from this document to {owner}` |
| R3 | `RED: {path}:{line}: the link's text is document id '{id}', and its target {target} is not that document ({owner})` | a link that shows one document's id and opens another misleads every reader who trusts the text | `point it at {relative path to owner}; after a move, every such link is repaired at once by: sh "<plugin root>/scripts/move-document.sh" --ids` — the placeholder is printed resolved |
| R4 | `RED: {path}:{line}: '{match}' is a path on one machine` — an absolute path under a home directory, or a `file:` link | it resolves on the machine it was written on and nowhere else | `link a file of this repository by its relative path, or cite the public address the fact was verified at, or drop the reference` |
| R5 | `RED: {path}:{line}: link target {destination} does not exist`; for a break the link checker names in words of its own: `… {destination} does not resolve: {its words}` | a reference that does not resolve fails the reader exactly when they need it, and nobody else sees it | `correct the path; if the target was moved by hand, repair every link to it by: sh "<plugin root>/scripts/move-document.sh" --moved <old path> <new path>; if it was deleted, remove the link and state here what it was cited for` |
| R6 | `RED: {path}:{line}: {destination} has no anchor '{fragment}'` — and, where the target holds one that differs only in case, ` (it has '{found}': an anchor's case counts)`; this second form is the module's own reading, which the link checker passes, and `heading_anchors` does not switch it off | the same as R5 | `cite an anchor the target carries, or add <a id="{fragment}"></a> on its own line before the cited place in {target}`; for the case form: `cite '{found}' as it is written` |
| R7 | `RED: {path}:{line}: {destination} resolves only through a heading — its generated name, or a {#key} written after it — not through an anchor written in {target}` | a generated name changes when the heading is reworded, and every link through it breaks unseen | `add <a id="<short fixed key>"></a> on its own line before that heading in {target} and cite the key; a repository whose links go through headings sets const-referencing: {heading_anchors: allow} in constitution.yaml until they are converted` |
| R8 | scan only: `RED: {path}:{line}: '{match}' names a document no covered document carries as its id` | outside Markdown no link checker follows a name, so it dangles unseen once the document is renamed or deleted | `correct the name, or drop the mention and state the rule in words` |
| X1 | `BROKEN: const-referencing needs lychee 0.24.2 or newer and found none on PATH — fix: install it (https://lychee.cli.rs/installation/), then run the scan — until then no reference is checked for resolving` | — | — |
| X2 | `BROKEN: const-referencing needs lychee 0.24.2 or newer, found '{what it printed}' — fix: install a current one (https://lychee.cli.rs/installation/), then run the scan — until then no reference is checked for resolving`; where it printed no version: `…, its version could not be read` | — | — |
| X3 | `BROKEN: lychee gave no report: {what} ({first line of its stderr}) — fix: this is a defect of the gate's invocation or of the installed lychee, not of the repository; run lychee --version and report both to whoever maintains the plugin — until then no reference is checked for resolving` — `what` is `exit {code}` or `no answer in 25 s`; exit 2 without a parsed report is this, never a finding | — | — |
| G1 | the green line's words for an examined document: `a covered document`. This module's skip reason: `{path} is not covered (const-referencing.territories)` | — | — |
| F9 | the count tail: scan — `{d} document(s) and {l} link(s) examined, {m} Markdown file(s) scanned, {n} lane(s), {k} mention pattern(s)`; post-write — `{l} link(s) of the whole tree examined, {f} finding(s) involve {path}`, and ` — the first {cap} shown` when capped | — | — |
| V1–V4 | the mover's lines, on stdout: `MOVED: {old} → {new}`; `REWROTE: {path}: {n} link(s)`; `MENTION: {path}:{line}: '{text}' names the old path outside a link — read it and decide; nothing was changed`; the closing count `{files} file(s) rewritten, {links} link(s), {mentions} mention(s) listed` followed by the whole-tree verdict | — | — |
| V5 | `BROKEN: {old} is not a file git lists` / `{new} already exists` / `{old} and {new} are the same file` / after `--moved`: `{old} still exists` or `{new} does not` — each with its fix, exit 1, nothing changed | — | — |
| C5 | this module's dial failures, `BROKEN: constitution.yaml: {detail} — fix: {fix}`: `territories` not a non-empty list of patterns; `governed_only` not a boolean; `heading_anchors` not `refuse` or `allow`; `bare_ids` not `refuse` or `allow`; `lanes` / `mentions` not a list; entry `{n}` not a mapping, carrying an unknown key, lacking `pattern`, `names`, `fix` (a lane) or `pattern` (a mention), or holding a `pattern` the `re` module cannot compile — the compiler's message quoted | — | — |

**Installed components reference nothing in the kit.** The skill, hooks, scripts, error texts, fixtures and install note name no kit document; the reasoning lives here and in [§4](#t4).

<a id="t7"></a>
## 7. Dials

| dial | default | read by | meaning |
|---|---|---|---|
| `severity` | `block` | gate, hook mode | How loud a write-time finding is, for both handlers. `block`: exit 2 — the lint blocks the write; the post-write check reports as an error and **blocks nothing**, the write having happened. `warn`: exit 0 with the finding in one JSON object, for both. The scan ignores it. |
| `log_dir` | absent | gate, mover | As every gate's ([template §7](../../module-template/MODULE.md#t7)). |
| `territories` | `["*.md"]` | gate, mover | The covered documents: path patterns in the dials file's dialect over the Markdown files git lists, tracked and untracked, ignored ones excepted; a negated pattern takes files out. |
| `governed_only` | `false` | gate, mover | `true` narrows coverage to documents that also lie in a policy's territory; it needs `root_policy`, and without one the run ends as every policy-resolving gate's does. |
| `heading_anchors` | `refuse` | gate | `allow` switches R7 off. |
| `bare_ids` | `refuse` | gate | `allow` switches R2 off — for a project whose ids are everyday words. |
| `lanes` | `[]` | gate | The project's bare forms: a list of `{pattern, names, fix, home}` — a regular expression; what the form cites, in the project's words; the link form to write instead, printed as written; `home`, optional, patterns of the documents where the form is the local alias and the lane is silent. The reason is the module's and no lane can replace it. |
| `mentions` | `[]` | scan | Governed ids named outside Markdown: a list of `{pattern, files}` — a regular expression whose whole match must be a covered document's id; `files`, optional, patterns of the files read, default every file git lists that is no Markdown, no link and not binary. |

Nothing of `lychee`'s configuration is a dial: the module owns the invocation. The gate validates every key it reads at each read.

<a id="t8"></a>
## 8. Boundary examples

The lint, resolution and R7 are deterministic; the fixtures are their pairs. The judgment is the skill's.

**An id or a path (F-a):**

1. The target opens with an envelope → `[its-id](path)` / *not* `[the policy on records](path)`: the id as text is what the id repair works from.
2. The target is a script → a bare relative path in a link / *not* an invented id.

**An anchor's key (F-b):**

3. `<a id="t7"></a>` before "7. Dials" → survives the heading becoming "7. Calibration" / *not* `#7-dials`.
4. A key is wrong but cited from six documents → it stays / *not* renamed to something prettier: a key is for machines.
5. A table row is cited → the anchor inside its first cell / *not* before the table: that cites the table.

**Code and hashes (F-c, F-d):**

6. "`read_event` in `events.py`" → survives edits above it / *not* "lines 19–50", unless the sentence is about today's diff.
7. "Fixed in 70b7c39" in a commit message → fine / in a policy → *not*: a rebuilt history leaves it pointing at nothing.

**Moving (F-e):**

8. "Move the policies into `docs/policies/`" → the move act per file, then its list of mentions read one by one / *not* `git mv` and a search-and-replace: that rewrites code samples and sentences about the old place.
9. The act lists "`old/path.md` was where this lived until March" → left as it is: it means the old place / *not* rewritten because a tool found it.

**In chat (F-f):**

10. "see [MODULE.md](MODULE.md), section 7" → clickable / *not* "see the module doc".
11. "option B of the decision on coverage" in a later message → the scope named / *not* a bare "B" three messages on.

<a id="t9"></a>
## 9. Enforcement honesty

| # | artifact | kind |
|---|---|---|
| E1 | `PreToolUse` hook + `check-references` (hook mode): R1–R4 | `gate`, severity dial `severity` |
| E2 | `check-references --scan`: R1–R8 | `gate`, always exit 2 on a finding, ignores `severity` |
| E3 | `PostToolUse` hook + `check-references` (hook mode): R5–R7 for the written file | **deterministic feedback, declared as not blocking**: the check is the gate's own, the moment cannot stop a write. Under `block` it exits 2 so the finding reaches the model as an error; the gate for these findings is E2 |
| E4 | `move-document`: the rewrites | `advisory` — a generator; its closing verdict is E2's check, which is the proof |
| E5 | `SessionStart` hook, skill `referencing` | `advisory` |

**Honest limits**, each with its backstop. The shared code's limits — [kit-shared-gate-code §4](../../shared/GATE.md#g4) — apply. This module's own:

1. **`block` blocks nothing after the write.** Backstop: the scan in CI.
2. **No `lychee`, no resolution check** — X1 on every write, exit 1, which the platform lets through. Backstop: the message is loud and names the install; the lint still blocks; CI's scan fails closed, since exit 1 fails a workflow.
3. **A move or deletion through the shell reaches no hook.** Backstop: the scan; the skill's last step; the move act itself.
4. **The post-write report is about the written file only**, so a break elsewhere, older than this write, is not repeated at every write. Backstop: the scan reports everything.
5. **Links inside code are neither checked nor repaired**, and neither is a link assembled by a template or a script. Backstop: the mover lists mentions of the old path, code included.
6. **R7 judges only targets that are covered Markdown.** A fragment into an uncovered or non-Markdown file is the link checker's alone. An anchor made by a `{#id}` heading attribute is no explicit anchor here, because a forge renders it as text.
7. **File-name case follows the file system** the check runs on: a link in the wrong case passes on a case-insensitive disk and fails on CI's. Backstop: CI is the gate.
8. **Remote links are not checked**: the check is offline. **Masking is line-based**: an unclosed fence masks to the end of the file, and code inside an HTML block is not seen as code.
9. **A lane is as good as its pattern**; a `fix` text that teaches badly is the project's. Backstop: the reason is fixed, and the install note shows a worked lane.
10. **R2 and R3 know only the ids of covered documents.** `mentions` matches examples in fixtures and comments too; its `files` patterns keep them out.
11. **Prose is never rewritten**, so a move leaves sentences naming the old place. Backstop: V3 lists each.
12. **The mover needs a work tree git can move in**; it refuses, changing nothing, when the target exists. It does not stage its rewrites, and a short moved file whose links were rewritten may show in git as a deletion and an addition.

**Exit-code contract** (gate and mover): `0` green, nothing examined (the count line says so), or a move whose closing check is green; `2` a finding — for the mover, the closing check's; `1` configuration failure: the shared ones, X1–X3, C5, V5. Nothing exits 0 on error. The `SessionStart` script is advisory and fails open by printing nothing.

<a id="t10"></a>
## 10. Acceptance

**Draft: the runner exists — `python3 tests/run.py`, 88 items green — for the lint (cases 1–5, items 10–28), the whole-tree check in the scan (items 30–40) and the handler after the write, driven by real `PostToolUse` events against files on disk (items 50–59), with the shared items from 101; `mentions`, `governed_only` and the mover have none yet.** Each group was probed with mutants on a copy made with links followed, and each mutant was seen to be caught by a named item; one that survived — anchors read inside code — earned item 40. The plan for the rest, and the shape all follow — golden literal lines for every finding's first line and every fix variant, never text built by the message functions; a fake `lychee` and a fake `git` that note their calls in a file; every taught fix *followed* in the fixture, not only matched:

| item | kind | what it proves |
|---|---|---|
| P1 | fixture, red→green | R1–R4, one pair each, through a real `PreToolUse` event; a form inside a fence, a code span, the YAML block and a link's text is green; a lane's `home` is silent; `bare_ids: allow` |
| P2 | fixture, red→green | **the specification's two:** a deliberately broken reference (R5), and a deliberately moved anchor (R6) — in the scan and through a real `PostToolUse` event; the case hint of R6 |
| P3 | fixture, red→green | R7: a link through a heading's generated name, through a `{#id}` attribute, in the wrong case; `heading_anchors: allow`; an uncovered target is not judged |
| P4 | fixture, assertion | post-write: an inbound break caused by the write is reported, an older break elsewhere is not; `warn` for both handlers; the cap and the total; the event name decides the handler, and an unknown one is a configuration failure |
| P5 | fixture, assertion | the owned invocation: a `lychee.toml` and a `.lycheeignore` in the consumer's tree change nothing; exit 2 without a report is X3; X1 and X2 by a fake binary; the absence fixture of gate-script rule 15 |
| P6 | fixture, assertion | coverage: defaults on a bare repository; a negated pattern; `governed_only` with and without a root policy; a link from a covered to an uncovered file must resolve |
| P7 | fixture, red→green | R8 and `mentions`; off by default |
| P8 | fixture, assertion | every C5 failure, exit 1; a pattern that does not compile |
| P9 | fixture, red→green | the mover: red is the scan after `git mv` alone, green after the act — inbound links, the moved file's own links, fragments kept, reference-style links, a link in a fence untouched, a mention listed; `--moved`; `--ids`; every V5 refusal changes nothing; R3's and R5's taught commands run as printed |
| P10 | fixture, shared | the shared acceptance items that apply |
| L1 | live | in this repository: the scan agrees with the kit's interim check on every document; the kit's four bare forms as `lanes`, its records as `mentions`; one move through the act |
| L2 | live | a session with the plugin loaded: a blocked lint finding, a post-write finding followed by the model, the `SessionStart` lines in context |
| L3 | review | the designed texts of [§6](#t6), at the one yes |

**Examined count.** F9 in every green and red line; zero is said as zero.

<a id="t11"></a>
## 11. Siblings

**Depends on:** [kernel §1](../../kernel/CONVENTIONS.md#k1) (the envelope's `id`), [§3](../../kernel/CONVENTIONS.md#k3) (territories; policies only under `governed_only`), [§6](../../kernel/CONVENTIONS.md#k6) (the dials file). **Kernel alone:** in a repository whose dials file says nothing about this module every Markdown file is covered, R2–R7 run, and the move acts work — with no dials file at all the run is the visible skip every gate makes, naming the file to create; a repository with no envelopes has no ids, so R2 and R3 find nothing, and say nothing.

- When module `const-catalogs` is installed, renumbering an item is a move: its skill's rename step is this module's move act.
- When module `const-decision-records` is installed, the links to a record about to be deleted are what the scan reports after the deletion.
- When module `const-meta-types` is installed, the envelopes R2 and R3 read are well-formed; alone, an unreadable envelope carries no id and is skipped without a finding.

<a id="t12"></a>
## 12. Deferred

1. **A check of chat replies** (a `Stop` hook reading the last message for unlinked file names) — noisy by the comparison's account. Signal: consumers report replies that cite files unclickably despite the always-on rule.
2. **A post-batch check that sees shell moves** (`PostToolBatch`). Signal: breaks that reach CI traced to shell moves in sessions.
3. **A named dial for one `lychee` option.** Signal: a consumer needs that option for this gate's verdict, not for a link check of their own.
4. **The preference half of [A5.1](../../docs/requirements.md#a5-1) as a check** — a path link to a governed document whose text is not its id. Signal: id repairs that miss links because they were written by path.
5. **Changing an id as an act.** The kernel says an id never changes; a migration stays a recorded decision made by hand.
