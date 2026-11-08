#!/bin/sh
# Kit tooling, never shipped in a module: the effect report of every module of this kit, over the kit's own
# sessions. The kit loads its modules from its own tree, through the marketplace its project settings declare,
# and never installs them, so `claude plugin list` names none of them and the shared entry,
# `python3 -m constitution_layer_kit.effect`, finds no report here. This script runs each module's own entry,
# `modules/<module>/plugin/scripts/effect-report.sh`, from the tree instead, in the order of the module
# folders, with the flags it is given; it adds no flag of its own. The entries import the shared package that
# pip installed for python3, as the kit's sessions do.
#
# Run from anywhere in the kit:
#   sh scripts/effect-reports.sh --transcripts ~/.claude/projects [--since <YYYY-MM-DD>] [--reader]
# The folder ~/.claude/projects holds every session's transcript; each entry keeps those whose folder lies
# in the kit, its worktrees included. A report blocks nothing and is never red: exit 0 when every entry
# printed its report, 1 when one could not run, its own lines saying why.
set -u
top=$(cd "$(dirname "$0")/.." && pwd)
code=0
for entry in "$top"/modules/const-*/plugin/scripts/effect-report.sh; do
  [ -f "$entry" ] || continue
  module=$(basename "$(dirname "$(dirname "$(dirname "$entry")")")")
  sh "$entry" "$@"
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "note: the effect report of $module exited $status; its lines above say why"
    code=1
  fi
done
exit $code
