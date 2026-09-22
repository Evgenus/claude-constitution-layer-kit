---
id: dec-0034-research-and-policies-numbered
type: task-record
title: The research comparisons and the policies enter the catalog form — prefixes res and plc, thirteen documents renamed by one recorded migration
status: inactive
stakes: process
decider: Eugene Chernyshov
---

# The research comparisons and the policies enter the catalog form

## Context

On 2026-09-22 the kit numbered one kind, its decision records, under `const-catalogs.catalogs` in `constitution.yaml` ([dec-0017-records-numbered-now](dec-0017-records-numbered-now.md) made the migration; [dec-0029-catalogs-module-rulings](dec-0029-catalogs-module-rulings.md) moved the declaration into the module's own dial). Two other kinds the kit holds under `docs/` were named by slug alone. The research comparisons, four files named after their modules, had a gap in their naming rule: rule 2 of [plc-0005-research](../policies/plc-0005-research.md) keeps a superseded comparison while it is cited, so a second survey of one module needed a name the rule did not give. The policies, nine files, were cited by name without ambiguity — but a policy's id is also its namespace key in the dials file, the `root_policy` path and the value of `record_policies`, so any later numbering would rewrite the dials file as well as every link. The decider asked for both kinds to enter the catalog form. The cost stood at thirteen ids changed once, the deliberate breach of [kernel §1](../../kernel/CONVENTIONS.md#k1) that the records' migration had made, and about fifty link sites.

## Options

- **A. Both kinds, migrated now in one recorded change.** Two catalog entries, every existing file renamed by first-commit order, ids changed once, links and dial keys rewritten in the same work, a Number rule in each kind's policy, the `mentions` dial of module `const-referencing` extended so a policy key in the dials file must name an existing policy.
  - **Pros:** one regime for every kind the kit numbers; the mention check starts guarding the dial keys; the debt stops growing, and a policy or comparison can be cited by a bare number.
  - **Cons:** the largest migration so far, with the policy ids rippling into the dials file and every prose handle; the benefit for policies is thin, since nine documents added one at a time by recorded decisions are already cited by name.
- **B. Research only; policies keep their names.**
  - **Pros:** takes the kind that needs numbering, at a third of the cost; dial keys and prose handles for policies stay short.
  - **Cons:** leaves policies as the one kit-owned kind under `docs/` outside the form, and a later migration would be larger.
- **C. Both catalogs declared, existing files left as they are.**
  - **Pros:** no id changes.
  - **Cons:** not viable: the catalogs gate's K1 fires on an existing file whose name shows no number at its next edit, so all thirteen files become findings, or the catalogs run at `severity: warn` forever — the reason option A of the records' migration was rejected.

## Recommendation and choice

The session recommended A: the cost for policies is real but one-time, and the kit is consumer zero, so showing every numbered kind of its own under the module it ships is worth more than nine shorter handles. **Chosen: A,** by Eugene Chernyshov in chat on 2026-09-22, with two amendments to the proposal: the policies' prefix is `plc`, not `pol`, and the policy slugs drop the word `kit`, since every policy here is the kit's. The research prefix `res`, width 4 for both, and the numbering order were accepted as proposed. A translation table was shown and approved before any file changed.

## Ruling

**R1.** The research comparisons are a numbered kind: prefix `res`, width 4, one entry of `const-catalogs.catalogs` in `constitution.yaml` whose territory is the research policy's own by a YAML alias; id and stem are one name, `res-<nnnn>-<slug>`, the slug naming the module surveyed. The policy [plc-0005-research](../policies/plc-0005-research.md) carries the numbering rule, and with it the answer to its rule 2: a later survey of a module takes the next number and keeps its name beside the one it supersedes.

**R2.** The policies are a numbered kind: prefix `plc`, width 4, one entry of `const-catalogs.catalogs` whose territory is the root policy's own by a YAML alias; id and stem are one name, `plc-<nnnn>-<slug>`, the slug naming the kind governed and never the kit. The root policy [plc-0001-root-policy](../policies/plc-0001-root-policy.md) carries the numbering rule. A policy's namespace key in the dials file is its id and so takes the same form; a `plc-` or `res-` name written outside Markdown — for a `plc-` name: a namespace key, the `root_policy` path, `record_policies` — matches a pattern of the `mentions` dial of module `const-referencing`, whose scan reports one that is not an id a document the scan covers carries, the way it already reported `dec-` names.

**R3.** Numbers were allocated by first-commit order of the existing files, and where one commit added several, by the order the dials file listed their policies. Their ids changed once, in this migration — the second deliberate breach of the kernel's "never changes" rule after the records', entering the regime the kernel already requires while nothing outside this repository references the old ids. The allocation:

| # | old path and id | new path and id |
|---|---|---|
| R1 | `docs/research/const-meta-types.md`, id `research-const-meta-types` | `docs/research/res-0001-const-meta-types.md` |
| R2 | `docs/research/const-decision-records.md`, id `research-const-decision-records` | `docs/research/res-0002-const-decision-records.md` |
| R3 | `docs/research/const-catalogs.md`, id `research-const-catalogs` | `docs/research/res-0003-const-catalogs.md` |
| R4 | `docs/research/const-referencing.md`, id `research-const-referencing` | `docs/research/res-0004-const-referencing.md` |
| P1 | `docs/policies/kit-root-policy.md`, id `kit-root-policy` | `docs/policies/plc-0001-root-policy.md` |
| P2 | `docs/policies/kit-kernel.md`, id `kit-kernel` | `docs/policies/plc-0002-kernel.md` |
| P3 | `docs/policies/kit-intent-page.md`, id `kit-intent-page` | `docs/policies/plc-0003-intent-page.md` |
| P4 | `docs/policies/kit-decision-records.md`, id `kit-decision-records` | `docs/policies/plc-0004-decision-records.md` |
| P5 | `docs/policies/kit-research.md`, id `kit-research` | `docs/policies/plc-0005-research.md` |
| P6 | `docs/policies/kit-module-documents.md`, id `kit-module-documents` | `docs/policies/plc-0006-module-documents.md` |
| P7 | `docs/policies/kit-requirements.md`, id `kit-requirements` | `docs/policies/plc-0007-requirements.md` |
| P8 | `docs/policies/kit-rollout-plan.md`, id `kit-rollout-plan` | `docs/policies/plc-0008-rollout-plan.md` |
| P9 | `docs/policies/kit-shared-code.md`, id `kit-shared-code` | `docs/policies/plc-0009-shared-code.md` |

The nineteen files deleted from `docs/research/` on 2026-09-18 — eighteen surveys and their index — and the policy renamed and the one replaced before this day had never carried the form, so they hold no numbers: both catalogs start at 1.

**R4.** The files were moved by the move act of module `const-referencing`, one command per file, which repaired every inbound link and each moved file's own relative links and closed each move with a green scan of the whole tree. The mover lists an old path named outside a link's destination, which it does not rewrite, and listed six: four link texts in the module documents that showed a comparison's old path, the `root_policy` line of the dials file, and one backticked path in the carry-audit skill. By hand in the same work, those six and what the mover does not look for: every link text that showed an old id, rewritten to the new id across records, policies, `CLAUDE.md`, `shared/GATE.md`, the rollout plan and the carry-audit skill; the thirteen envelope ids; the eleven lines of the dials file that carry a policy's id, the `root_policy` line among the six. The carry audit then found, and the same work rewrote, four more link texts that still showed a comparison's old `research-` id, one in the context of each of four accepted records, and the path form of a comparison in step 2 of `CLAUDE.md`. No prose mention of an old id outside a link was found. One old form was left as written: item 2 of [dec-0010-module-research-per-module](dec-0010-module-research-per-module.md) states the path form the comparisons had — an accepted record is not edited, and R1 supersedes it. A reference-form migration under [kernel §5](../../kernel/CONVENTIONS.md#k5).

**R5.** From this record on, a new comparison and a new policy take the highest number their catalog has held plus one, provisional until the branch lands on main ([requirement A13.3](../requirements.md#a13-3)); this record is `dec-0034`.

## Applied

In the commits of the work `catalogs-research-policies`: the thirteen moves and their link repairs; the ids, the link texts, the dials file — two catalog entries, two aliases, nine keys, the root policy path, the records dial, two mention patterns — and rule 6 of the two policies. The kit-live proof is the catalogs scan over this repository: `dec up to dec-0033, plc up to plc-0009, res up to res-0004`, green, and the referencing scan green over 71 documents. The record is born `inactive`.

## Carry list

1. R1 — rule 6 of [plc-0005-research](../policies/plc-0005-research.md); [the dials file](../../constitution.yaml); step 2 of [CLAUDE.md](../../CLAUDE.md) for the research path's form and its reading list for the superseded comparison kept beside the current one.
2. R2 — rule 6 of [plc-0001-root-policy](../policies/plc-0001-root-policy.md) and, for the `res-` names, rule 6 of [plc-0005-research](../policies/plc-0005-research.md); [the dials file](../../constitution.yaml).
3. R3 — history only: the allocation and the one-time change of ids on the day.
4. R4 — history only: what was moved and rewritten on the day.
5. R5 — rule 6 of [plc-0005-research](../policies/plc-0005-research.md) and rule 6 of [plc-0001-root-policy](../policies/plc-0001-root-policy.md); the record's own number: history only.
