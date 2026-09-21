#!/bin/sh
# const-referencing: the always-on rule about references in chat, printed at session start.
# Advisory: it shapes replies and checks nothing. Reads nothing; its only failure is printing
# nothing, which costs the session one rule and no verdict.
cat <<'RULE'
const-referencing (advisory): in chat, write every reference to a file, a section or a document as a markdown link wherever the file exists. A number, letter or key is a handle local to its message, decision or session: when a cite crosses that boundary, name the message or decision it came from.
RULE
