#!/bin/sh
# Fixture of the branch-first gate, in a throwaway repository: the clone that is not set up takes a
# commit on main, the clone that is set up refuses it and takes the same commit on a branch.
# The user's global git configuration is kept out, so a global hooks path or signing cannot colour a case.
# Its folder is made under TMPDIR (or /tmp when it is unset) and the fixture fails when it is not there.
# Usage: sh scripts/git-hooks/tests/run.sh    Exit: 0 all as expected; 2 not; 1 the fixture's folder is not under TMPDIR.

GIT_CONFIG_GLOBAL=/dev/null; export GIT_CONFIG_GLOBAL

kit=$(cd "$(dirname "$0")/../../.." && pwd)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/git-hooks.XXXXXX") && tmp=$(cd "$tmp" && pwd -P) || exit 1
trap 'rm -rf "$tmp"' EXIT
base=$(cd "${TMPDIR:-/tmp}" && pwd -P) || exit 1
case $tmp in "$base"/*) ;; *)
    echo "RED: the fixture's folder $tmp is not under ${TMPDIR:-/tmp}, so a run's TMPDIR would not hold its repositories — fix: make it with mktemp -d \"\${TMPDIR:-/tmp}/git-hooks.XXXXXX\", the template names the place; on macOS mktemp -d without one ignores TMPDIR"
    exit 1 ;;
esac
failed=0
cases=0

expect() {  # expect <wanted exit, or several joined by |> <label> <command...>
    wanted=$1; label=$2; shift 2; cases=$((cases + 1))
    "$@" >"$tmp/out" 2>&1; got=$?
    if case "|$wanted|" in *"|$got|"*) true ;; *) false ;; esac; then echo "ok    $label"; else echo "WRONG $label — exit $got, wanted $wanted"; sed 's/^/        /' "$tmp/out"; failed=1; fi
}

cd "$tmp" && git init -q -b main repo && cd repo || exit 1
git config user.name fixture && git config user.email fixture@example.invalid
git commit -q --allow-empty -m root
mkdir scripts && cp -R "$kit/scripts/git-hooks" scripts/ && cp "$kit/scripts/setup-clone.sh" scripts/

expect 2 "an unprepared clone is red"                    sh scripts/setup-clone.sh --check
echo x > x && git add x
expect 0 "without the hook a commit lands on main"        git commit -q -m "unguarded"
expect 0 "setup turns the clone green"                    sh scripts/setup-clone.sh
git config --unset pull.ff
expect 2 "a clone that pulls with a merge commit is red"   sh scripts/setup-clone.sh --check
sh scripts/setup-clone.sh >/dev/null 2>&1
echo a > a && git add a
expect 1 "a commit on main is refused"                    git commit -q -m "on main"
git commit -q -m "on main" >"$tmp/msg" 2>&1
expect 0 "the refusal teaches the fix"                     grep -q 'fix: git switch -c work/<name>' "$tmp/msg"
expect 0 "and the way to main, a pull request's merge"     grep -q 'gh pr merge <n> --merge --subject "Work: <name>"' "$tmp/msg"
expect 1 "--no-verify does not get past it"               git commit -q --no-verify -m "on main"
expect 1 "an amend on main is refused"                    git commit -q --amend -m "reworded"
git commit -q --amend -m "reworded" >"$tmp/msg" 2>&1
expect 0 "and is told to leave the commit and correct it on a branch" grep -q 'If this was an amend: the commit is on main already' "$tmp/msg"
git switch -q -c work/one
expect 0 "the same commit passes on a branch"             git commit -q -m "on a branch"
echo b > b && git add b && git commit -q -m "second"
git switch -q main
before=$(git rev-parse HEAD)
# git's exit after a refusing prepare-commit-msg hook: 128 before git 2.56, 1 since (git commit 18f5750beb14,
# "sequencer: never reschedule on failed commit"); a conflict also exits 1, so each refusal is also read for the hook's line
refused="1|128"
expect "$refused" "a cherry-pick onto main is refused (git's own exit)" git cherry-pick work/one
cp "$tmp/out" "$tmp/msg"
expect 0 "and is told to abort first"                     grep -q 'fix: git cherry-pick --abort' "$tmp/msg"
expect 128 "for git will not switch branches in the middle of one" git switch -c work/stuck
expect 0 "the taught fix works: abort, then the branch"   sh -c 'git cherry-pick --abort && git switch -q -c work/two && git switch -q main'
expect 0 "and main has not moved"                         test "$(git rev-parse HEAD)" = "$before"
expect 0 "a merge into main passes"                       git merge -q work/one -m "Work: one"
expect 0 "and is a merge commit though it could fast-forward" test "$(git rev-list --merges --count HEAD)" -eq 1
before=$(git rev-parse HEAD)
expect "$refused" "a revert on main is refused (git's own exit)"   git revert --no-edit HEAD^2
cp "$tmp/out" "$tmp/msg"
expect 0 "by the hook"                                     grep -q '^RED: this commit would land on main' "$tmp/msg"
expect 0 "the taught fix works: the staged revert goes to a branch" sh -c 'git switch -q -c work/three && git commit -q -m "revert, on a branch" && git switch -q main'
expect 0 "and main has not moved"                         test "$(git rev-parse HEAD)" = "$before"
expect "$refused" "a revert of several commits on main is refused"  git revert --no-edit work/one work/one~1
cp "$tmp/out" "$tmp/msg"
expect 0 "and is told to abort first"                     grep -q 'fix: git revert --abort' "$tmp/msg"
expect 0 "the taught fix works: abort, then the branch"   sh -c 'git revert --abort && git switch -q -c work/four && git switch -q main'
git init -q --bare -b main "$tmp/remote.git" && git push -q "$tmp/remote.git" main
git clone -q "$tmp/remote.git" "$tmp/other" && (cd "$tmp/other" && git -c user.name=f -c user.email=f@example.invalid commit -q --allow-empty -m "merged on the remote" && git push -q origin main)
remote_main=$(git --git-dir="$tmp/remote.git" rev-parse main)
expect 0 "the remote's main is ahead of this one"          test "$remote_main" != "$(git rev-parse HEAD)"
expect 0 "after setup a pull onto main only fast-forwards" git pull -q "$tmp/remote.git" main
expect 0 "to the remote's main exactly, no merge of its own" test "$(git rev-parse HEAD)" = "$remote_main"
chmod -x scripts/git-hooks/prepare-commit-msg
expect 2 "a hook that is not executable makes the clone red" sh scripts/setup-clone.sh --check
mkdir -p deep && (cd deep && sh ../scripts/setup-clone.sh --check) >"$tmp/msg" 2>&1
expect 0 "and from a subfolder its fixes name the setup and the hook by absolute path" \
    grep -q "fix: sh \"$tmp/repo/scripts/setup-clone.sh\" .*chmod +x \"$tmp/repo/scripts/git-hooks/prepare-commit-msg\"; if it is missing: git -C \"$tmp/repo\" checkout -- scripts/git-hooks/prepare-commit-msg$" "$tmp/msg"
chmod +x scripts/git-hooks/prepare-commit-msg
git config extensions.worktreeConfig true && git worktree add -q "$tmp/wt" -b work/wt
(cd "$tmp/wt" && git config --worktree core.hooksPath "$tmp/repo/scripts/git-hooks")
expect 0 "a worktree whose own config names this repository's hooks folder by its absolute path, as the desktop app writes, is green" \
    sh -c 'cd "$1" && sh "$2" --check' - "$tmp/wt" "$tmp/repo/scripts/setup-clone.sh"
chmod -x scripts/git-hooks/prepare-commit-msg
expect 2 "that worktree is red when the hook its path names is not executable" \
    sh -c 'cd "$1" && sh "$2" --check' - "$tmp/wt" "$tmp/repo/scripts/setup-clone.sh"
cp "$tmp/out" "$tmp/msg"
fix=$(sed -n 's/.*if the hook is not executable: \(chmod +x [^;]*\);.*/\1/p' "$tmp/msg")
expect 0 "and its fix names that hook, not the worktree's own copy" test "$fix" = "chmod +x \"$tmp/repo/scripts/git-hooks/prepare-commit-msg\""
expect 0 "the taught fix works: run it, the worktree is green" \
    sh -c 'cd "$1" && sh -c "$3" && sh "$2" --check' - "$tmp/wt" "$tmp/repo/scripts/setup-clone.sh" "$fix"
