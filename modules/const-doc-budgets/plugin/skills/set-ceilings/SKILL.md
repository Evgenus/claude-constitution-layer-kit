---
name: set-ceilings
description: >
  Load this skill first, before a ceiling is set, raised, lowered or moved to error, and before a
  finding of the length check is fixed — every time, whether or not the number seems obvious. It
  sets a character ceiling for a group of documents from the repository's own history, and reads a
  finding of the check: a document over its ceiling, a note at warning, a ceiling refused for too
  few days of data, two ceilings holding one document. Use when a group of documents is to be
  measured for the first time, when the check reports after a write or in its scan, when a
  document must stand over its ceiling, and when the history report is read. Advisory: it shapes
  the numbers and the cuts; the check holds the count, the ceilings and the 30 days.
---

# Set ceilings

A document that grows with every change costs every reader, and every session that loads it. A
ceiling says how long a group of documents may be, in characters, as the project's conventions
count them — never tokens, never bytes, never lines. This procedure sets the number from what the
group was observed to need, and turns a finding into a cut. It is judgment from start to finish,
except the checks named in steps 1 and 2.

## 1. A ceiling comes from data

- **Group first.** A ceiling holds a group of documents named by path patterns: a kind of
  document — the path patterns of its policy, by a YAML alias where the dials file anchors
  them — or any other group, such as the project's CLAUDE.md or its skills. One document, one ceiling:
  two entries that match one document are refused.
- **Then the report.** Write the entry at `level: warning` with a generous number, then run the
  report over the history: `--scan --since <the first day of the window>`. It prints, per day,
  the longest document of the group, and per ceiling the window's longest document with the rule
  of thumb beside it.
- **The rule of thumb.** The window's longest document plus 10 %, rounded up to a multiple of
  1,000. No document is over the number on the day it is set, and the margin holds the small
  edits that make a frozen document longer. A number below the longest document is a target, not
  a ceiling: every document over it is red on day one.
- **The window.** Write the first and the last day of the data in `window`. The dates are
  declared, not proven: they say which data the number came from, and a reviewer checks them
  against the report.

## 2. Warning, then error

A ceiling stays at `level: warning` until 30 days of data stand behind it: the check refuses
`error` on a window shorter than 30 days. At warning an excess is a note that reaches the model
after the write and is listed by the scan, never red. After 30 days, run the report again, set
the number from it, widen the window, and move the level to `error`, in a change of its own that
names the number and the reason.

## 3. Reading a finding

- **Over a ceiling at error** — the finding names the document, its length, the ceiling and how
  much to cut. Cut or split; never squeeze. A shorter document that says less clearly is the
  wrong fix. Split along a seam the document already has: a long table into a document of its
  own, linked from the first; a rule restated from its home replaced by a link to that home; a
  procedure that loads only when its activity occurs moved into a skill.
- **Over a ceiling at warning** — the same numbers in a note. Cut or split before the ceiling
  blocks; the note repeats after every write until then.
- **A document already over,** written again for another reason: the finding repeats the length,
  not how much this write changed it. Cut what the first finding asked, or declare the document.

## 4. A document that must stand

An accepted record, a frozen comparison, a document the project will not rewrite: first make the
edits the project's rules allow for such a document, where they bring it under. Declare what they
do not reach in the dials file, as an entry of `departures` with `paths` for the document or its
number range, `allow` naming the ceiling it may exceed, and a one-line `reason`. The check still
measures it, and the other ceilings still apply. Never mark the document, and never take it out of
a ceiling's paths with a negated pattern, which hides it with no reason. An entry that lifts
nothing — it matches no document that a ceiling it names holds — is a note on every scan: remove
it or fix its names.

## 5. Lowering a ceiling

A ceiling is lowered only from data — the report showing the group smaller for a while — in a
change of its own with the number and the reason. A lower number that falls below a frozen
document needs that document's departure in the same change.

## What the check does not judge

Whether a long document says what it needs to, whether a split left each part readable, whether
the declared window is where the number came from, and a file written by a shell command, which
the scan sees and the hook does not. Those are the writer's and the reviewer's.
