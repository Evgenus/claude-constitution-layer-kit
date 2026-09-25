#!/usr/bin/env bash
# Deterministic invariant check. Exit 2 blocks the action.
# Error message contract (see MODULE.md): what failed, why the rule
# exists (one clause), the exact fix.
# Example:
#   echo "document lacks 'type' frontmatter — every governed document
#   declares a meta-type so sessions know its authority; add
#   type: current-state | task-record | non-authoritative" >&2
#   exit 2
exit 0
