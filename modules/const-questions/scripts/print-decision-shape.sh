#!/bin/sh
# const-questions: the always-on shape of a decision message, printed at session start.
# Advisory: it shapes replies and checks nothing. Reads nothing; its only failure is printing
# nothing, which costs the session one rule and no verdict.
cat <<'SHAPE'
const-questions (advisory): a choice put to the user takes one shape, in the chat message, one decision per message. Options lettered A, B, C…, each a bullet: the bold letter and title with a one-sentence description on the first line; beneath it two indented sub-bullets, **Pros:** and **Cons:**, one prose line each — never inline in the description, never a table. Then exactly one recommendation with its reasoning, and the decider named. A one-fact clarification is a plain line and takes none of this. Whether to ask at all, the tool or the letter, and the project's preferences are the skill ask-or-decide: load it before putting any choice.
SHAPE
