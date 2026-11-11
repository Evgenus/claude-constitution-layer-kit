---
name: promote-recurring-notes
description: >
  Load this skill first, before the same small question is answered again — every time, whether or
  not the earlier answers seem worth a ruling. It finds routine calls that keep recurring in
  commit messages on one theme and promotes the theme to a decision record or a documented
  procedure. Use when reviewing recent history before a release or a retrospective, when someone
  says "we keep deciding this", or when asked which commit notes deserve a ruling. Advisory: it
  shapes which themes are promoted and to what; no gate checks anything here.
---

# Promote recurring commit notes

Routine calls leave a line in the commit message and no record. That is right for one call
and wrong for the fifth on the same theme. A question answered again and again is a missing
ruling, and each answer may differ from the last. Recurring notes on one theme are the
standing signal to settle it once. This is a procedure for reading that signal. It is
judgment from start to finish; no check enforces it.

## 1. Gather the notes

Read recent history, bounded so it fits in context:

```bash
git log --since="3 months ago" --format="%h %s%n%b" --no-merges
```

The project may mark routine notes with a trailer: `note_trailer` under
`const-decision-records` in `constitution.yaml` names the key; absent or empty, there is
none. If it does, let git count the themes first:

```bash
git shortlog -ns --group=trailer:<the key> HEAD
```

The count sees only commits that carry the trailer, as the last paragraph of the message.
It treats two spellings of one theme as two themes. Read the log as well.

## 2. Cluster by theme

Group the notes by the question they answer, not by the files they touch. Some such
questions are: "where does this kind of file go", "who signs off on that kind of change",
"how do we name these". A theme
recurs when **three or more** notes answer the same question, or when **two** notes answer
it differently — disagreement is the stronger signal.

## 3. Promote

For each recurring theme choose one:

- **A ruling is missing** — the answers vary, or people keep asking. Price it and record
  it: use the `record-decision` skill of this plugin. The record cites the commits as the
  friction that earned it.
- **The answer is stable but undocumented** — everybody does the same thing and new
  sessions still have to rediscover it. Write it into the procedure or policy document
  where a reader would look. If that changes a policy or a procedure, the change itself is
  a `process` decision and gets its record.
- **Neither** — the notes merely share a word. Leave them.

## 4. Report

List every theme found, with its commits, and what you did or propose for each. Include
the themes you left alone, so the reader can disagree. Propose; at recorded stakes the
decider chooses.
