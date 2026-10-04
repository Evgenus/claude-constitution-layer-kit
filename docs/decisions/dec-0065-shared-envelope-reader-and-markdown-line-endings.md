---
id: dec-0065-shared-envelope-reader-and-markdown-line-endings
type: task-record
title: One shared reader says where the envelope stands and splits its lines, every gate that finds its end asks it, and a line ends only at a line feed, a CRLF or a lone carriage return
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# One shared reader says where the envelope stands and splits its lines, every gate that finds its end asks it, and a line ends only at a line feed, a CRLF or a lone carriage return

## Context

An audit of the kit's hardcoded logic on 2026-10-02 found that four places read where the envelope ends, each in its own way. The shared reader ignored trailing whitespace on a `---` line and split lines with Python's `splitlines()`. [`const-language`](../requirements.md#const-language) compared each line with `== "---"` and split on line feeds only. So a closing line `--- ` made the language gate grade the title as prose, a false red on the wrong line. Worse, with a later `---` in the body, it blanked everything down to that line, so the first section was never read: a false green. [`const-referencing`](../requirements.md#const-referencing) and [`const-locations`](../requirements.md#const-locations) kept copies that agreed with the shared reader on common input. An inventory made before any code found a fifth site, a second test in the referencing gate. It also found a second drift: Python's `splitlines()` breaks a line at a form feed, U+2028 and six other characters, which Vale and Markdown do not.

The change this record rules is on one branch. Every module is a draft at `0.0.x`, so no version is bumped ([dec-0053-drafts-keep-their-versions](dec-0053-drafts-keep-their-versions.md)). [Rule 2 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2) admits code to the shared source when it implements a kernel section and two or more modules need it, and lets a shared part be widened for one module when the widening keeps a rule the part carries for all. Five questions were put to the decider in chat, each with lettered options and one recommendation, the pick a letter. Section 6 holds what the change makes where no choice existed.

## 1. Whether the envelope's bounds are shared

The audit's item on this defect argued three ways to fix it.

- **A. A local fix in the language gate.** Two lines make its comparison ignore trailing whitespace.
  - **Pros:** routine stakes; proven green on a copy; the module's own limit that claims to read the envelope as the shared reader does becomes true.
  - **Cons:** four copies of the rule stay; the next copy can drift the same way.
- **B. One shared helper that says where the envelope stands, used by every reader that finds its end.**
  - **Pros:** one definition, so the modules cannot disagree; a shared acceptance item proves it in every gate that judges envelopes; admission under rule 2 holds, class K, since it implements the frontmatter block of [kernel section 1](../../kernel/CONVENTIONS.md#k1) and three modules need it.
  - **Cons:** it touches shared code and three modules; `process` stakes, so a record and a yes.
- **C. Normalise the text once in the shared pipeline.** Every line's trailing whitespace stripped, or CRLF turned into LF, before any module sees it.
  - **Pros:** one point fixes CRLF for every gate.
  - **Cons:** it changes what every gate reads, not only the envelope; a trailing double space is a Markdown line break, and a length count must see the file as written; it hides the rule instead of naming it.

**Recommendation.** B, by the audit's session on 2026-10-02: the drift came from copies, and only one definition stops the next one.

**Choice.** B, by the decider, in chat on 2026-10-04, when the decider set this change's scope.

**R1.** The shared envelope reader has two more public parts, both class K. `envelope_bounds(text)` says where the envelope stands, as character offsets into the text as given, a byte-order mark included. `envelope_lines(text, start, stop)` is the line splitter. `parse_envelope` is built on both and gives the same verdict as before for every text that holds none of the characters of R4. A module that blanks, masks or rewrites the envelope asks `envelope_bounds` where it stands and cuts its lines with `envelope_lines`; it keeps no reading of its own of where the envelope opens or closes, or of where one of the envelope's lines ends.

## 2. Whether the history report's link defect joins this change

The same audit item found a defect of the same class in [`const-doc-budgets`](../requirements.md#const-doc-budgets): its history report measures a symbolic link as the length of its target's path. It shares no code with the envelope reader.

- **A. Its own item, later.** It stays out of this change and is fixed as a small routine change of its own.
  - **Pros:** the change keeps the scope set at its start, a lesson of the change before it; this record and its audit cover one idea; another module, so the two cannot block each other.
  - **Cons:** the history report stays wrong a little longer; one more branch and pull request.
- **B. Inside this change.** The history report follows a link inside the tree in the same branch.
  - **Pros:** one pull request closes both halves of the audit item; fixed sooner.
  - **Cons:** scope growth at the start; a fourth module in this record and its audit.

**Recommendation.** A, by the session: no code in common with the reader, and a small change was the point.

**Choice.** A, by the decider, in chat on 2026-10-04.

**R2.** This change leaves the history report of [`const-doc-budgets`](../requirements.md#const-doc-budgets) as it is; its link defect is work of its own.

## 3. The shared-code page over its ceiling

[The shared-code page](../../shared/GATE.md) stood at 56,331 characters against its 49,000 `shared-code` ceiling, at warning, and this change adds to it. The ceiling and its warning level were left as they are by [dec-0064-shared-gate-defects-one-refusal-one-path-rule](dec-0064-shared-gate-defects-one-refusal-one-path-rule.md).

- **A. Leave it at warning, as before.** The change adds its lines; the follow-up is tracked.
  - **Pros:** keeps the earlier call and this change's scope; nothing blocks; the follow-up is audited on its own.
  - **Cons:** the page grows further past its ceiling; the warning shows on every edit and scan.
- **B. Split section 5 into its own document, inside this change.**
  - **Pros:** the warning goes; the new shared item lands in the new document.
  - **Cons:** scope growth; links that many records and module documents cite move, so the carry audit widens.
- **C. Raise the ceiling to about 58,000, inside this change.**
  - **Pros:** one line; the warning goes.
  - **Cons:** a ceiling raised to fit holds nothing; scope growth; a ceiling change is a call of its own.

The decider then asked whether the page could be shortened instead. The session answered: yes, by about 8,000 to 12,000 characters, but [rule 6 of plc-0009-shared-code](../policies/plc-0009-shared-code.md#r6) keeps each platform fact's version, date, backstop and fallback, so only the history of the observations and text that restates code can go, and many records cite the page.

**Recommendation.** A, by the session, with the follow-up worded as a shortening within rule 6.

**Choice.** A, by the decider, in chat on 2026-10-04, "for now", to be taken up after the remaining changes of the audit.

**R3.** The decider's choice for the page among splitting section 5, raising the ceiling and shortening the page within rule 6 is taken up after the remaining changes of the audit of 2026-10-02.

## 4. Which characters end a line

The helper returns offsets, so line numbers stay right whatever it calls a line. The choice decides which `---` closes the envelope when one of the characters `\x0b`, `\x0c`, `\x1c` to `\x1e`, `\x85`, U+2028 or U+2029 stands beside it. The inventory showed the language gate reaching a false green through a form feed before the closer.

- **A. Keep Python's `splitlines()`.** The language gate and the locations generator follow the shared reader as it was.
  - **Pros:** the four gates built on the shared reader keep exactly their verdicts; the smallest change; the false green goes.
  - **Cons:** a `\x0c---` line closes the envelope where GitHub and Vale see no closer, so a gate is green on an envelope a renderer shows as text.
- **B. Markdown's line endings only: a line feed, a CRLF, a lone carriage return.** Trailing whitespace on a delimiter is still ignored.
  - **Pros:** the gates read the file as GitHub, Vale and every Markdown renderer do; an envelope a renderer would break is red; the false green goes.
  - **Cons:** the shared reader's verdict changes on such rare files, in four modules; one more case in the new shared item.

**Recommendation.** B, by the session: a gate's green should mean a Markdown reader sees the same envelope.

**Choice.** B, by the decider, in chat on 2026-10-04.

**R4.** A line ends at a line feed, a CRLF or a lone carriage return, and nowhere else. The envelope opens when the first line, leading byte-order marks aside, is `---` with its trailing whitespace ignored, and ends at the first later line that is `---` the same way. A line that holds one of the other characters before `---`, or after it with text, such as `\x0c---`, is no delimiter.

## 5. A second copy of the line rule

The verifier of the locations generator's piece found that `filling.py` held its own copy of R4's line-ending pattern, to cut the envelope into lines. No input reaches it today, since the command reads templates in a way that turns every ending into a line feed. But nothing tied the two copies together.

- **A. Fix it inside this change.** The shared reader makes its line splitter public, and the generator uses it and drops its pattern.
  - **Pros:** the rule lives once, the purpose of this change; small, inside R1's scope; the documents were not written yet, so they name it at no extra cost.
  - **Cons:** one more public shared function for one module, to be justified under rule 2; one more commit and verifier.
- **B. Log it as an item of its own and leave the copy.**
  - **Pros:** no more work in this change; no reachable harm today.
  - **Cons:** the change closes with the copy it set out to remove; the record must explain it.

**Recommendation.** A, by the session: a copy of the rule left behind undoes the change's purpose, and the fix is small and in scope.

**Choice.** A, by the decider, in chat on 2026-10-04.

**R5.** `envelope_lines` is the one place R4's line rule is written in code. It is a widening for one module that rule 2 of plc-0009-shared-code admits, since it keeps the line rule the reader carries for every module, and the other modules call nothing new.

## 6. What the change makes where no choice existed

These items carry no options. Each follows from the answers above or from the kit's rules, and each stands open to the decider's override before the yes.

**R6.** The language gate blanks exactly the envelope `envelope_bounds` returns. Everything before its end is replaced by one empty line for each line feed it holds, so every line number Vale reports stays the same. A carriage return in the envelope is deleted, not turned into a space, so prose after a closer that ends with a lone carriage return is read and never taken for indented code. An envelope that never closes is not blanked.

**R7.** The referencing gate masks the envelope from the start of the file to where `envelope_bounds` says it ends, and to the end of the file when it never closes.

**R8.** The locations generator rewrites the envelope it finds through `envelope_bounds` and `envelope_lines`, writes the rewritten block with line feeds and no byte-order mark before it, and keeps the body as the command read it.

**R9.** The shared acceptance item S164 proves R4 and the offsets and line cuts of R1 in every gate that judges envelopes. A gate that judges none leaves it out, and where it blanks or masks the envelope, it proves where the envelope ends in its own items.

## Applied

The commits of this branch apply every item. R1 and R4 to R9 were applied by the commits before the one that adds this record, save sentences added with the record or by its audit. The commit that adds the record adds item 9 of section 2 of the shared-code page, which states R1's rule for a module, the clause of [`const-referencing`](../requirements.md#const-referencing)'s rows section that states R7, and the plan's sentence that holds R3. The audit's fixes add the plan's sentence that holds R2 and the clause of rule L-d of [`const-locations`](../requirements.md#const-locations) on the byte-order mark in R8. The record is born `inactive`.

## Carry list

1. R1 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `envelope` row of section 1; [section 2](../../shared/GATE.md#g2), item 9; [`const-language`](../../modules/const-language/MODULE.md#t9), limit 9.
2. R2 — pending: [step 9 of the rollout plan](../rollout-plan.md#s9), the routine change that makes the history report follow a link; until it lands, limit 9 of the module's own document states the defect.
3. R3 — pending: [step 9 of the rollout plan](../rollout-plan.md#s9), the decider's choice for the shared-code page.
4. R4 — [kit-shared-gate-code](../../shared/GATE.md#g4), limit 8 of section 4; [section 1](../../shared/GATE.md#g1), the `envelope` row; [`const-language`](../../modules/const-language/MODULE.md#t7), the configuration of the envelope's blanking.
5. R5 — [kit-shared-gate-code](../../shared/GATE.md#g1), the `envelope` row of section 1; [section 2](../../shared/GATE.md#g2), item 9.
6. R6 — [`const-language`](../../modules/const-language/MODULE.md#t7), the configuration of the envelope's blanking; [its acceptance section](../../modules/const-language/MODULE.md#t10), item T7.
7. R7 — [`const-referencing`](../../modules/const-referencing/MODULE.md#t3), the row of [requirement A5.1](../requirements.md#a5-1) in section 3.
8. R8 — [`const-locations`](../../modules/const-locations/MODULE.md#t5), rule L-d; [its acceptance section](../../modules/const-locations/MODULE.md#t10), item T5; [kit-shared-gate-code](../../shared/GATE.md#g2), item 9 of section 2.
9. R9 — [kit-shared-gate-code](../../shared/GATE.md#g5), the row S164 of section 5 and the paragraph after the table.