git config core.hooksPath "$tmp/repo/scripts/git-hooks"
expect 0 "so is the clone itself with that absolute path"  sh scripts/setup-clone.sh --check
mkdir -p sub/scripts && cp -R scripts/git-hooks sub/scripts/ && git config core.hooksPath "$tmp/repo/sub/scripts/git-hooks"
expect 2 "a hooks folder in a plain folder of the clone is red" sh scripts/setup-clone.sh --check
git init -q "$tmp/stranger" && mkdir -p "$tmp/stranger/scripts" && cp -R scripts/git-hooks "$tmp/stranger/scripts/"
git config core.hooksPath "$tmp/stranger/scripts/git-hooks"
expect 2 "another repository's hooks folder is red"      sh scripts/setup-clone.sh --check
cp "$tmp/out" "$tmp/msg"
expect 0 "and the red says the path names no hooks folder of this repository" grep -q 'which names no scripts/git-hooks of this repository' "$tmp/msg"
expect 0 "and gives the fix for a worktree's own config"   grep -q 'git config --worktree core.hooksPath scripts/git-hooks' "$tmp/msg"
sh scripts/setup-clone.sh >/dev/null 2>&1
git init -q -b main "$tmp/tracked" && cp -R scripts "$tmp/tracked/" \
    && (cd "$tmp/tracked" && git add scripts && git -c user.name=f -c user.email=f@example.invalid commit -q -m hooks \
        && git config merge.ff false && git config pull.ff only && git config extensions.worktreeConfig true \
        && git worktree add -q "$tmp/tracked-wt" -b work/wt && rm scripts/git-hooks/prepare-commit-msg) \
    && (cd "$tmp/tracked-wt" && git config --worktree core.hooksPath "$tmp/tracked/scripts/git-hooks")
expect 2 "a worktree whose path names a checkout that lost its hook is red" \
    sh -c 'cd "$1" && sh scripts/setup-clone.sh --check' - "$tmp/tracked-wt"
cp "$tmp/out" "$tmp/msg"
fix=$(sed -n 's/.*if it is missing: \(git -C .*\)$/\1/p' "$tmp/msg")
expect 0 "the taught fix works: run it, the hook is back and the worktree is green" \
    sh -c 'cd "$1" && sh -c "$2" && sh scripts/setup-clone.sh --check' - "$tmp/tracked-wt" "$fix"
git switch -q --detach
expect 0 "a detached HEAD is not main"                    git commit -q --allow-empty -m "detached"

[ "$failed" -eq 0 ] && echo "GREEN: $cases cases as expected" && exit 0
echo "RED: a case went wrong — see above"; exit 2
