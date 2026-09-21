#!/bin/sh
# Kit routine: the two settings a clone needs for the branch-first gate. Git keeps them per clone
# and never versions them, so a fresh clone is unguarded until this has run once.
#   sh scripts/setup-clone.sh           set them
#   sh scripts/setup-clone.sh --check   exit 0 when both are set, 2 when not
# core.hooksPath  scripts/git-hooks  — git runs the kit's tracked hooks
# merge.ff        false              — a merge into main is always a merge commit, never a fast-forward

cd "$(git rev-parse --show-toplevel)" || { echo "BROKEN: not inside a git repository" >&2; exit 1; }

if [ "$1" = "--check" ]; then
    if [ "$(git config --get core.hooksPath)" = "scripts/git-hooks" ] && [ "$(git config --get merge.ff)" = "false" ] \
        && [ -x scripts/git-hooks/prepare-commit-msg ]; then
        echo "GREEN: this clone runs the kit's hooks and merges without fast-forward"
        exit 0
    fi
    cat >&2 <<MSG
RED: this clone is not set up — core.hooksPath is "$(git config --get core.hooksPath)", merge.ff is "$(git config --get merge.ff)", the hook is $([ -x scripts/git-hooks/prepare-commit-msg ] && echo executable || echo "missing or not executable")
  why: git never versions these two settings, and without them a commit can land on main unrefused
  fix: sh scripts/setup-clone.sh   — and chmod +x scripts/git-hooks/prepare-commit-msg if the hook is not executable
MSG
    exit 2
fi

git config core.hooksPath scripts/git-hooks && git config merge.ff false && sh scripts/setup-clone.sh --check
