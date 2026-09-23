---
id: dec-0037-dials-file-block-style
type: task-record
title: The dials file is written in block style, flow style only where a list or a mapping is empty; a kit gate holds it and rewrites it
status: active
stakes: process
decider: Eugene Chernyshov
---

# The dials file is written in block style; a kit gate holds it and rewrites it

## Context

At the yes on the sixth module the decider read the kit's `constitution.yaml` and asked, on 2026-09-23, for its mappings and lists to be written out one key or one item per line — flow style, `{…}` and `[…]`, kept only for an empty list or mapping — and for that to hold in future. The file had grown flow-style collections from its first territories to the coverage map the sixth module added: a pair written `{name: …, code: […], docs: […]}` on one line is read twice before it is read right, and a diff of such a line cannot name the item that changed. The dials file is the one file every module reads and every consumer will copy the shape of.

## Options

- **A. A kit gate.** `scripts/check-yaml-style.py`, Python with PyYAML: red with file and line on any non-empty flow collection, the fix naming the block form; wired into the routine list of `pyproject.toml` and the gate list of `CLAUDE.md`, run before commits until the kit's CI runs it, with a self-test as its fixture.
  - **Pros:** deterministic and teaching; no third-party tool; the shape of the kit's other gates; the rule and its gate land together.
  - **Cons:** one more script to run by hand until CI; it judges the file, not YAML examples inside Markdown fences.
- **B. A formatter that rewrites the file.**
  - **Pros:** nothing to fix by hand.
  - **Cons:** as a third-party tool: the one round-trip library tried on this file dropped an inline comment into the data and broke the file — a rewrite is the wrong tool for a file read by people and machines alike unless it keeps every comment and anchor by construction.
- **C. The rule in prose only,** in the file's header comment and in `CLAUDE.md`.
  - **Pros:** nothing to build.
  - **Cons:** the kit's own history shows prose rules drifting; this one drifted in the change the record is folded into.

## Recommendation

A, by the session.

## Choice

A and B together, chosen by the decider in chat on 2026-09-23: the gate, plus a rewrite of the file's own — a `--fix` mode of the same script, working on the parser's event stream so that every comment, anchor, alias and quote outside a flow collection's span stays as written; for `constitution.yaml` only; folded into the change of the sixth module rather than a change of its own.

## Ruling

**R1.** The kit's `constitution.yaml` is written in block style: one key or one `- ` item per line; flow style, `[]` or `{}`, only where a list or a mapping is empty. The rule is the kit's own, for its one dials file; the YAML examples inside the kit's Markdown are not under it, and a consumer's file is the consumer's.

**R2.** The gate is `scripts/check-yaml-style.py`, kit development tooling never shipped in a module: exit 2 with the line and a teaching message on a non-empty flow collection, exit 0 with the count of collections examined otherwise, exit 1 when it could not run; `--fix` rewrites every non-empty flow collection into block style, keeps every comment, anchor, alias and quote as written, refuses a collection spanning several lines, and proves before writing that the file still says what it said; `--self-test` is its fixture. It is run before every commit that touches the file until the kit's CI runs it, and is listed in the routine of `pyproject.toml`.

**R3.** The rewrite of the file on 2026-09-23 — thirty-one collections, the data and every comment proven equal before and after — and the folding of this record into the sixth module's change: one-time acts.

## Carry list

1. R1 — the header comment of [constitution.yaml](../../constitution.yaml) and its reading-list line in [CLAUDE.md](../../CLAUDE.md).
2. R2 — [the gate itself](../../scripts/check-yaml-style.py), its docstring stating the modes and exits; the routine list of [pyproject.toml](../../pyproject.toml); the reading-list line in [CLAUDE.md](../../CLAUDE.md).
3. R3 — history only.
