---
id: dec-0005-reference-forms
type: task-record
title: Reference forms for kit documents and chat; explicit anchors on every citable unit
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Reference forms for kit documents and chat

## Context

The kit had no ruling on how one document cites another. Kernel sections were cited as bare `§n`, modules as `M<n>`, requirement rows as `A<n>.<m>`, laws as `law n`, and records by backticked id — none of them links, none anchored, none resolvable by a tool. `M<n>` was defined only inside the rollout plan and was already used unresolved in four records. Every MODULE.md shares the template's section numbers, so "MODULE.md [kernel §3](../constitution/CONVENTIONS.md#k3)" would become ambiguous with the first authored module. Requirement [A5.1](../requirements.md#a5-1) names the three reference kinds (id, path+anchor, code) and [A5.2](../requirements.md#a5-2) demands explicit anchors. No anchor syntax or id-link syntax had been chosen, so neither could be applied.

An inventory of every reference form in use and in chat was made on 2026-09-15 (twenty forms, keyed R1–R20), with the uniqueness scope, resolution reach, and qualifier of each. The decider ruled on each form in chat; the four sub-decisions below were the open slots the rulings left.

## Rulings on the forms

Two surface rules:

- **in chat**, every reference to something that exists as a file is clickable, and local handles (numbers, letters, keys) are scoped to the message, the decision, or the session;
- **in documents**, every cross-document reference resolves uniquely, and a bare handle is local to its own document.

- <a id="r1"></a>R1 id reference: canonical for governed documents; syntax per sub-decision 2.
- <a id="r2"></a>R2 path + explicit anchor: the universal cross-document form; absorbs kernel sections (R5), module handles (R7), template sections (R8).
- <a id="r3"></a>R3 bare path: ungoverned files and chat only; a governed document is cited by id.
- <a id="r4"></a>R4 code location: symbol name, file-qualified; line ranges only as transient pointers.
- <a id="r6"></a>R6 requirement rows:
  - **prose form** "requirement [A5.3](../requirements.md#a5-3)", "[aspect A5](../requirements.md#a5), requirement [A5.3](../requirements.md#a5-3)" where the aspect matters;
  - **each row and each aspect header** carries an anchor;
  - **cross-document form** is a link with the handle as text.
- <a id="r7"></a>R7 `M<n>`:
  - **retired outside the rollout plan**, where it stays as the planning alias;
  - **elsewhere** a link to the module's spec section with the plugin name as text.
- <a id="r9"></a>R9/R10 catalogued items: unchanged, as requirement [A13.6](../requirements.md#a13-6) states.
- <a id="r11"></a>R11 sibling modules: module prose says "module `const-x`" with conditional phrasing; kit documents and chat link to the spec.
- <a id="r12"></a>R12 `${CLAUDE_PLUGIN_ROOT}`, R13 commit hashes (commit messages, record bodies, chat only), R14–R16 local chat handles, R18 qualified PR references: unchanged.
- <a id="r17"></a>R17 laws: verbose form "[law 3 of CLAUDE.md](../../CLAUDE.md#law-3)", linked; valid only while laws are numbered.
- <a id="r19"></a>R19 dials: verbose form "dial `ns.key`".
- <a id="r20"></a>R20 rejected forms: as already ruled by [law 1 of CLAUDE.md](../../CLAUDE.md#law-1), [law 2 of CLAUDE.md](../../CLAUDE.md#law-2), [kernel §1](../constitution/CONVENTIONS.md#k1), [A5.1](../requirements.md#a5-1), [A5.2](../requirements.md#a5-2), [A6.2](../requirements.md#a6-2), [A7.5](../requirements.md#a7-5).

## Sub-decision 1 — anchor mechanism and id scheme

1. **HTML anchor element on its own line before the target** (`<a id="k4"></a>`; inside the first cell for a table row), ids as short fixed keys: `k1`–`k7` kernel sections, `t1`–`t12` template sections, `a5` aspects, `a5-3` requirement rows, `law-3` laws, the plugin name for module specs.
   - Pro: rendered everywhere; lychee resolves `id=` attributes so requirement [A5.3](../requirements.md#a5-3)'s gate covers it; survives edits and renumbering; keys equal the handles already in use.
   - Con: visible HTML in the source; one extra line per target.
2. Anchor element inline in the heading line.
   - Pro: no extra lines.
   - Con: pollutes heading text for tooling; cannot anchor table rows.
3. Pandoc `{#id}` attributes.
   - Pro: clean source.
   - Con: not rendered by GitHub, not parsed by lychee: fails "clickable" outright.
4. Descriptive slug ids with mechanism 1.
   - Pro: readable URLs.
   - Con: invites heading-derived drift; longer chat handles; the numbers already carry the meaning.

Choice: option 1.

## Sub-decision 2 — id-reference syntax

1. **Markdown link, id as text, current path as target**:
   - **`[dec-0001-session-conduct-rows](docs/decisions/dec-0001-session-conduct-rows.md)`**;
   - **the id is the durable part**, the path is derived and repaired by tooling on a move.
   - Pro: clickable now, verified by lychee, repairable later; no new syntax.
   - Con: the path is a second copy that rots between a move and the repair.
2. Wiki-link `[[id]]`.
   - Pro: one token.
   - Con: not clickable; gate blind.
3. Path link without the id.
   - Pro: plain markdown.
   - Con: is R3, not R1; nothing to repair from after a move.

Choice: option 1.

## Sub-decision 3 — migrating inactive records in place

1. Migrate mechanically, ruling text untouched, commit named a migration.
   - Pro: honours R7 fully; records stay clickable evidence.
   - Con: an in-place edit of a record with no rule saying it is allowed.
2. Freeze records; exempt `docs/decisions/` from the check.
   - Pro: [kernel §5](../constitution/CONVENTIONS.md#k5) stays absolute.
   - Con: `M<n>` stays unresolvable in records forever; every future convention needs the same exemption.
3. **Migrate, and state the carve-out in [kernel §5](../constitution/CONVENTIONS.md#k5)**: a reference-form migration is not a ruling and is applied in place.
   - Pro: removes the ambiguity for good.
   - Con: a kernel edit for a case seen once.

Choice: option 3.

## Sub-decision 4 — proposals P1 and P2

P1 (requirement-row form, R6) accepted on the condition that an aspect has exactly one anchorable home; the matrix's aspect header rows are that home. P2 (sibling form, R11) accepted.

## Applied in the same commit

- **Kernel:** anchors `k1`–`k7`; [kernel §5](../constitution/CONVENTIONS.md#k5) gains the migration sentence.
- **Template MODULE.md:** anchors `t1`–`t12`; sibling wording "module `const-x`"; cross-document cites linked.
- **Rollout plan:**
  - **anchors** on aspect headers, requirement rows, and module spec headings;
  - **requirements [A5.5](../requirements.md#a5-5)–[A5.7](../requirements.md#a5-7) added**;
  - **[`const-referencing`](../requirements.md#const-referencing) spec** carries the rulings and the interim check.
- **CLAUDE.md:** anchors `law-1`–`law-9`; a session-conduct bullet for the chat rule; module step 1 notes the link-depth check after copying the template.
- **All four earlier records:** cites migrated (sub-decision 3).
- `scripts/check-references.sh`: the interim gate (bare retired forms, lychee with fragments), run by hand until the CI of [aspect A12](../requirements.md#a12) exists.

Deviation from a stated assumption:

- **inside its own document** a handle stays bare (a local alias, per the documents rule above) rather than being linked;
- **the earlier assumption** to link self-references was dropped as redundant.
