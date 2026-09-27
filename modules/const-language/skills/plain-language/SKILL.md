---
name: plain-language
description: >
  Write the prose of a governed document in plain English for a reader whose first language is
  not English — short sentences, short words, no idiom, the actor named — and read a finding of
  the language check: a document over the grade ceiling, a sentence over the word limit, a
  construction plain language avoids, a word with a plain replacement, passive voice. Use when
  writing or editing prose in a document the check covers, when the check reports after a write
  or in its scan, when a phrase the project must keep is flagged, when adopting the check on a
  repository with many findings, and when setting its thresholds. Advisory: it shapes the
  writing; the check holds the numbers and the lists.
---

# Plain language

A document is read by people whose first language is not English, and by a model that reads
it in every session. Both pay for every long sentence, every long word and every idiom. This
procedure shapes the prose before the check reads it, and turns a finding into a fix. It is
judgment from start to finish, except the check named in step 3.

## 1. Before writing

- **One idea per sentence.** A sentence carries one idea and stops. The project's limit is the
  words-per-sentence number of the check; when a sentence passes it, split it at a clause —
  "and", "which", "so that" — into two.
- **The short word.** The plain word is the one a reader meets first: `use`, not `utilize`;
  `before`, not `prior to`; `about`, not `with regard to`; `if`, not `in the event that`. The
  check names the plain word in its finding.
- **No idiom.** An idiom is a phrase whose meaning is not the meaning of its words: `hit the
  ground running`, `low-hanging fruit`, `circle back`. Say the plain thing.
- **Name who acts.** "The scan reports the finding", not "the finding is reported". The
  passive is right where the actor does not matter or is unknown; it is a register, and the
  project sets whether the check reports it, reds it or ignores it.
- **A term at first use.** A word of the project's own, or of the trade, is defined in one
  clause where it first appears.
- **Headings, code and tables are not prose to the grade**, but a heading is a sentence to
  the word limit: keep headings short.

## 2. What the grade measures

The check computes the Flesch–Kincaid grade of the document's prose — the years of schooling
the text assumes — from two counts: words per sentence and syllables per word. Nothing else
moves it. A document over the ceiling comes down by shorter sentences and shorter words; a
heading, a code span, a code block and a table cell are left out of the count.

## 3. Read a finding

The check runs after every write of a covered document and in its scan, `check-language.sh
--scan`. Each finding names the file and line, why the rule exists and the fix:

- **Over the grade ceiling**, reported at line 1: shorten the long sentences first, then the
  long words; the check prints the grade after the next write.
- **A sentence over the limit**: split it where the finding's echo shows it starts.
- **A construction plain language avoids**: say it in plain words, or drop it.
- **A word with a plain replacement**: write the plain word the finding names.
- **Passive voice**: reported as a note by default; name the actor where it helps.
- **A Vale comment in the document**: remove it. Nothing in a document switches a rule off;
  the check blanks the comment before it reads, and reports it.

A phrase the project keeps on purpose — a term of art the plain word would change — is named
in `const-language.exceptions` of `constitution.yaml`, one line per phrase, and the check stops
reporting it everywhere. A phrase of the project's own to forbid goes in `const-language.forbidden`;
a pair of its own in `const-language.simpler`. A document that must stand as it is written — an
accepted record, a frozen comparison — takes first the wording edits its policy allows, where the
constitution's conventions page lets that policy list them: a sentence split, a plain word. What
no such edit fixes is declared in `const-language.departures`, by path or by a pattern over its
kind, with the rules it may fail there and the reason in one line; the check still reads it for
every other rule, and nothing is written into the document.

## 4. Adopt the check on a repository

A repository with many findings does not turn every rule red on day one. The path: set the
thresholds the documents can bear today — `grade_ceiling`, `sentence_words` — and the rules the
project is not ready for to `warning` under `levels`, so every finding is reported and none is
red; rewrite the documents kind by kind; lower the numbers and raise the levels in steps, each
step a change of `constitution.yaml` with its reason in the commit. A document that must not be
edited — an accepted record, a frozen comparison — beyond the wording edits its policy allows is
brought under each step by those edits; what they cannot fix is declared as a departure in
`const-language.departures`, never marked and never taken out of the territory.

## 5. What the check does not judge

Whether a term is defined at first use, whether a sentence of twenty words holds one idea or
two, whether a passive was chosen, whether the prose is clear: judgment, yours. The check holds
the grade, the word count, its two lists and the passive's shape, and claims nothing else.
