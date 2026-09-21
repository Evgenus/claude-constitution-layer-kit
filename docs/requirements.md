---
id: constitution-requirements
type: current-state
title: Constitution Requirements — traceability matrix and module specifications
status: active
---

# Constitution Requirements

*What every module must implement, and nothing about when: the phases and sequence live in the rollout plan [constitution-rollout-plan](rollout-plan.md), the kit's write-head. A module implements exactly its rows here ([law 4 of CLAUDE.md](../CLAUDE.md#law-4)).*

# Module Specifications — in order of introduction

*A description below is the module's draft until authoring begins; then it moves into the module's `MODULE.md` and this heading keeps its anchor with a one-line stub linking there. The anchor is the module's stable handle in the kit for its whole life, authored or not (decision [dec-0015-pre-module-audit-rulings](decisions/dec-0015-pre-module-audit-rulings.md)).*

**Traceability matrix** — every aspect decomposed into requirement parts, each with exactly one primary destination. Destination classes: **kernel §n** (shared semantics), **Mx** (module, with artifact kind), **binding** (per-project `constitution.yaml` — never module content), **template** (authoring law). An authoring session for module X takes exactly its rows as the requirement set; coverage check = every part homed, every module = exactly its rows.

**"Enters when" has two meanings** (decision [dec-0006-accumulating-set-first](decisions/dec-0006-accumulating-set-first.md)). For an accumulating module it names the first moment an object for the module exists; the module is authored *before* that moment, and for a greenfield consumer the whole accumulating set is the day-one install set. For a self-limiting module it names the friction signal that earns authoring. Dials follow the consumer; modules never wait for calibration.

