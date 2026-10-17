#!/bin/sh
# const-task-close: the always-on pointer to the module's skill, printed at session start and, as the
# context a subagent starts with, at every subagent's start, so that the skill is loaded at the
# moment it applies. Advisory: it shapes when the skill is loaded and checks nothing. Reads nothing
# but its one argument; its only failure is printing nothing, which costs a session the pointer and
# no verdict. The text holds no double quote and no backslash, so it stands in JSON unescaped.
pointer='const-task-close (advisory): before the first edit of any change — a rename, a refactor, any edit of more than one file — and when a change is done, load the skill const-task-close:commit-before-edit; when a task, a branch or a pull request is finished, merged or handed off, load the skill const-task-close:close-task.'
if [ "$1" = "--subagent" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"%s"}}\n' "$pointer"
else
  printf '%s\n' "$pointer"
fi
