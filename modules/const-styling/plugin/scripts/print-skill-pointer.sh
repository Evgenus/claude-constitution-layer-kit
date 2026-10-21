#!/bin/sh
# const-styling: the always-on pointer to the module's skill, printed at session start and, as the
# context a subagent starts with, at every subagent's start, so that the skill is loaded at the
# moment it applies. Advisory: it shapes when the skill is loaded and checks nothing. Reads nothing
# but its one argument; its only failure is printing nothing, which costs a session the pointer and
# no verdict. The text holds no double quote and no backslash, so it stands in JSON unescaped.
pointer='const-styling (advisory): before writing a table, a diagram, a list, a formula, a heading below level three, a callout or a fenced block in a document, load the skill const-styling:style-defaults.'
if [ "$1" = "--subagent" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"%s"}}\n' "$pointer"
else
  printf '%s\n' "$pointer"
fi
