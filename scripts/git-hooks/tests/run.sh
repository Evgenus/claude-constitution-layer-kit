#!/bin/sh
# Fixture of the branch-first gate: each case in a throwaway repository, red without the rule
# kept, green with it. Usage: sh scripts/git-hooks/tests/run.sh    Exit: 0 all as expected; 2 not.

kit=$(cd "$(dirname "$0")/../../.." && pwd)
tmp=$(mktemp -d) || exit 1
trap 'rm -rf "$tmp"' EXIT
failed=0

expect() {  # expect <wanted exit> <label> <command...>
    wanted=$1; label=$2; shift 2
    "$@" >"$tmp/out" 2>&1; got=$?
    if [ "$got" -eq "$wanted" ]; then echo "ok    $label"; else echo "WRONG $label — exit $got, wanted $wanted"; sed 's/^/        /' "$tmp/out"; failed=1; fi
}

cd "$tmp" && git init -q -b main repo && cd repo || exit 1
git config user.name fixture && git config user.email fixture@example.invalid
git commit -q --allow-empty -m root
mkdir scripts && cp -R "$kit/scripts/git-hooks" scripts/ && cp "$kit/scripts/setup-clone.sh" scripts/

expect 2 "an unprepared clone is red"                    sh scripts/setup-clone.sh --check
echo x > x && git add x
expect 0 "without the hook a commit lands on main"        git commit -q -m "unguarded"
expect 0 "setup turns the clone green"                    sh scripts/setup-clone.sh
echo a > a && git add a
expect 1 "a commit on main is refused"                    git commit -q -m "on main"
git commit -q -m "on main" 2>&1 | grep -q 'fix: git switch -c work/<name>' ; expect 0 "the refusal teaches the fix" test $? -eq 0
expect 1 "--no-verify does not get past it"               git commit -q --no-verify -m "on main"
expect 1 "an amend on main is refused"                    git commit -q --amend -m "reworded"
git switch -q -c work/one
expect 0 "the same commit passes on a branch"             git commit -q -m "on a branch"
echo b > b && git add b && git commit -q -m "second"
git switch -q main
before=$(git rev-parse HEAD)
expect 128 "a cherry-pick onto main is refused (git's own exit)" git cherry-pick work/one
git cherry-pick --abort 2>/dev/null; git reset -q --hard
expect 0 "and main has not moved"                         test "$(git rev-parse HEAD)" = "$before"
expect 0 "a merge into main passes"                       git merge -q work/one -m "Work: one"
expect 0 "and is a merge commit though it could fast-forward" test "$(git rev-list --merges --count HEAD)" -eq 1
before=$(git rev-parse HEAD)
expect 128 "a revert on main is refused (git's own exit)"   git revert --no-edit HEAD^2
git revert --abort 2>/dev/null; git reset -q --hard
expect 0 "and main has not moved"                         test "$(git rev-parse HEAD)" = "$before"
git switch -q --detach
expect 0 "a detached HEAD is not main"                    git commit -q --allow-empty -m "detached"

[ "$failed" -eq 0 ] && echo "GREEN: 16 cases as expected" && exit 0
echo "RED: a case went wrong — see above"; exit 2
