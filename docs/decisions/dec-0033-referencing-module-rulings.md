---
id: dec-0033-referencing-module-rulings
type: task-record
title: Rulings of the const-referencing authoring — a move repairs what it breaks; the scan is the gate, the check after a write is feedback; heading-derived anchors are a finding
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# Rulings of the const-referencing authoring

## Context

The fourth module, [`const-referencing`](../requirements.md#const-referencing), was authored on 2026-09-21 and 2026-09-22 from its research comparison ([res-0004-const-referencing](../research/res-0004-const-referencing.md)) and the rows of [aspect A5](../requirements.md#a5) homed in it. Ten questions were put to the decider in chat, one per message, each with lettered options; the rest was derived by the authoring session, or found by its validations, and is listed in section 11 for the decider to override before the yes. One answer went against the session's recommendation (section 4), four overturn what the matrix or the module's specification said (sections 2, 5, 9, 10), and one adds a row (section 1). The module is the first gate of the kit wired to two tool events, the first that calls a third-party binary, and the first with a second entry point.

## 1. Whether "repaired by tooling on a move" becomes a row

The specification said an id cite is "repaired by tooling on a move", in one clause and with no row, so shipping the repair would have been scope creep and not shipping it left the clause unmet ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)). The kit had paid for the absence four times: a catalogued item's renumbering, a record's deletion, the template's links re-levelled in every copied module, and its largest rename done by hand. The comparison found no scriptable tool that moves a Markdown file and repairs the links to it.

- **A. A new row, with a move act in the module's script.**
  - **Pros:** the friction is earned; nothing can be adopted; the move's test of correctness — no reference is broken — is this module's invariant, so its gate is the move's proof.
  - **Cons:** the largest single piece of the module; it needs a command line beyond the gate's two modes.
- **B. A new row, carried by a skill procedure only.**
  - **Pros:** no code beyond the gate.
  - **Cons:** the rewrite stays hand work, and re-relativizing a moved file's own links by hand is the part that goes wrong.
- **C. No row; the clause reworded to "repaired by hand, proven by the scan".**
  - **Pros:** the smallest module.
  - **Cons:** the friction signal has already fired four times.

