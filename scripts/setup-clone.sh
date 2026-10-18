#!/bin/sh
# Kit routine: the three settings a clone needs for the branch-first gate. Git keeps them per clone
# and never versions them, so a fresh clone is unguarded until this has run once.
#   sh scripts/setup-clone.sh           set them
#   sh scripts/setup-clone.sh --check   exit 0 when all three are set and the hook file is executable, 2 when not
# core.hooksPath  scripts/git-hooks  — git runs the kit's tracked hooks; --check also takes an absolute path to
#                                      scripts/git-hooks in the top folder of a checkout sharing this clone's git
#                                      common directory — the main checkout or one of its worktrees, never another
#                                      clone — which the Claude desktop app writes into the config of each worktree
#                                      it makes; git then runs that checkout's copy of the hook
# merge.ff        false              — a merge into main is always a merge commit, never a fast-forward
# pull.ff         only               — a pull onto main only fast-forwards to the remote's merge; with merge.ff
#                                      false alone, a plain git pull would make a merge commit of its own

top=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ] && cd "$top" || { echo "BROKEN: not inside a git repository — fix: run it from a clone of the kit" >&2; exit 1; }

common() {  # the absolute git common directory of the checkout whose top folder is $1, empty when it is none
    (cd "$1" 2>/dev/null && [ "$(git rev-parse --show-toplevel 2>/dev/null)" = "$(pwd -P)" ] \
        && cd "$(git rev-parse --git-common-dir)" && pwd -P)
}
hooks=$(git config --get core.hooksPath)
case $hooks in  # the folder git runs this clone's hooks from, when it is the kit's; empty when it is not
    scripts/git-hooks) dir=scripts/git-hooks ;;
    /*/scripts/git-hooks) dir=$hooks; [ -n "$(common .)" ] && [ "$(common "${hooks%/scripts/git-hooks}")" = "$(common .)" ] || dir= ;;
    *) dir= ;;
esac
case $dir in /*) hookdir=$dir ;; *) hookdir=$top/scripts/git-hooks ;; esac  # the hooks folder a fix acts on, absolute

if [ "$1" = "--check" ]; then
    if [ -n "$dir" ] && [ "$(git config --get merge.ff)" = "false" ] \
        && [ "$(git config --get pull.ff)" = "only" ] \
        && [ -x "$dir/prepare-commit-msg" ]; then
        echo "GREEN: this clone runs the kit's hooks, merges without fast-forward and pulls only by fast-forward"
        exit 0
    fi
    cat >&2 <<MSG
RED: this clone is not set up — core.hooksPath is "$hooks"$([ -n "$dir" ] || echo ", which names no scripts/git-hooks of this repository"), merge.ff is "$(git config --get merge.ff)", pull.ff is "$(git config --get pull.ff)", the hook is $([ -x "${dir:-scripts/git-hooks}/prepare-commit-msg" ] && echo executable || echo "missing or not executable")
  why: git never versions the three settings or runs a hook that is not executable, and without all four main can take a commit no rule allowed
  fix: sh scripts/setup-clone.sh   — in a worktree whose own config names another hooks path: git config --worktree core.hooksPath scripts/git-hooks; if the hook is not executable: chmod +x "$hookdir/prepare-commit-msg"; if it is missing: git -C "${hookdir%/scripts/git-hooks}" checkout -- scripts/git-hooks
MSG
    exit 2
fi

git config core.hooksPath scripts/git-hooks && git config merge.ff false && git config pull.ff only && sh scripts/setup-clone.sh --check
