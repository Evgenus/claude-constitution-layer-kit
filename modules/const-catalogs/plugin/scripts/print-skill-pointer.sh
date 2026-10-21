#!/bin/sh
# const-catalogs: the always-on pointer to the module's skill, printed at session start and, as the
# context a subagent starts with, at every subagent's start, so that the skill is loaded at the
# moment it applies. Advisory: it shapes when the skill is loaded and checks nothing. Reads nothing
# but its one argument; its only failure is printing nothing, which costs a session the pointer and
# no verdict. The text holds no double quote and no backslash, so it stands in JSON unescaped.
pointer='const-catalogs (advisory): before creating a document of a kind the project numbers — a decision record, a task, an RFC — and when a write is blocked for its file name, id or number, load the skill const-catalogs:catalog-item.'
if [ "$1" = "--subagent" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"%s"}}\n' "$pointer"
else
  printf '%s\n' "$pointer"
fi
