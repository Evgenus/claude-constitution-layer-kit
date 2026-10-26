#!/bin/sh
# const-<aspect-name>: the always-on pointer to the module's skill, printed at session start and, as the
# context a subagent starts with, at every subagent's start, so that the skill is loaded at the
# moment it applies. Advisory: it shapes when the skill is loaded and checks nothing. Reads nothing
# but its one argument; its only failure is printing nothing. Keep the text free of double quotes
# and backslashes, so that it stands in JSON unescaped. Delete this file where the module ships no
# pointer line, with its two entries in hooks.json.
pointer='const-<aspect-name> (advisory): before <the moment>, load the skill const-<aspect-name>:<skill>.'
if [ "$1" = "--subagent" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"%s"}}\n' "$pointer"
else
  printf '%s\n' "$pointer"
fi
