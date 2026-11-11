---
name: ask-or-decide
description: >
  Load this skill first, before the reply is written, every time a message will put options, a
  recommendation or a question to the user — a choice of design, of mechanism, of wording that
  binds, of what to do next — whether or not the shape seems known. It decides whether a choice is
  the user's to make or the session's, and when it is the user's, puts it as one decision per
  message in a fixed shape: lettered options, each with Pros: and Cons: sub-bullets, one
  recommendation, the decider named. Use when a request has more than one plausible reading, when
  a slot of a template, a dial or a plan is open, when a delivered plan or document would
  otherwise carry an open question, and when the user says an argument never reached them.
  Advisory: judgment shaped in prose; the plugin's hook holds only the marker half of the
  no-deferred-question rule, the rest is yours.
---

# Ask or decide

A question asked below its price costs the person asked a turn for nothing. A call made above
its price costs the next session the reasoning. This procedure prices the question first, then
shapes it. It is judgment from start to finish, and it is yours — except the one deterministic
slice named in step 5, which the plugin's hook holds.

## 1. Price it: is this the user's to decide?

Ask at **recorded stakes**, or at a **genuine blocker**. At recorded stakes the choice rules on a
policy, a procedure, a harness, on what a user sees, or on a structure hard to reverse. The
stakes levels are defined by the constitution's conventions page the project adopted. Nothing here
redefines them. A genuine blocker is a fact only the user holds, without which the work cannot
proceed. Below that line, make the reasonable call, do the work, and put one line in the commit
message saying what was chosen and why. A question that should not have been asked is the first
defect. A call that should have been asked is the second. The line is drawn by examples, not by
criteria. Each pair reads *decide and note / ask*:

1. Which of two directory names holds a scratch file → decide / where the project's decision
   records live and how they are numbered → ask.
2. The wording of a commit message, the name of a helper nobody else calls → decide. / The name of
   a dial, a trailer key or a flag that others will type → ask.
3. A fact you can find by reading the tree, the documents or the history → find it, never ask. /
   A fact only the user holds — who decides, which project, a date — → ask. If the user is
   absent, halt that part behind a named blocker.
4. Two readings of a request that lead to the same work → proceed on the stated reading, restated
   first. / Two readings that lead to materially different work → ask. A material assumption is a
   question, not an assumption.

The project's own line comes first. Read `boundary_examples` under `const-questions` in
`constitution.yaml`, the project's own pairs, `{ask: …, decide: …}`. Absent or empty, the pairs
above apply. Read also `preferences` beside it, a list of entries. Each entry names a `decider` and
the topics they want to be asked about (`ask`) even below the line. It names the topics they want
decided and noted (`decide`) even above it. It also names how they take a pick (`pick`: `tool`, the
default, or `letter`). The entry of the person you are working with overrides the pairs on its
topics. Absent or empty, the pairs alone apply, and at the first choice at recorded stakes ask who
decides. Read both as written; nothing validates them.

## 2. Derive the question; never improvise it

Questions come from the artifact's open slots, in document order. Such a slot is the next
unfilled template section, the next inline `[decide: …]` marker, the next missing dial, the next unresolved row.
Name the slot the question answers. "While we are at it" is not a slot: note it as deferred, with
the signal that would reopen it, and move on.

- **Closed vocabulary first.** Where the slot's values are an enum, a dial's listed values or a
  policy's list, the options are exactly that set; invent nothing beside it. Free text only for
  a genuinely open value — a title, a path the project owns — with the default proposed.
- **Default with override.** A slot with a sensible default is asked as "default is X — accept
  or override?". An override carries a one-line reason, kept in the record or the commit note.

## 3. Vague or context-foreign input: restate before acting

A request may show any sign of ambiguity, or not obviously fit the current context. Then open
the reply with the reading taken — "I read this as: …". Where several readings are plausible,
name them and the one chosen. Ask only above the line of step 1; otherwise proceed on the stated
reading. Never guess silently and never elaborate in an unrequested direction.

## 4. One decision per message, in this shape

Never bundle. A simple factual clarification — one fact, answered in a word — is a plain
one-line question and takes none of this shape. A real choice takes all of it, in the chat
message:

- **Lettered.** Options are lettered **A, B, C…** — capital letters, so an option is never confused with a
  numbered finding, step or assumption. Each option is a bullet: the bold letter and title plus a
  one-sentence description on the first line. Beneath it are two indented sub-bullets, **Pros:** and
  **Cons:**, one prose line each, several points joined by semicolons. They are never inline in the
  description, never a table, never a third level.
- **One recommendation.** Then exactly one recommendation with its reasoning, and the **named decider**.
- **The tool.** Fewer than five options, and the decider's `pick` is `tool`: the platform's question tool
  follows the message and collects the pick only. The tool holds a one-line question, and each
  option is its letter plus a short label, at most one clause of description. The pros, cons and
  recommendation never go inside the tool. Five or more,
  a `pick` of `letter`, or a session where the tool is not offered: chat only, the user answers
  with a letter.
- **Too complex.** A trade-off too complex for this shape — options that need a scored table — is reported as
  such. Do not force it into the shape and do not improvise a scoring method.

**The argument must reach the user.** Text written in the same turn as a tool call is not always
rendered for the user. Once the user reports an argument missing, every later decision in that
session ends the turn on the chat message. The pick is then collected by letter, without the
tool.

## 5. No deferred question in a deliverable

A delivered plan or document holds resolved decisions only. Where a decision is open and the
decider is absent, the affected part halts behind an explicit blocker — "blocked: <who> must
decide <what>". It is never an open question, a `TBD` or a "to be agreed" inside the finished
deliverable. A draft whose own convention marks open slots inline is the one exception, while it
is a draft. The marker half of this rule is held by the plugin's hook. A Markdown write carrying
an open-question marker (`[decide:`, `TODO`, `TBD`, `FIXME` by default, outside code) is blocked
with the fix in the message. Or it is reported and let through, where the project set the hook to
warn. The prose half is judgment.

## 6. What the answer leaves behind

A routine answer is one line in the commit message saying what was chosen and why. A recorded
answer is the conventions page's to record. When a module that writes decision records is
installed, its skill writes the answer down as it was argued. It writes the options, pros and cons,
the recommendation, the choice and who made it.