**Module boundaries remain provisional until authoring** — settled by three tests: *one invariant? one enforcement moment? one lifecycle trigger?* Flagged rows (†) sit on boundaries under test: M7 may dissolve (A8.x → M6, A10.2 → M9). Settled: the M1/M2 boundary — [A2.3](#a2-3) is M1's, so one write-time script guards claimed territory and M2 is advisory creation (decision [dec-0015-pre-module-audit-rulings](decisions/dec-0015-pre-module-audit-rulings.md)).

| Part | Requirement (one line) | Destination | Recommended enforcement |
|---|---|---|---|
| <a id="a1"></a>**A1 — Document meta-types** | | | |
| <a id="a1-1"></a>A1.1 | Vocabulary: current-state / task-record / non-authoritative, with definitions | [kernel §2](../kernel/CONVENTIONS.md#k2) | definitional — enforced through A1.4's enum check |
| <a id="a1-2"></a>A1.2 | Lifecycle-aware precedence (policies always; write-head; current over historical; planned binds nothing) | [kernel §2](../kernel/CONVENTIONS.md#k2) | advisory — applied in agent judgment; conflicts surface via A4.4 |
| <a id="a1-3"></a>A1.3 | Reconciliation semantics: current-state = is-and-should-be, aligned at every task close | [kernel §2](../kernel/CONVENTIONS.md#k2) | definitional — enforced through A4.4's close gate |
| <a id="a1-4"></a>A1.4 | Every document in territory declares a valid envelope (id unique in the tree, type, title, status); nonconforming writes blocked with teaching errors | M1 hook+script | **gate**: PreToolUse hook, exit 2 blocks at write |
| <a id="a1-5"></a>A1.5 | Type-selection guidance incl. founding contrastive pairs and the mixed-document split rule | M1 skill | advisory — skill prose; pairs are the definition |
| <a id="a2"></a>**A2 — Location & governance binding** | | | |
| <a id="a2-1"></a>A2.1 | Territories; path-first resolution; declaration only where path absent/ambiguous; three defect classes | [kernel §3](../kernel/CONVENTIONS.md#k3) | definitional — enforced through A2.3 |
| <a id="a2-2"></a>A2.2 | Policy interface: governed current-state doc, referenced by id, calibration in dials, no internal format | [kernel §3](../kernel/CONVENTIONS.md#k3) | definitional — id-resolution checked by A2.3 |
| <a id="a2-3"></a>A2.3 | Resolution enforcement: no-policy / multi-policy / contradicting declaration blocked | M1 hook+script | **gate**: write-time hook block; same script as CI backstop on PR |
| <a id="a2-4"></a>A2.4 | Documents created by command from the policy's template into the canonical home | M2 skill | advisory procedure — its *output* is caught by A1.4+A2.3 gates |
| <a id="a2-5"></a>A2.5 | New-document-kind procedure: policy first (`process` stakes), then creation | M2 skill | advisory — skipping it lands in A2.3's no-policy defect anyway |
| <a id="a2-6"></a>A2.6 | The territory declarations themselves: `root_policy`, the optional `territory_dialect`, and each policy's territory in its dials namespace ([kernel §3](../kernel/CONVENTIONS.md#k3), [kernel §6](../kernel/CONVENTIONS.md#k6)) | binding | config — validated against the kernel's dials schema at each read, malformed = configuration failure (decision [dec-0018-dials-schema](decisions/dec-0018-dials-schema.md)); no declarations = silent territory |
| <a id="a3"></a>**A3 — Decisions & records** | | | |
| <a id="a3-1"></a>A3.1 | Stakes enum, ceremony table, fast lane | [kernel §4](../kernel/CONVENTIONS.md#k4) | definitional — enum enforced through A3.4; ceremony via review |
| <a id="a3-2"></a>A3.2 | Record shape: `stakes`+`decider`; body = options, pros/cons, one recommendation, choice | [kernel §5](../kernel/CONVENTIONS.md#k5) | frontmatter: **gate** via A3.4; body shape: advisory (skill-emitted, review-judged) |
| <a id="a3-3"></a>A3.3 | Supersession = in-place edit, stable id/path, named in commit; git is the append-only layer | [kernel §1](../kernel/CONVENTIONS.md#k1) | git-native (protected branch = immutability; by convention until a PR flow exists); commit naming: review judgment |
| <a id="a3-4"></a>A3.4 | Record validity enforced; records via skill, never free-form; routine → commit note | M3 hook+skill | **gate** on schema (hook/CI); creation path advisory |
| <a id="a3-5"></a>A3.5 | Routine/recorded boundary contrastive examples | binding | advisory — judgment calibrated by the examples |
| <a id="a3-6"></a>A3.6 | Promotion loop: recurring commit notes on a theme → record or procedure | M3 skill | advisory procedure; optional assist script listing note themes — no gate |
| <a id="a3-7"></a>A3.7 | Who may decide per stakes level | binding | review judgment (human check in PR) |
| <a id="a4"></a>**A4 — Handoff & task lifecycle** | | | |
| <a id="a4-1"></a>A4.1 | Task close is a single act: code + current-state docs together; then task files deleted | [kernel §2](../kernel/CONVENTIONS.md#k2) | definitional — enforced through A4.4 + A4.5 |
| <a id="a4-2"></a>A4.2 | Defect rule: doc↔code divergence outside any active task's scope is a defect | [kernel §2](../kernel/CONVENTIONS.md#k2) | detected by M4 scan — **gate as flag**; blocking is a dial |
| <a id="a4-3"></a>A4.3 | Lifecycle doctrine: `active` = in force, `inactive` = historical evidence kept while referenced, unreferenced → deleted; stalled = active record with no commits in scope | [kernel §1](../kernel/CONVENTIONS.md#k1) | advisory + optional active-age assist script |
| <a id="a4-4"></a>A4.4 | Close enforcement: code-touching change updates covered docs or carries a no-impact declaration | M4 check | **gate**: PR check, red = fix |
| <a id="a4-5"></a>A4.5 | Close skill: merge deltas → delete working files → set record `inactive`; active-without-progress flagged | M4 skill | advisory procedure; leftover-files check scriptable (**gate-lite** at close) |
| <a id="a4-6"></a>A4.6 | Coverage map; no-impact declaration format; active-age alarm | binding | config — validated at each read, malformed = configuration failure |
| <a id="a4-7"></a>A4.7 | Commit before you edit: rollback points live in git, not chat rewind (which skips Bash/script/subagent edits); dirty tree committed before a batch of edits, committed again after each coherent change, never left dirty at turn end | M4 skill + hook | advisory procedure + **gate-lite**: `Stop` hook warns on a dirty tree at turn end; blocking is a dial |
| <a id="a5"></a>**A5 — Referencing** | | | |
| <a id="a5-1"></a>A5.1 | One syntax per reference kind (id / path+anchor / code), id preferred where one exists | M5 policy | syntax: light lint script (**gate**); preference: advisory |
| <a id="a5-2"></a>A5.2 | Anchors are explicit stable IDs surviving edits, never heading-derived | M5 gate + skill | **gate**, in the whole-tree check of [A5.3](#a5-3): a link whose fragment is not among the explicit anchors of a covered target is a finding, unless the module's dial allows heading-derived anchors — the adoption path; choosing and placing an anchor: advisory at authoring |
| <a id="a5-3"></a>A5.3 | No merge introduces a broken reference (`lychee` ≥0.24.2) | M5 gate | **gate**: the whole-tree scan, CI on PR, red = fix; at write time the same whole-tree check runs after the write as deterministic feedback — it reports in the turn that breaks a reference and cannot block |
| <a id="a5-4"></a>A5.4 | References stay valid under supersession (stable id/path) | [kernel §1](../kernel/CONVENTIONS.md#k1) | git-native + caught by A5.3 when violated |
| <a id="a5-5"></a>A5.5 | Every citable unit of a kit document carries an explicit HTML anchor with a short fixed key — kernel section `k4`, template section `t3`, aspect `a5`, requirement row `a5-3`, law `law-3`, module spec = plugin name; the anchor stands on its own line before its target, or inside the first cell of a table row; a bare handle is a local alias inside its own document and link text everywhere else | M5 policy + template | advisory at authoring; broken anchors caught by A5.3 |
| <a id="a5-6"></a>A5.6 | Cross-document references are links: a governed document by `[id](current path)`; a section, row, aspect, law, or module spec by path+anchor with the handle as text; verbose handles — "[law 3 of CLAUDE.md](../CLAUDE.md#law-3)", "dial `ns.key`", "requirement A5.3" / "aspect A5", "module `const-x`" in module prose; `M<n>` retired outside this document; bare paths for ungoverned files only; a code location by symbol name, file-qualified — a line range only as a transient pointer; commit hashes only in commit messages, record bodies, and chat; a reference-form migration of a record is applied in place, at any time ([kernel §5](../kernel/CONVENTIONS.md#k5)) | M5 policy + lint | syntax: **gate** — M5's lint, the kit's own forms declared as its `lanes` in `constitution.yaml`; in the kit its scan is run by hand before every commit that touches a document until the kit's CI runs it; preference: advisory |
| <a id="a5-7"></a>A5.7 | Chat references are clickable wherever a file exists; local handles (numbers, letters, keys) are scoped to the message, the decision, or the session and the scope is named when a cite crosses it | M5 `SessionStart` hook (chat half; per-item handles stay A7.5) | advisory — always-on content, printed at session start: a skill is loaded by an activity, and a chat reply is none |
| <a id="a5-8"></a>A5.8 | A move or rename of a document leaves no reference broken: one act moves the file and rewrites the inbound links to it and its own relative links; after a move made by hand the same repair runs from the old and the new path, or from the envelope alone where a link's text is a governed id; links inside code are not rewritten, and mentions in prose are listed for a human, never rewritten; changing an `id` is not a move — it stays a recorded migration ([kernel §1](../kernel/CONVENTIONS.md#k1), [kernel §5](../kernel/CONVENTIONS.md#k5)) | M5 script + skill | the rewrite: advisory (a generator); its completeness: **gate** — the [A5.3](#a5-3) scan is green afterwards |
| <a id="a6"></a>**A6 — Question asking** | | | |
| <a id="a6-1"></a>A6.1 | Threshold: ask only at recorded stakes or genuine blockers; below → decide + commit note | M6 skill | advisory — honestly ungateable |
| <a id="a6-2"></a>A6.2 | One decision per message, in a fixed chat shape: options lettered A, B, C… (letters never collide with numbered items), each a bullet with a one-sentence description and separate **Pros:** / **Cons:** sub-bullets (one prose line each, several points joined by semicolons — never inline, never a table); exactly one recommendation with reasoning; named decider. Fewer than five options: the platform's question tool follows, carrying only letter + short label, never the argument. Complex trade-offs: a weighted-analysis policy, added at first concrete need | M6 skill | advisory |
| <a id="a6-9"></a>A6.9 | The argument must reach the user: chat text between tool calls in one turn is not always rendered; once the user reports an argument missing, every later decision in that session ends the turn on the chat message and the pick is collected by letter, without the tool | M6 skill | advisory |
| <a id="a6-3"></a>A6.3 | Derive-don't-improvise: questions from the artifact's open slots, in order | M6 skill | advisory |
| <a id="a6-4"></a>A6.4 | Enum-first: closed vocabularies offered as the option set | M6 skill | advisory |
| <a id="a6-5"></a>A6.5 | Defaults-with-override; overrides carry a one-line reason | M6 skill | advisory |
| <a id="a6-6"></a>A6.6 | Vague or context-foreign input: open the reply by restating it as understood; where several readings are plausible, name them and the one chosen; ask only above the A6.1 threshold, otherwise proceed on the stated reading — never guess silently | M6 skill | advisory |
| <a id="a6-7"></a>A6.7 | No deferred questions in deliverables; absent decider → explicit named blocker | M6 skill | advisory + optional **gate-lite**: script scanning deliverables for open-question markers |
| <a id="a6-8"></a>A6.8 | Per-decider asking preferences | binding | advisory |
| <a id="a7"></a>**A7 — Answer shape** | | | |
| <a id="a7-1"></a>A7.1 | Classify expected answer shape and match; yes/no answered with the word first | M7 skill | advisory — honestly ungateable |
| <a id="a7-2"></a>A7.2 | Every assumption made while interpreting or doing the work is listed explicitly, one line each, so the user can correct it; none listed when none were made; an assumption that would change the work materially is a question under A6.1, not an assumption | M7 skill | advisory |
| <a id="a7-3"></a>A7.3 | Lead with the answer; elaborate only on request | M7 skill | advisory |
| <a id="a7-4"></a>A7.4 | Honesty over agreement: say plainly when a request is wrong, unreasonable, or conflicts with governing rules, and why — even after the user has decided; never soften findings, hide failures, or report unverified work as done | M7 skill | advisory — honestly ungateable |
| <a id="a7-5"></a>A7.5 | Every list item is addressable: lists, tables, and option sets carry a stable per-item handle (number, letter, or key) so the user can cite one item without quoting it | M7 skill | advisory; optional **gate-lite**: script flagging unnumbered multi-item lists in governed documents |
| <a id="a8"></a>**A8 — Escalation** | | | |
| <a id="a8-1"></a>A8.1 | Stakes-triaged: routine gap → call + note; recorded gap → stop, ask, record | M7 skill † (→M6?) | advisory; record-side outcome caught by A3.4 when it happens |
| <a id="a8-2"></a>A8.2 | Never improvise a recorded-stakes procedure | M7 skill † (→M6?) | advisory |
| <a id="a8-3"></a>A8.3 | Irreversibility-triggered escalation, orthogonal to stakes: before any hard-to-reverse action (delete, history rewrite, force push, dropping a kernel definition, breaking a published contract) state the consequence and the reversible alternative, wait for an explicit yes in chat; one approval covers one action; a repeated request after the warning is the user's decision — proceed, note the objection in the commit | M7 skill + hook † (→M6?) | advisory for the class; **gate** for the enumerated command patterns: `PreToolUse` hook on Bash blocks known destructive commands with a teaching error until confirmed; pattern list is a dial |
| <a id="a9"></a>**A9 — Styling** | | | |
| <a id="a9-1"></a>A9.1 | One style-defaults policy; templates inherit; deviations carry a one-line reason | M8 policy | advisory; deviation-reason *presence* scriptable (**gate-lite**) |
| <a id="a9-2"></a>A9.2 | Founding entries: Mermaid-first; ASCII trivial-only by examples; pseudocode over formulas | M8 policy | advisory; PlantUML-without-justification detectable (**gate-lite**) |
| <a id="a9-3"></a>A9.3 | Lazy accretion: a default added at first concrete need, via the decision path | M8 policy | review judgment (`process` stakes path) |
| <a id="a9-4"></a>A9.4 | Checkable defaults graduate to Vale rules when [`const-language`](#const-language) installed | M8 policy | n/a until graduation — then A10.1's gate |
| <a id="a10"></a>**A10 — Language complexity** | | | |
| <a id="a10-1"></a>A10.1 | Governed documents pass Vale (`vale-cli`, pinned); grade/length/construction rules | M9 gate; thresholds → binding | **gate**: Vale in CI, red = fix |
| <a id="a10-2"></a>A10.2 | Plain chat language for non-native readers | M7 skill † (→M9?) | advisory — honestly ungateable |
| <a id="a11"></a>**A11 — Document budgets** | | | |
| <a id="a11-1"></a>A11.1 | Sizes measured in characters, never tokens | [kernel §7](../kernel/CONVENTIONS.md#k7) | definitional — embodied by A11.2's script |
| <a id="a11-2"></a>A11.2 | Post-hoc length gate per document kind; ceilings, not targets | M10 script | **gate**: script, warn → block per dial (ladder) |
| <a id="a11-3"></a>A11.3 | Ceilings set from observed data (≥ a month), one per meta-type at most | binding | review judgment, data-informed |
| <a id="a12"></a>**A12 — Kit portability** | | | |
| <a id="a12-1"></a>A12.1 | No project references in modules; specifics via dials; empty-repo test | [kernel §6](../kernel/CONVENTIONS.md#k6) + template | **gate**: kit-repo CI — install on bare repo + project-reference grep. The grep (decision [dec-0015-pre-module-audit-rulings](decisions/dec-0015-pre-module-audit-rulings.md)): in every file of a module, any absolute path, `file:` link, `~/`, or repository-relative path literal not prefixed by `${CLAUDE_PLUGIN_ROOT}` and not a public URL is a finding, with no exemption marker; the one repository path a module may name is `constitution.yaml`, every other location comes from the dials file or the territory declarations at runtime. A heuristic: the bare-repo defaults-only run stays the gate of record |
| <a id="a12-2"></a>A12.2 | Sibling references only as optional enhancements; kernel+module alone = functioning install | template | **gate**: kit-repo CI — kernel+single-module bare-repo run |
| <a id="a12-3"></a>A12.3 | One dials file, namespace per module, defaults always work | [kernel §6](../kernel/CONVENTIONS.md#k6) | **gate**: covered by A12.1's defaults-only run |
| <a id="a13"></a>**A13 — Catalogs (numbered kinds)** | | | |
| <a id="a13-1"></a>A13.1 | Catalogued id form: for a numbered kind, the kernel `id` and the filename stem are one name, `<prefix>-<nnnn>-<slug>` — lowercase kebab ([kernel §1](../kernel/CONVENTIONS.md#k1), [kernel §7](../kernel/CONVENTIONS.md#k7)), one prefix per kind with its own sequence, fixed zero-padded width; uppercase prefix tolerated in prose and resolved case-insensitively | M11 hook+script | **gate**: write-time hook in catalog territory blocks a non-conforming stem, or an id that is not the stem, with a teaching error |
| <a id="a13-2"></a>A13.2 | A catalog is virtual: the set of files carrying its prefix; no index, ledger, or register file exists; a listing is rendered on demand | M11 skill | advisory; the listing is one git-native command the skill names, an assist, never a gate |
| <a id="a13-3"></a>A13.3 | Allocation: next number = one more than the highest number the catalog has held on the branch, deleted items included, so a number once held is never issued again; provisional until it lands on main, frozen from then; reference items after they land | M11 skill+script | advisory procedure — the skill takes the number from the scan's count line, and the write-time fix text names it; history moves the advice only, never a verdict |
| <a id="a13-4"></a>A13.4 | Uniqueness: no two items of one catalog share a number; a collision at PR is repaired by the branch that has not landed renumbering its own item and its same-branch references — the item already on main keeps its number | M11 gate+skill | **gate**: the scan, run in CI on PR, red = fix; at write time a new item under a number the working tree already carries is blocked; renumber procedure advisory |
| <a id="a13-5"></a>A13.5 | Gaps are legitimate: a missing number is a deleted or renumbered item, git holds what it was; no continuity check, no placeholder records ([kernel §1](../kernel/CONVENTIONS.md#k1) deletion rule) | M11 | definitional — stated as an honest limit; backstop = branch review + git log |
| <a id="a13-6"></a>A13.6 | Reference forms: the full stem is canonical on machine surfaces (frontmatter, links); bare `PREFIX-NNNN` tolerated in prose; either resolves by one glob | M11 skill | advisory; syntax lint when [`const-referencing`](#const-referencing) is installed |
| <a id="a13-7"></a>A13.7 | Catalog declarations: a numbered kind is an entry of the module's dials — prefix, territory, width — independent of policies ([kernel §6](../kernel/CONVENTIONS.md#k6)); the same prefix listed twice is a defect | M11 script | the entries validated at each read (**gate**, configuration failure); double-declaration defect (**gate**, configuration failure) |

<a id="const-meta-types"></a>
## M1 `const-meta-types` — accumulating; authored first, in Phase A

Description moved into the module's document: [`modules/const-meta-types/MODULE.md`](../modules/const-meta-types/MODULE.md) (rows [A1.4](#a1-4), [A1.5](#a1-5), [A2.3](#a2-3)); this anchor stays the module's handle.

<a id="const-locations"></a>
## M2 `const-locations` — accumulating; enters with the second territory

**Failure pattern:** documents created in arbitrary places; kinds without homes; governance resolution ambiguity — every misplaced document is retrofit debt.
**Rules (advisory — skill prose, honestly labeled):** a new document is born in its canonical home with a valid envelope, from its policy's template; a new kind gets its policy first. The resolution gate that catches a misplaced document is [`const-meta-types`](#const-meta-types)' (A2.3, moved there — decision [dec-0015-pre-module-audit-rulings](decisions/dec-0015-pre-module-audit-rulings.md)); this module claims no gate and works with the kernel alone.
**Ships:** creation skill: new documents are created **by command/skill from the policy's template, landing in the canonical home with valid envelope** — templates are outputs of commands, never exemplars to imitate. Procedure for a new document kind: routine if a policy covers it; otherwise a `process`-stakes decision creates the policy first (escalation, stakes-triaged).
**Dials:** none of its own beyond the kernel's territory declarations (the project's core calibration); default policy for otherwise-unclaimed governed roots (optional).
**Acceptance:** a clean creation via the command lands in the canonical home with a valid envelope (review); the three defect classes are [`const-meta-types`](#const-meta-types)' fixtures.

<a id="const-decision-records"></a>
## M3 `const-decision-records` — accumulating; enters at the first real decision

Description moved into the module's document: [`modules/const-decision-records/MODULE.md`](../modules/const-decision-records/MODULE.md) (rows [A3.4](#a3-4), [A3.6](#a3-6)); this anchor stays the module's handle.

<a id="const-task-close"></a>
## M4 `const-task-close` — accumulating; enters at the first real task

**Failure pattern:** migrations left open — transactions that neither committed back nor rolled back, leaving the halfway state as silent de-facto truth; doc↔code drift with no owner.
**Invariant:** task close is a **single act**: a change touching code in territory covered by current-state documents also updates those documents *or* explicitly declares no impact; the task's working files are then deleted and its record set `inactive` (git remembers); an active task-record with no commits in its scope is stalled drift, to be committed back or rolled back.
**Ships:** PR-level check reading the diff's territories against current-state coverage — update present, or a no-impact declaration (mechanism: PR body marker or commit trailer — a design decision at authoring, decider: you); close skill executing the sequence: merge deltas into current-state docs → delete working files → set the record `inactive`. The kernel's **defect rule** made executable: doc↔code divergence outside any active task's scope is flagged, never tolerated. Carries the handoff residue: durable work products exist only as artifacts of defined kinds; work not committed did not happen. **Commit-before-edit (A4.7):** the session-level form of the same rule — git, not chat rewind, is the rollback layer (rewind does not track Bash, script, or subagent edits); a dirty tree is committed before a batch of edits and after each coherent change, never left dirty at turn end; a `Stop` hook warns on a dirty tree, blocking per dial.
**Dials:** current-state coverage map (which docs guard which code territories); no-impact declaration format; active-task age alarm (optional); dirty-tree-at-turn-end: warn or block.
**Acceptance:** red→green — code-touching PR without doc update or declaration blocked; with either, passes; close skill leaves no working files behind and the record `inactive`; dirty tree at turn end warned, clean tree silent.

<a id="const-referencing"></a>
## M5 `const-referencing` — accumulating once documents multiply; enters with the first cross-references

Description moved into the module's document: [`modules/const-referencing/MODULE.md`](../modules/const-referencing/MODULE.md) (rows [A5.1](#a5-1)–[A5.3](#a5-3) and [A5.5](#a5-5)–[A5.8](#a5-8)); this anchor stays the module's handle.

<a id="const-questions"></a>
## M6 `const-questions` — self-limiting; enters on the friction signal (expect it in Phase A's authoring sessions)

**Failure pattern:** both poles observed in the field — questions bundled, improvised, or asked without options and a recommendation; questions asked below the threshold (the agent should have decided and noted); open questions deferred into delivered documents; and the inverse ritualization: every small uncertainty escalated as a fixed-price ceremony.
**Rules (advisory — skill prose, honestly labeled):**
- **Threshold first:** ask only at recorded stakes (`process`/`product`/`architecture`) or at a genuine blocker; below it, make the reasonable call and note it in the commit — a question that shouldn't be asked is the first defect class.
- **One decision per message**, never bundled; simple factual clarifications exempt from the full format.
- **Format:** the argument lives in the chat message. Options are lettered **A, B, C…** — capital letters, so an option is never confused with a numbered finding, step, or assumption. Each option is a bullet: bold letter and title plus a one-sentence description on the first line, then two indented sub-bullets **Pros:** and **Cons:**, one prose line each; several points on one line are joined by semicolons, never a third nesting level; pros and cons are never inline in the description and never a table. Then exactly **one** recommendation with reasoning, and the **named decider**. When there are fewer than five options, the platform's question tool follows the message and only collects the pick: one-line question, letter plus short label per option, at most one clause of description — the pros, cons, and recommendation never go inside the tool. Five or more options: chat only, answered by letter. Trade-offs too complex for this shape get a weighted-analysis policy — deferred until a consumer hits the need. **Fallback (A6.9):** the argument must reach the user — chat text between tool calls in one turn is not always rendered (observed 2026-09-15: two of three arguments lost); once the user reports one missing, every later decision in that session ends the turn on the chat message and the pick is collected by letter, without the tool.
- **Derive, don't improvise:** questions come from the artifact's open slots (template fields, missing dials, unresolved `[decide]` markers), in order — not from free association.
- **Enum-first:** where a closed vocabulary exists (kernel enums, dial values, policy lists), the question offers exactly that option set; free text only for genuinely open values.
- **Defaults with override:** a slot with a sensible default is asked as "default is X — accept or override?"; overrides carry a one-line reason.
- **Vague input:** open the reply by restating it as understood; where several readings are plausible, name them and the one chosen; ask only above the threshold, otherwise proceed on the stated reading — never guess silently or elaborate in an unrequested direction.
- **No deferred questions:** a delivered plan or document contains only resolved decisions; if a decider is absent, an explicit named blocker halts the affected part — never an open question inside a finished deliverable.
**Ships:** the skill; contrastive pairs seeding the ask-vs-decide boundary (aligned with M3's routine/recorded examples — the two modules share the triage). A recorded-stakes answer produces a record per [kernel §5](../kernel/CONVENTIONS.md#k5) — via [`const-decision-records`](#const-decision-records)' skill when installed, free-form-per-schema otherwise; this module is the record's front-end in dialog, not a dependent of M3.
**Dials:** ask-vs-decide boundary examples; per-decider preferences (who wants to be asked about what).
**Acceptance:** the contrastive pairs; no gate claimed.

<a id="const-interaction"></a>
## M7 `const-interaction` — self-limiting; enters on its own friction signal

**Failure pattern:** short vague requests answered by 500-word essays; answers buried under preamble; assumptions silently made.
**Rules (advisory — skill prose, honestly labeled):** classify the expected answer shape (yes/no, value, short list, explanation) and match it — yes/no answered with the word first, qualifications after; lead with the answer, elaborate only on request; every assumption made while interpreting or doing the work listed explicitly, one line each, none when none were made — a material assumption is a question, not an assumption. **Honesty over agreement (A7.4):** say plainly when a request is wrong, unreasonable, or conflicts with governing rules, even after the user has decided; never soften findings, hide failures, or report unverified work as done. **Addressable lists (A7.5):** every list, table, or option set carries a per-item handle so one item can be cited without quoting it. **Irreversibility escalation (A8.3):** a second escalation trigger beside stakes — before any hard-to-reverse action, state the consequence and the reversible alternative and wait for an explicit yes; one approval, one action; a repeated request after the warning is the user's decision, executed with the objection noted in the commit; a `PreToolUse` hook on Bash blocks the enumerated destructive command patterns (dial) as a genuine gate — everything outside the list stays advisory, said so. Escalation, stakes-triaged: a procedural gap at routine stakes → reasonable call + commit note; at recorded stakes → stop, ask per the kernel's decision format, write the record per [kernel §5](../kernel/CONVENTIONS.md#k5) — never improvise a recorded-stakes procedure. (Richer when [`const-questions`](#const-questions) and [`const-decision-records`](#const-decision-records) are installed; functional with the kernel alone.) Plain chat language for non-native readers (the chat half of the old language aspect; the document half is M9).
**Ships:** skill (+ optional output style — a carrier plugins support); a `SessionStart` hook (matchers `startup`, `resume`, `clear`, `compact`) printing the module's mandatory rules to stdout — the plugin-native always-on carrier, re-injected after compaction, labeled advisory since it only shapes context; at most a one-line CLAUDE.md pointer for discoverability. Fallback when the consumer cannot run hooks: INSTALL.md instructs copying the mandatory block into CLAUDE.md (manual step, drifts on version bumps). Verified 2026-09-14 against the official docs: a plugin-root CLAUDE.md is never loaded, `${CLAUDE_PLUGIN_ROOT}` does not resolve in `@` imports, and the plugin cache path changes per version — so an import cannot reach a plugin, but a SessionStart hook can.
**Dials:** shape-boundary contrastive examples; verbosity preference (first concrete value: restatement and assumption lines appear only when triggered, never as empty ritual); destructive-command pattern list.
**Acceptance:** the contrastive pairs; red→green for the destructive-command hook only (blocked without confirmation, passes with); everything else advisory, no gate claimed.

<a id="const-styling"></a>
## M8 `const-styling` — self-limiting; enters at the first formatting friction

**Invariant/shape:** one **style-defaults policy** all templates inherit; templates state only deviations, each with a one-line reason. Founding entries exactly three: Mermaid by default, PlantUML only where Mermaid cannot express the diagram (one line naming the missing capability); ASCII art only for trivial cases (defined by contrastive examples); pseudocode over formulas. Defaults added **lazily at first need** — each born with a concrete consumer, via the normal decision path; mechanically checkable defaults may graduate into Vale rules when [`const-language`](#const-language) is installed — an optional enhancement, not a dependency.
**Ships:** the defaults policy document + inheritance wording for M2's templates.
**Dials:** none at founding.

<a id="const-language"></a>
## M9 `const-language` — self-limiting; enters on prose-complexity complaints

**Invariant:** governed documents pass Vale with the project ruleset — readability-grade ceiling, sentence-length limit, forbidden constructions — plain English for non-native readers.
**Ships:** Vale config (org renamed to `vale-cli`; pin packages by release URL — settled research) + CI/hook wiring. Known limitation carried forward: Vale cannot detect *missing* frontmatter fields (its scopes match only present content) — that is M1's script, never Vale.
**Dials:** the ruleset thresholds; covered territories.
**Acceptance:** red→green on an over-complex fixture.

<a id="const-doc-budgets"></a>
## M10 `const-doc-budgets` — self-limiting; enters when bloat is observed, with data

**Invariant:** governed documents respect character ceilings per document kind — **characters, never tokens** (tokenizer changes silently redefine token ceilings; character counts are vendor-stable and offline) — measured post-hoc by script; budgets are ceilings, not targets.
**Ships:** length-check script + wiring; a month of observed length data informs the ceilings before any becomes blocking.
**Dials:** ceiling per document kind (start with one per meta-type at most).
**Acceptance:** red→green on an over-limit fixture.

<a id="const-catalogs"></a>
## M11 `const-catalogs` — accumulating; enters with the first numbered kind (typically the first decision record, beside M3)

Description moved into the module's document: [`modules/const-catalogs/MODULE.md`](../modules/const-catalogs/MODULE.md) (rows [A13.1](#a13-1)–[A13.7](#a13-7)); this anchor stays the module's handle.

---

**Horizon — the knowledge layer (separate layer, builds on M1–M5 once lived-in):** `know-subject-units` (subject-shaped living documents — declared code paths, invariants + rationale only, merge-first rule, granularity by contrastive examples), `know-distillation` (story-close distillation into units, then deletion of exhaust), `know-pointers` (nested `CLAUDE.md` / path-scoped rules *generated from* `subject` declarations — no taxonomy, cross-cutting units surface everywhere they touch), `know-staleness` (subject+commit drift flagging — a flag means "re-verify the invariant," not "rewrite a mirror"). Entry gate: the constitution being lived-in, and the archaeology of the code worth trusting having a governed place to land.