<a id="r1"></a>**R1.** The decider chose A and widened it in their own words: "move/rename as feature (might be script or command) + repair after manual move + check for consistency". [Requirement A5.8](../requirements.md#a5-8) is added: one act moves a document and rewrites the inbound links and the moved file's own relative links; after a move made by hand the same repair runs from the two paths, or from the envelope alone where a link's text is a governed id; links inside code are not rewritten, and mentions in prose are listed for a human, never rewritten; changing an `id` is not a move. The rewrite is advisory — a generator; its completeness is a gate: each act ends with the scan of the whole tree and exits with its verdict.

## 2. Where the check of resolution runs at write time

The matrix said "CI on PR". The comparison found that a document not yet on disk cannot be shown to lychee faithfully — on standard input a same-document link is reported broken — and that a `PostToolUse` hook exiting 2 cannot block, while its stderr reaches the model word for word; and it measured lychee at about 52 ms for the kit's whole tree.

- **A. The scan only.**
  - **Pros:** what the matrix says; one handler.
  - **Cons:** a break is found one commit later, or at the pull request; until the kit has CI, only when someone remembers.
- **B. The scan as the gate, and the same whole-tree check after each write as feedback.**
  - **Pros:** a break in *another* document — the kind an own-document check never sees — is reported in the turn that causes it; one code path; the cost of an interpreter's start.
  - **Cons:** a second event in the shared code; `block` where nothing can be blocked; a move through the shell is still unseen.
- **C. A blocking `PreToolUse` check of the written document's own links by a resolver of the module's own.**
  - **Pros:** it blocks.
  - **Cons:** two resolvers to keep agreeing; forward references refused; inbound breaks unseen.

<a id="r2"></a>**R2.** B. The scan is the gate for resolution. After each `Write` or `Edit` of a covered document the same whole-tree check runs and reports, as deterministic feedback declared as not blocking, the findings that involve the written document — its own links, and other documents' links into it. [Requirement A5.3](../requirements.md#a5-3) says so. The decider asked whether lychee is used under B: it is, in every session, and its absence is a configuration failure that names the install.

## 3. How the move and repair acts reach the command line

[kit-shared-gate-code](../../shared/GATE.md) fixed two modes, hook and scan; the third module had deferred the same seam.

- **A. Module-declared modes in the shared command line.**
  - **Pros:** one entry point, one guard.
  - **Cons:** a generic mechanism with one user; a checker with a flag that edits the tree.
- **B. A second entry point in the module, the shared guard split from the gate's parser.**
  - **Pros:** a file named for moving that rewrites, beside a file named for checking that never does ([law 5 of CLAUDE.md](../../CLAUDE.md#law-5)); gate-script rule 1 of the template foresees a second entry point; the gate's interface stays two modes.
  - **Cons:** the shared code is touched; two entry files carry the floor check.
- **C. A standalone script with a guard of its own.**
  - **Pros:** nothing shared changes.
  - **Cons:** the guard, the exit codes and the log written twice — what [dec-0025-shared-gate-code-linked](dec-0025-shared-gate-code-linked.md) exists to prevent.

<a id="r3"></a>**R3.** B. The mover is `move-document`, a second entry point; the shared code offers the single guard to any entry point — `cli.guarded` — and `cli.run` is a gate's way into it, unchanged for the three shipped gates.

## 4. What decides which documents the gate covers

- **A. The module's own dial, independent of policies** — `territories`, default every Markdown file git lists.
  - **Pros:** a broken link is broken whether or not a policy governs the file; works with no configuration; no index per write; the module reads only its own namespace.
  - **Cons:** a consumer who wants only governed documents restates their territories.
- **B. Policy resolution.**
  - **Pros:** one declaration of territory for all gates.
  - **Cons:** covers nothing without a root policy, and never a README.
- **C. Both: the own dial, and `governed_only: true` to narrow it to what a policy governs.**
  - **Pros:** serves both kinds of consumer.
  - **Cons:** two code paths and two sets of fixtures for a need no consumer has voiced.

<a id="r4"></a>**R4.** C, against the session's recommendation of A; the objection — machinery for a failure nobody has hit — was stated before the choice and stands recorded here. `territories` defaults to `["*.md"]`; `governed_only` defaults to `false`, needs `root_policy` when `true`, and counts the policies themselves as governed. Coverage decides whose links are judged: a link from a covered document to any file must resolve.

## 5. Whether a link through a heading-derived anchor is a finding

The matrix had [requirement A5.2](../requirements.md#a5-2) as advisory. The comparison found one deterministic slice — a fragment that is not among the explicit anchors of a covered target — and found lychee looser than a forge in two places: it compares fragments in lower case, and it accepts a heading's `{#key}` attribute, which a forge shows as text. None of the kit's 706 fragment links went through a heading.

- **A. A gate inside the whole-tree check, with a dial for adoption.**
  - **Pros:** the rule's one mechanical slice is checked; both gaps closed; one code path with resolution.
  - **Cons:** a new consumer's first scan may be red in hundreds of places until the dial is set.
- **B. A, and blocking at `PreToolUse` where the target exists.**
  - **Pros:** such a link never lands.
  - **Cons:** the lint stops being a function of one document's text.
- **C. Advisory, as the matrix said.**
  - **Pros:** nothing to build.
  - **Cons:** the drift is silent until a heading is reworded — the failure the row names.

<a id="r5"></a>**R5.** A. A link whose fragment is not among the explicit anchors of a covered Markdown target is a finding of the whole-tree check; the dial `heading_anchors: allow` switches it off — the adoption path. An anchor cited in another case than it is written is a finding whatever the dial says. [Requirement A5.2](../requirements.md#a5-2) says so.

## 6. How the syntax lint gets its vocabulary

The kit's bare forms — a module's number, a requirement row, a kernel section, a numbered law — are project content ([law 2 of CLAUDE.md](../../CLAUDE.md#law-2)). Three checks need none: a governed id in backticks that is no link, a link whose text is a governed id and whose target is another file, a path on one machine.

- **A. A dial `lanes` of `{pattern, names, fix, home}`; the reason is the module's fixed text.**
  - **Pros:** every finding still states what, why and the fix ([law 6 of CLAUDE.md](../../CLAUDE.md#law-6)); the kit's own lint can move into the module.
  - **Cons:** two thirds of a lane finding's text is the consumer's.
- **B. The three universal checks only.**
  - **Pros:** every text is the module's.
  - **Cons:** every consumer re-invents the masking; the kit keeps two reference gates.
- **C. A, with the reason configurable too.**
  - **Pros:** the most flexible.
  - **Cons:** why a rule exists becomes configuration.

<a id="r6"></a>**R6.** A. With it, as the session proposed and the decider accepted: the regions masked are the YAML block that opens the file, fenced and indented code, HTML comments and code spans, so a document may show a retired form inside code; the dial `bare_ids: allow` switches the id-in-backticks check off, for a project whose ids are everyday words; the preference half of [requirement A5.1](../requirements.md#a5-1) — an id where one exists — stays advisory.

## 7. What `severity` means where nothing can be blocked

- **A. One dial, one meaning — how loud.** `block`: both handlers exit 2. `warn`: both exit 0 with the finding in one JSON object.
  - **Pros:** one switch for adoption; the shared report serves both.
  - **Cons:** the word `block` is inexact after the write.
- **B. `severity` governs the lint only; the check after a write always exits 2.**
  - **Pros:** the word stays exact.
  - **Cons:** no quiet adoption path for resolution.
- **C. A second dial for the handler after the write.**
  - **Pros:** exact names.
  - **Cons:** a dial before its friction; `off` would remove the half chosen in section 2.

<a id="r7"></a>**R7.** A, with the inexactness said where a reader looks for it: after the write `block` blocks nothing, and the gate for those findings is the scan.

## 8. What happens to the kit's interim reference gate

`scripts/check-references.sh` did four things: the kit's bare forms, the path on one machine, lychee over every Markdown file, and one check with no counterpart — a file that is not Markdown naming a decision record that does not exist, which no link checker follows.

- **A. The module replaces the script whole; the fourth check becomes an optional, scan-only dial.**
  - **Pros:** one reference gate; the kit's live proof exercises every part of the module; the friction was earned here, by the carry audit of 2026-09-19.
  - **Cons:** it generalizes from one consumer; a pattern also matches examples; deleting a script needs a spoken yes.
- **B. The module replaces the Markdown half; a small kit-only script stays.**
  - **Pros:** the module stays about Markdown.
  - **Cons:** two gates for good.
- **C. The script stays whole beside the module.**
  - **Pros:** a second opinion.
  - **Cons:** two sets of texts drifting; the kit is then not consumer zero of its own module.

<a id="r8"></a>**R8.** A. The dial `mentions` — a list of `{pattern, files}` — declares how a document's id looks outside Markdown; in the scan every match in a file git lists that is no Markdown, no link and not binary must be a covered document's id. The module reads [requirement A5.3](../requirements.md#a5-3) so: a governed id named outside Markdown is a reference where the project declares its form.

<a id="r9"></a>**R9.** The interim script stays the gate of [requirement A5.6](../requirements.md#a5-6), and the baseline the module's scan is compared with, until the module is proven live in this repository. It is then deleted on the decider's spoken yes, given for that act, and the texts that name it are amended in the same change. The proof was made on 2026-09-22 — the scan and the script agreeing on every kind of break they share, and on the one gap the decider's question found, closed by R21 — and the yes was given in chat the same day: "yes, delete it and amend the texts".

## 9. What carries the rule about references in chat

The matrix said a skill. A skill's text enters context when its description matches an activity, and writing a reply is none.

- **A. A `SessionStart` hook prints the rule; the skill carries the authoring procedure.**
  - **Pros:** the rule is in context where replies are written; it is the template's own carrier for always-on advisory content.
  - **Cons:** a third handler; its characters are spent in every session.
- **B. The skill alone.**
  - **Pros:** no always-on cost.
  - **Cons:** the rule is absent exactly when it applies.
- **C. A, and a `Stop` hook inspecting each reply.**
  - **Pros:** the one deterministic slice of the chat half.
  - **Cons:** noisy by the comparison's account; no consumer has reported the friction.

<a id="r10"></a>**R10.** A: two sentences, 297 characters, printed at session start with no matcher, so they return after a compaction or a clear; advisory. [Requirement A5.7](../requirements.md#a5-7) names the carrier. C is deferred with its signal.

## 10. Whether the consumer configures lychee

The specification listed "lychee config" as a dial. The comparison found, and the session re-ran, that a `lychee.toml` in the working directory is loaded unasked — a file with two broken links exited 0 — that a `.lycheeignore` is honoured even under `--config` unless lychee is started elsewhere, and that lychee exits 2 on a broken link and on bad usage alike.

- **A. No pass-through: the module owns the invocation.**
  - **Pros:** the verdict depends on the repository and the module's namespace alone; no false green from a stray file.
  - **Cons:** lychee's remapping and excludes are out of reach through this gate.
- **B. A dial naming a configuration file.**
  - **Pros:** a declared escape hatch.
  - **Cons:** a key there can switch off what the gate promises, in a format that changes between versions.
- **C. lychee's default behaviour.**
  - **Pros:** nothing to build.
  - **Cons:** the silent false green, and a verdict read from outside the module's namespace ([kernel §6](../constitution/CONVENTIONS.md#k6)).

<a id="r11"></a>**R11.** A. lychee, 0.24.2 or newer, is found and its version read at each run, started in an empty scratch directory with the module's own configuration file and its inputs on standard input; exit 2 is a finding only with a parsed report. None of its options is a dial. A named dial for one option is deferred with its signal.

## 11. Rulings taken by the authoring session

No real choice was put to the decider on these; each is the session's derivation, open to override before the yes.

<a id="r12"></a>**R12.** The check after a write examines the whole tree and reports only the findings that involve the written document, the first twenty printed — fewer where twenty would pass the platform's cap — and the total in the count line: on a repository with older breaks every write would otherwise repeat all of them. The scan reports everything.

<a id="r13"></a>**R13.** The lint runs before the write and nowhere else at write time; the whole-tree check runs after it and in the scan. An event the gate is not wired to is a configuration failure.

<a id="r14"></a>**R14.** A document whose envelope nobody can read carries no id here and is judged on its references all the same; saying that the envelope is unreadable is another gate's.

<a id="r15"></a>**R15.** The mover repairs the covered documents and no others; it refuses, changing nothing, when the target exists, the source is not a file git lists, a path leaves the repository, or no dials file exists — without one the scan that proves a move cannot run; the id repair leaves alone an id two documents carry; it does not stage its rewrites; what names the old path outside a link's destination — in a covered document or in any other text file git lists — is listed and never changed.

<a id="r16"></a>**R16.** No command and no agent: a move is asked for in words and the skill carries it. The mover's message keys are V1 to V5, since the letter a module's number is written with would trip the kit's own lane.

<a id="r17"></a>**R17.** A negated pattern takes a tree out of `territories` as `!dir/**`; `!dir/` names the directory alone, and the files inside still match. Found by experiment while the install note was written, against what the session had told the decider under section 4.

<a id="r21"></a>**R21.** A path on one machine is read in code and comments too; only the YAML block that opens the file is left out. Put to the decider on 2026-09-22, when they asked whether the module covers all the interim script gave: it did not — the session had stretched the masking accepted under section 6 from bare forms to this check without asking, and a probe showed the script red and the scan green on a home-directory path inside a code span. Options: A, the check reads code; B, the mask stays, and the kit's rule against local paths is held by review inside backticks; C, a dial. The decider chose A: a bare form in code is an illustration, a local path leaks a machine's layout however it is set.

<a id="r22"></a>**R22.** Two rows gain the words their checks already stood under, so that neither check is content beyond its row ([law 4 of CLAUDE.md](../../CLAUDE.md#law-4)): [requirement A5.1](../requirements.md#a5-1) now says that a reference never names a path on one machine, and [requirement A5.3](../requirements.md#a5-3) that a governed id named outside Markdown is a reference where the project declares its form. Found by the first fresh-context validation; both checks were ruled by the decider (R21, R8), the rows had not followed.

<a id="r23"></a>**R23.** From the first fresh-context validation, pinned to 22ab5da — twenty findings, nine of fourteen mutants alive — the behaviour that changed:

- **the mover** asks everything that can refuse before it moves anything, the link checker and the root policy of `governed_only` among it, and a failure after the move closes by saying that the act stopped midway, never that nothing was changed;
- **it keeps line endings** and leaves a file that is not UTF-8 alone, saying so;
- **a usage of a reference definition** is a link, judged by what its label opens, and never rewritten, its definition being the link;
- **a fence indented under a list item** is code;
- **a write to a document that is not covered** still has the covered links it broke reported after it;
- **a key of the module's namespace that is no dial** is a configuration failure;
- **message key R4** asks for a user's directory and something inside it;
- **one document's cost** is linear in its size.

<a id="r26"></a>**R26.** Message key R4 gets the switch the two other universal checks have: the dial `local_paths: refuse | allow`, default `refuse`. Put to the decider on 2026-09-22 after the first validation showed an ordinary document message key R4 blocks with no way out — a README whose Dockerfile fence sets the working directory to a home directory inside the container. Options: A, the dial; B, fences masked for the `/home/` form only, which would half reopen R21; C, the limit stated and nothing built. The decider chose A: the kit keeps `refuse`, a consumer gets the same adoption path as for `bare_ids` and `heading_anchors`.

<a id="r25"></a>**R25.** From the second fresh-context validation, pinned to 822c070 — thirteen findings, twelve of thirty-one mutants alive — the behaviour that changed:

- **a fence closes at its opener's depth**, a tab counts as four columns, and a fence that shows a deeper fence is content to its own end (the first validation's fix had let any closing fence end any fence);
- **a footnote** is no link;
- **the report after a write** is cut by characters as well as by count, so the count line survives the platform's cap;
- **the mover** refuses a new path that names a directory, that drops the `.md` ending, or whose source is a symbolic link, allows a rename in case alone, and repairs a document moved out of coverage;
- **the cost of code spans** is linear.

<a id="r24"></a>**R24.** The handler after the write is a `gate` in kind — deterministic, red means fix — at a moment that cannot block, and is declared so; it is not `advisory`, since nothing in it shapes judgment. The validation had found "deterministic feedback" to be a third kind beside the two [law 5 of CLAUDE.md](../../CLAUDE.md#law-5) names.

<a id="r27"></a>**R27.** The admission rule of the shared gate code gains a clause: a part already shared may be widened for one module where the widening keeps a rule the part carries for all — one guard, one pipeline, one fixture subject — and defaults to what the other modules pass, so they change nothing. That is what R18–R20 did, and the carry audit's confirming reader found the clause stated in the shared-code document alone, which its own policy governs and which cannot widen that policy: the clause now stands in rule 2 of the policy and in CLAUDE.md, and the document echoes it.

## 12. The shared gate code, met by a fourth consumer

Each seam was fixed at the source with the fixtures of all four modules green.

<a id="r18"></a>**R18.** The tool event keeps its name. For an event after the write the pipeline reads the document from disk and reconstructs nothing, with a skip reason of its own for a file that is not there; the hook report takes the event's name, which the `warn` channel repeats, and a count line of the module's own, both defaulting to what a gate before the write passes; the text of the unusable-input failure says "one tool event".

<a id="r19"></a>**R19.** The single guard is offered to a second entry point: `cli.guarded(identity, mode, body, could_not_run)`, with `Mode.ACT` stamping the log and the closing line the entry point's own, since "0 documents examined" is a gate's.

<a id="r20"></a>**R20.** The fixture subject gains two fields, defaults unchanged: what the count line says of a README with no envelope at the repository's top, and whether the gate judges envelopes — one that does not leaves the item about an unreadable envelope out and proves in its own items that such an envelope is no crash.

## Applied

On the branch `work/const-referencing`, in the commits before this record and the one that creates it: the module's [MODULE.md](../../modules/const-referencing/MODULE.md), its scripts, hooks, skill, install note and fixtures; [requirement A5.8](../requirements.md#a5-8) added, the enforcement cells of [A5.2](../requirements.md#a5-2), [A5.3](../requirements.md#a5-3) and [A5.7](../requirements.md#a5-7) amended, the module's specification replaced by its stub; the shared gate code and [its document](../../shared/GATE.md); the research comparison. The interim script was deleted after the live proof, on the yes of R9, and the texts that named it as the gate were amended in that commit.

## Carry list

1. R1 — [requirement A5.8](../requirements.md#a5-8); the last row of [§3](../../modules/const-referencing/MODULE.md#t3), the two `script (py)` rows of [§6](../../modules/const-referencing/MODULE.md#t6), and limits 11 and 12 of [§9](../../modules/const-referencing/MODULE.md#t9) of the module's document.
2. R2 — [requirement A5.3](../requirements.md#a5-3); its row in [§3](../../modules/const-referencing/MODULE.md#t3), row E3 and limits 1 to 4 of [§9](../../modules/const-referencing/MODULE.md#t9).
3. R3 — the `script (py)` row of the mover in [§6](../../modules/const-referencing/MODULE.md#t6); item 1 of [kit-shared-gate-code §2](../../shared/GATE.md#g2).
4. R4 — the rows `territories` and `governed_only` of [§7](../../modules/const-referencing/MODULE.md#t7); the row of [requirement A5.3](../requirements.md#a5-3) in [§3](../../modules/const-referencing/MODULE.md#t3). That the choice went against the recommendation: history only.
5. R5 — [requirement A5.2](../requirements.md#a5-2); its row in [§3](../../modules/const-referencing/MODULE.md#t3), the rows R6 and R7 of the error-message table in [§6](../../modules/const-referencing/MODULE.md#t6), the row `heading_anchors` of [§7](../../modules/const-referencing/MODULE.md#t7).
6. R6 — the rows of [requirement A5.1](../requirements.md#a5-1) and [requirement A5.6](../requirements.md#a5-6) in [§3](../../modules/const-referencing/MODULE.md#t3); the rows `lanes` and `bare_ids` of [§7](../../modules/const-referencing/MODULE.md#t7); row R1 of the error-message table in [§6](../../modules/const-referencing/MODULE.md#t6).
7. R7 — the row `severity` of [§7](../../modules/const-referencing/MODULE.md#t7); row E3 and limit 1 of [§9](../../modules/const-referencing/MODULE.md#t9).
8. R8 — the row of [requirement A5.3](../requirements.md#a5-3) in [§3](../../modules/const-referencing/MODULE.md#t3); the row `mentions` of [§7](../../modules/const-referencing/MODULE.md#t7); row R8 of the error-message table in [§6](../../modules/const-referencing/MODULE.md#t6).
9. R9 — the script is gone, and its absence is the carried state; what the gate is now: the cell of [requirement A5.6](../requirements.md#a5-6) and the rule "References are clickable" in [CLAUDE.md](../../CLAUDE.md). The proof and the yes of the day: history only.
10. R10 — [requirement A5.7](../requirements.md#a5-7); its row in [§3](../../modules/const-referencing/MODULE.md#t3), the hook row and the always-on slot of [§6](../../modules/const-referencing/MODULE.md#t6); item 1 of [§12](../../modules/const-referencing/MODULE.md#t12).
11. R11 — platform fact 8, the `configuration` row and rows X1 to X3 of [§6](../../modules/const-referencing/MODULE.md#t6); the closing sentence of [§7](../../modules/const-referencing/MODULE.md#t7); item 3 of [§12](../../modules/const-referencing/MODULE.md#t12).
12. R12, R13 — the row of [requirement A5.3](../requirements.md#a5-3) in [§3](../../modules/const-referencing/MODULE.md#t3); row F9 of the error-message table in [§6](../../modules/const-referencing/MODULE.md#t6); limit 4 of [§9](../../modules/const-referencing/MODULE.md#t9); [the gate's entry file](../../modules/const-referencing/plugin/scripts/check-references.py).
13. R14 — the last item of [§11](../../modules/const-referencing/MODULE.md#t11).
14. R15 — limits 11 and 12 of [§9](../../modules/const-referencing/MODULE.md#t9) and row V5 of the error-message table in [§6](../../modules/const-referencing/MODULE.md#t6); [the mover's entry file](../../modules/const-referencing/plugin/scripts/move-document.py).
15. R16 — the `command` and `agent` rows of [§6](../../modules/const-referencing/MODULE.md#t6). The reason for the keys' letter: history only.
16. R21 — the row of [requirement A5.1](../requirements.md#a5-1) in [§3](../../modules/const-referencing/MODULE.md#t3) of the module's document; [the gate's entry file](../../modules/const-referencing/plugin/scripts/check-references.py); step 2 of [the install note](../../modules/const-referencing/plugin/INSTALL.md). That the session had stretched the mask unasked: history only.
17. R22 — [requirement A5.1](../requirements.md#a5-1) and [requirement A5.3](../requirements.md#a5-3). That the rows had not followed: history only.
18. R23 — the rows of [requirement A5.1](../requirements.md#a5-1), [A5.3](../requirements.md#a5-3) and [A5.8](../requirements.md#a5-8) in [§3](../../modules/const-referencing/MODULE.md#t3) of the module's document; rows V1–V5 and C5 of the error-message table and platform fact 9 in its [§6](../../modules/const-referencing/MODULE.md#t6); the closing sentence of its [§7](../../modules/const-referencing/MODULE.md#t7); limits 5, 8 and 12 of its [§9](../../modules/const-referencing/MODULE.md#t9); [the mover's entry file](../../modules/const-referencing/plugin/scripts/move-document.py). The count of findings and mutants: history only.
19. R26 — the row `local_paths` of [§7](../../modules/const-referencing/MODULE.md#t7) of the module's document, the row of [requirement A5.1](../requirements.md#a5-1) in its [§3](../../modules/const-referencing/MODULE.md#t3), limit 8 of its [§9](../../modules/const-referencing/MODULE.md#t9); step 3 of [the install note](../../modules/const-referencing/plugin/INSTALL.md). The Dockerfile case: history only.
20. R25 — limits 8 and 12 of [§9](../../modules/const-referencing/MODULE.md#t9) of the module's document, rows V5 and F9 of the error-message table in its [§6](../../modules/const-referencing/MODULE.md#t6), platform fact 9 there. The counts: history only.
21. R24 — row E3 of [§9](../../modules/const-referencing/MODULE.md#t9) of the module's document.
22. R17 — [the install note](../../modules/const-referencing/plugin/INSTALL.md), step 3. That it corrects what was said in chat: history only.
23. R27 — rule 2 of [plc-0009-shared-code](../policies/plc-0009-shared-code.md#r2); step 4 of [CLAUDE.md](../../CLAUDE.md); the admission paragraph of [kit-shared-gate-code §1](../../shared/GATE.md#g1). That the clause first stood in the document alone: history only.
24. R18 — the `events` and `pipeline` rows of [kit-shared-gate-code §1](../../shared/GATE.md#g1), item 3 of [its §2](../../shared/GATE.md#g2), rows G1.7 and C12.4 of [its §3](../../shared/MESSAGES.md#g3).
25. R19 — item 1 of [kit-shared-gate-code §2](../../shared/GATE.md#g2).
26. R20 — item 8 of [kit-shared-gate-code §2](../../shared/GATE.md#g2).
