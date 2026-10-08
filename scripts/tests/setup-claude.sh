#!/bin/sh
# Fixture of scripts/setup-claude.sh and of the pinned folder in scripts/gate-list.sh, in throwaway
# repositories holding copies of the kit's scripts. A fake npm first on PATH logs its arguments and writes a
# fake claude that prints the version it was asked for, so no package is downloaded; a fake claude of the
# person's own, 2.1.286, stands for the one the gate list must not prefer without the folder. The user's
# global git configuration is kept out, and so is every variable of the kit's own checks.
# Usage: sh scripts/tests/setup-claude.sh    Exit: 0 all as expected; 2 not.

GIT_CONFIG_GLOBAL=/dev/null; export GIT_CONFIG_GLOBAL
unset CONSTITUTION_KIT_ANY_CLAUDE CONSTITUTION_KIT_INSTALL_FROM CLAUDE_CONFIG_DIR DISABLE_AUTOUPDATER

kit=$(cd "$(dirname "$0")/../.." && pwd)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/setup-claude.XXXXXX") && tmp=$(cd "$tmp" && pwd -P) || exit 1
trap 'rm -rf "$tmp"' EXIT
GIT_CEILING_DIRECTORIES=$tmp; export GIT_CEILING_DIRECTORIES
failed=0
cases=0
NPM_LOG=$tmp/npm.log; CLAUDE_LOG=$tmp/claude.log; export NPM_LOG CLAUDE_LOG

# the tools the script itself needs (ls for the fake claude), and no npm: the PATH of the cases that miss one
mkdir "$tmp/bin" "$tmp/tools" "$tmp/nothing"
for t in git sh dirname cat wc tr awk rm mktemp ls; do ln -s "$(command -v "$t")" "$tmp/tools/$t"; done

cat >"$tmp/claude.template" <<'EOF'
#!/bin/sh
printf '%s|%s|%s\n' "$DISABLE_AUTOUPDATER" "$CLAUDE_CONFIG_DIR" "$(ls -A "$CLAUDE_CONFIG_DIR" | wc -l | tr -d ' ')" >>"$CLAUDE_LOG"
echo "@VERSION@ (Claude Code)"
EOF
cat >"$tmp/bin/npm" <<'EOF'
#!/bin/sh
# as npm does: a folder that already holds the package at the asked version is left as it is
echo "$*" >>"$NPM_LOG"
[ -z "$FAKE_NPM_FAIL" ] || exit "$FAKE_NPM_FAIL"
prefix=""; version=""
while [ "$#" -gt 0 ]; do
    case $1 in
        --prefix) prefix=$2; shift ;;
        @anthropic-ai/claude-code@*) version=${1##*@} ;;
    esac
    shift
done
package=$prefix/node_modules/@anthropic-ai/claude-code
if grep -qs "\"version\": \"$version\"" "$package/package.json"; then echo "up to date"; exit 0; fi
mkdir -p "$package" "$prefix/node_modules/.bin"
printf '{"version": "%s"}\n' "$version" >"$package/package.json"
sed "s/@VERSION@/$version/" "$FAKE_CLAUDE_TEMPLATE" >"$package/cli.sh"
chmod +x "$package/cli.sh"
ln -sf ../@anthropic-ai/claude-code/cli.sh "$prefix/node_modules/.bin/claude"
EOF
printf '#!/bin/sh\necho "2.1.286 (Claude Code)"\n' >"$tmp/bin/claude"
chmod +x "$tmp/bin/npm" "$tmp/bin/claude"
FAKE_CLAUDE_TEMPLATE=$tmp/claude.template; export FAKE_CLAUDE_TEMPLATE
PATH=$tmp/bin:$PATH; export PATH

# run_in <dir> <command...>: run it there, its standard output and error together in $tmp/out, its exit in $got
run_in() {
    dir=$1; shift
    (cd "$dir" && "$@") >"$tmp/out" 2>&1; got=$?
}

# is <label> <wanted exit> <wanted output>: the last run_in exited so and printed exactly that, nothing else
is() {
    cases=$((cases + 1))
    printf '%s\n' "$3" >"$tmp/want"
    if [ "$got" -eq "$2" ] && cmp -s "$tmp/want" "$tmp/out"; then
        echo "ok    $1"
    else
        echo "WRONG $1 — exit $got, wanted $2"
        sed 's/^/        wanted: /' "$tmp/want"
        sed 's/^/        got:    /' "$tmp/out"
        failed=1
    fi
}

# holds <label> <command...>: the command exits 0
holds() {
    label=$1; shift; cases=$((cases + 1))
    if "$@" >/dev/null 2>&1; then echo "ok    $label"; else echo "WRONG $label — $*"; failed=1; fi
}

mkclone() {  # mkclone <dir>: a repository holding the scripts the cases run
    git init -q -b main "$1" && mkdir "$1/scripts" && cp "$kit/.gitignore" "$1/" || exit 1
    for f in setup-claude.sh gate-list.sh claude-code.version check-bare-install.py check-install-guide.py kit_module_doc.py; do
        cp "$kit/scripts/$f" "$1/scripts/" || exit 1
    done
    git -C "$1" add -A && git -C "$1" -c user.name=fixture -c user.email=fixture@example.invalid commit -q -m kit || exit 1
}

pin_fix="write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's only line"
green() { echo "GREEN: $1/.claude-code-pinned holds Claude Code $2, which scripts/gate-list.sh --run puts first on PATH for the install entries and the guide"; }
red() {  # red <clone> <pin> <what>
    echo "RED: the pinned Claude Code $2 is not set up — $3
  why: the install entries and the guide fail to run on any other version, and the gate list finds the pinned one only in $1/.claude-code-pinned
  fix: sh scripts/setup-claude.sh"
}
off_pin() {  # the install check's line for a claude of version $1
    echo "BROKEN: claude is $1, and the kit's install checks read the platform as 2.1.282 writes it (scripts/claude-code.version) — fix: put Claude Code 2.1.282 first on PATH for this run: either run sh scripts/setup-claude.sh in the kit's clone, then the check through sh scripts/gate-list.sh --run install-<module> (--run guide for the guide's check), which puts it first, or install it beside your own by hand (npm install --prefix <folder> @anthropic-ai/claude-code@2.1.282, then PATH=<folder>/node_modules/.bin:\$PATH), or set CONSTITUTION_KIT_ANY_CLAUDE=1 to run on $1 with a note on every headline line
BROKEN: the check could not run — 0 modules examined"
}

# the install, in a clone and from a linked worktree of it
mkclone "$tmp/clone"
clone=$tmp/clone
run_in "$clone" sh scripts/setup-claude.sh --check
is "no folder: --check is red" 2 "$(red "$clone" 2.1.282 "$clone/.claude-code-pinned has no executable node_modules/.bin/claude")"
run_in "$clone" sh scripts/setup-claude.sh
is "the install turns the clone green" 0 "$(green "$clone" 2.1.282)"
holds "npm was asked for the pinned package, into the clone's folder" test "$(cat "$NPM_LOG")" = "install --prefix $clone/.claude-code-pinned --no-audit --no-fund @anthropic-ai/claude-code@2.1.282"
holds "git ignores the folder" git -C "$clone" check-ignore -q .claude-code-pinned/node_modules/.bin/claude
holds "and the clone has nothing to commit" test -z "$(git -C "$clone" status --porcelain)"
run_in "$clone" sh scripts/setup-claude.sh --check
is "--check is green on the pin" 0 "$(green "$clone" 2.1.282)"

mkclone "$tmp/main"
git -C "$tmp/main" worktree add -q "$tmp/linked" -b work/linked
: >"$NPM_LOG"
run_in "$tmp/linked" sh scripts/setup-claude.sh
is "a linked worktree installs, and is green through the main checkout's folder" 0 "$(green "$tmp/main" 2.1.282)"
holds "npm was asked to install into the main checkout's folder" test "$(cat "$NPM_LOG")" = "install --prefix $tmp/main/.claude-code-pinned --no-audit --no-fund @anthropic-ai/claude-code@2.1.282"
holds "the main checkout holds the claude" test -x "$tmp/main/.claude-code-pinned/node_modules/.bin/claude"
holds "the worktree holds no folder of its own" test ! -e "$tmp/linked/.claude-code-pinned"
run_in "$tmp/linked" sh scripts/setup-claude.sh --check
is "--check from the worktree reads the main checkout's folder" 0 "$(green "$tmp/main" 2.1.282)"
run_in "$tmp/main" sh scripts/setup-claude.sh --check
is "and so does the main checkout" 0 "$(green "$tmp/main" 2.1.282)"

# the check: every state it finds red, and the fix it prints followed as printed, which is the script
# itself, to green. npm leaves a folder that holds the package as it is, so the script replaces the
# folder whole; the fake npm does as npm does, and says so
bin=$clone/.claude-code-pinned/node_modules/.bin
walk() {  # walk <label> <what the RED says> <commands that put the installed folder in that state>
    eval "$3"
    run_in "$clone" sh scripts/setup-claude.sh --check
    is "$1: --check is red" 2 "$(red "$clone" 2.1.282 "$2")"
    run_in "$clone" sh scripts/setup-claude.sh
    is "$1: the fix, run as printed, turns it green" 0 "$(green "$clone" 2.1.282)"
    run_in "$clone" sh scripts/setup-claude.sh --check
    is "$1: and --check stays green" 0 "$(green "$clone" 2.1.282)"
}
no_claude="$clone/.claude-code-pinned has no executable node_modules/.bin/claude"
walk "no folder" "$no_claude" 'rm -rf "$clone/.claude-code-pinned"'
walk "a bin link replaced by a claude of another version" "its claude answers 2.1.286, not 2.1.282" 'rm "$bin/claude"; sed "s/@VERSION@/2.1.286/" "$tmp/claude.template" >"$bin/claude"; chmod +x "$bin/claude"'
rm "$bin/claude"; sed "s/@VERSION@/2.1.286/" "$tmp/claude.template" >"$bin/claude"; chmod +x "$bin/claude"
run_in "$clone" npm install --prefix "$clone/.claude-code-pinned" --no-audit --no-fund @anthropic-ai/claude-code@2.1.282
is "npm alone, asked again for the package that folder holds, says up to date" 0 "up to date"
run_in "$clone" sh scripts/setup-claude.sh --check
is "and changes nothing, so the folder stays red: the fix cannot be npm alone" 2 "$(red "$clone" 2.1.282 "its claude answers 2.1.286, not 2.1.282")"
walk "a claude of the package damaged to print nothing" "its claude exited 0 without a version (no output)" 'printf "#!/bin/sh\nexit 0\n" >"$bin/claude"'
walk "a claude that fails" "its claude exited 3 without a version (boom)" 'printf "#!/bin/sh\necho boom\nexit 3\n" >"$bin/claude"'
walk "a claude that is not executable" "$no_claude" 'chmod -x "$bin/claude"'
walk "a bin link that points nowhere" "$no_claude" 'rm "$bin/claude"; ln -s /nonexistent/claude "$bin/claude"'
walk "a bin folder with no claude" "$no_claude" 'rm "$bin/claude"'
walk "a file in the folder's place" "$no_claude" 'rm -rf "$clone/.claude-code-pinned"; : >"$clone/.claude-code-pinned"'
walk "a folder holding another version of the package" "its claude answers 2.1.286, not 2.1.282" 'rm -rf "$clone/.claude-code-pinned"; mkdir -p "$bin"; sed "s/@VERSION@/2.1.286/" "$tmp/claude.template" >"$bin/claude"; chmod +x "$bin/claude"; mkdir -p "$clone/.claude-code-pinned/node_modules/@anthropic-ai/claude-code"; printf "{\"version\": \"2.1.282\"}\n" >"$clone/.claude-code-pinned/node_modules/@anthropic-ai/claude-code/package.json"'
: >"$CLAUDE_LOG"
person=$tmp/person; mkdir "$person"
(cd "$clone" && CLAUDE_CONFIG_DIR=$person DISABLE_AUTOUPDATER=0 sh scripts/setup-claude.sh --check) >"$tmp/out" 2>&1; got=$?
is "the claude is green again, with the person's two variables set" 0 "$(green "$clone" 2.1.282)"
asked=$(cat "$CLAUDE_LOG")
holds "it was asked with the auto-updater off" test "${asked%%|*}" = 1
config=${asked#*|}; config=${config%|*}
holds "in a configuration folder that is not the person's" test "$config" != "$person"
holds "and was empty" test "${asked##*|}" = 0
holds "which the script removed" test ! -e "$config"
holds "and the person's own folder is untouched" test -z "$(ls -A "$person")"

# the pin file, in every form pinned_claude of scripts/kit_module_doc.py refuses, and in the forms it takes
mkclone "$tmp/pins"
pins=$tmp/pins
pin_file=$pins/scripts/claude-code.version
: >"$NPM_LOG"
mv "$pin_file" "$tmp/pin.saved"
run_in "$pins" sh scripts/setup-claude.sh
is "a missing pin file is BROKEN" 1 "BROKEN: $pin_file cannot be read — fix: $pin_fix"
# the fix is typed in two places, the script and PIN_FIX of scripts/kit_module_doc.py; nothing else ties them
shell_fix=$(sed 's/^.* — fix: //' "$tmp/out")
python_fix=$(PYTHONDONTWRITEBYTECODE=1 python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import kit_module_doc; print(kit_module_doc.PIN_FIX)' "$pins/scripts")
holds "the script's fix for a pin is the Python constant's" test "$shell_fix" = "$python_fix" -a -n "$python_fix"
: >"$pin_file"
run_in "$pins" sh scripts/setup-claude.sh
is "an empty pin file is BROKEN" 1 "BROKEN: $pin_file is empty — fix: $pin_fix"
mkdir "$tmp/pin.dir"; rm "$pin_file"; ln -s "$tmp/pin.dir" "$pin_file"
run_in "$pins" sh scripts/setup-claude.sh
is "a folder in the pin file's place is BROKEN" 1 "BROKEN: $pin_file cannot be read — fix: $pin_fix"
rm "$pin_file"
not_one="BROKEN: $pin_file is not one version — fix: $pin_fix"
pin_form() {  # pin_form <label> <printf format of the file's bytes>
    printf "$2" >"$pin_file"
    run_in "$pins" sh scripts/setup-claude.sh
    is "a pin that is $1 is BROKEN" 1 "$not_one"
}
pin_form "a carriage return and a line feed" '2.1.282\r\n'
pin_form "headed by a byte-order mark" '\357\273\2772.1.282\n'
pin_form "two lines" '2.1.282\n2.1.283\n'
pin_form "two lines, the second empty" '2.1.282\n\n'
pin_form "two lines, the second the same, with no final line feed" '2.1.282\n2.1.282'
pin_form "a word" 'latest\n'
pin_form "a line feed alone" '\n'
pin_form "two numbers" '2.1\n'
pin_form "four numbers" '2.1.282.1\n'
pin_form "a letter for a number" '2.1.x\n'
pin_form "headed by a space" ' 2.1.282\n'
pin_form "ended by a space" '2.1.282 \n'
pin_form "a number missing between two dots" '2..282\n'
pin_form "headed by a dot" '.2.1.282\n'
pin_form "ended by a dot" '2.1.282.\n'
pin_form "followed by a NUL byte" '2.1.282\0\n'
pin_form "of Arabic-Indic digits" '\331\242.\331\241.\331\242\331\250\331\242\n'
pin_form "headed by a v" 'v2.1.282\n'
holds "no pin form reached npm" test ! -s "$NPM_LOG"
run_in "$pins" sh scripts/setup-claude.sh --check
is "--check refuses it too" 1 "$not_one"
printf '2.1.282' >"$pin_file"
run_in "$pins" sh scripts/setup-claude.sh
is "a pin with no final line feed is read" 0 "$(green "$pins" 2.1.282)"
printf '10.20.3000\n' >"$pin_file"
run_in "$pins" sh scripts/setup-claude.sh
is "a pin of longer numbers is read, and asked of npm" 0 "$(green "$pins" 10.20.3000)"
holds "npm was asked for it" test "$(tail -1 "$NPM_LOG")" = "install --prefix $pins/.claude-code-pinned --no-audit --no-fund @anthropic-ai/claude-code@10.20.3000"

# what else fails: a bad argument, npm that fails or is missing, git missing, no repository
mkclone "$tmp/fails"
fails=$tmp/fails
: >"$NPM_LOG"
run_in "$fails" sh scripts/setup-claude.sh --install
is "an unknown argument is BROKEN" 1 "BROKEN: unknown argument '--install' — fix: sh scripts/setup-claude.sh [--check]"
run_in "$fails" sh scripts/setup-claude.sh --check now
is "an argument beside --check is BROKEN" 1 "BROKEN: unknown argument '--check now' — fix: sh scripts/setup-claude.sh [--check]"
run_in "$fails" env FAKE_NPM_FAIL=3 sh scripts/setup-claude.sh
is "an npm that fails is BROKEN, with the command to run by hand" 1 "BROKEN: npm install exited 3 — fix: run npm install --prefix \"$fails/.claude-code-pinned\" --no-audit --no-fund \"@anthropic-ai/claude-code@2.1.282\" by hand and read why it fails"
run_in "$fails" sh scripts/setup-claude.sh
is "a good install, for the cases that follow to leave or fail to remove" 0 "$(green "$fails" 2.1.282)"
mkdir "$tmp/failrm"
printf '#!/bin/sh\nexit 1\n' >"$tmp/failrm/rm"
chmod +x "$tmp/failrm/rm"
: >"$NPM_LOG"
run_in "$fails" env PATH="$tmp/failrm:$PATH" sh scripts/setup-claude.sh
is "a folder that cannot be removed is BROKEN, with the fix" 1 "BROKEN: $fails/.claude-code-pinned could not be removed — fix: remove it by hand, then run sh scripts/setup-claude.sh again"
holds "npm was never called" test ! -s "$NPM_LOG"
holds "and the folder is as it was" test -x "$fails/.claude-code-pinned/node_modules/.bin/claude"
run_in "$fails" env PATH="$tmp/tools" /bin/sh scripts/setup-claude.sh
is "a missing npm is BROKEN" 1 "BROKEN: npm is not installed, and Claude Code is an npm package — fix: install Node.js with npm (https://nodejs.org/) and put npm on PATH"
holds "the good install is still there: the folder is removed only once npm is found" test -x "$fails/.claude-code-pinned/node_modules/.bin/claude"
run_in "$fails" env PATH="$tmp/tools" /bin/sh scripts/setup-claude.sh --check
is "and --check is still green" 0 "$(green "$fails" 2.1.282)"
rm -rf "$fails/.claude-code-pinned"
run_in "$fails" env PATH="$tmp/tools" /bin/sh scripts/setup-claude.sh --check
is "--check needs no npm: a clone with no folder is red, not BROKEN" 2 "$(red "$fails" 2.1.282 "$fails/.claude-code-pinned has no executable node_modules/.bin/claude")"
run_in "$fails" env PATH="$tmp/nothing" /bin/sh scripts/setup-claude.sh
is "a missing git is BROKEN" 1 "BROKEN: git is not installed, and the pinned folder is found through it — fix: install it and put it on PATH"
mkdir "$tmp/plain"
run_in "$tmp/plain" sh "$fails/scripts/setup-claude.sh"
is "outside a repository is BROKEN" 1 "BROKEN: not inside a git repository — fix: run it from a clone of the kit"

# the gate list: the pinned folder goes first on PATH for the install entries and the guide, and for no other
mkclone "$tmp/list"
list=$tmp/list
bin=$list/.claude-code-pinned/node_modules/.bin
install_entry=const-meta-types
ran="gate-list: exit 1 — python3 scripts/check-bare-install.py --module $install_entry"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
is "install entry, no folder: the person's own claude is the one asked" 1 "$(off_pin 2.1.286)
$ran"
mkdir -p "$bin"
printf '#!/bin/sh\necho "9.9.9 (Claude Code)"\n' >"$bin/claude"
chmod -x "$bin/claude"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
is "install entry, a folder whose claude is not executable: the person's own again" 1 "$(off_pin 2.1.286)
$ran"
chmod +x "$bin/claude"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
is "install entry, a folder with a claude: that claude is the one asked" 1 "$(off_pin 9.9.9)
$ran"
git -C "$list" worktree add -q "$tmp/list-linked" -b work/linked
run_in "$tmp/list-linked" sh scripts/gate-list.sh --run "install-$install_entry"
is "install entry from a linked worktree: the main checkout's folder is the one used" 1 "$(off_pin 9.9.9)
$ran"
holds "and the worktree holds no folder" test ! -e "$tmp/list-linked/.claude-code-pinned"

# a python3 in the folder that logs its arguments shows which entries had the folder on PATH
printf '#!/bin/sh\necho "$*" >>"$MARKER"\n' >"$bin/python3"
chmod +x "$bin/python3"
MARKER=$tmp/marker; export MARKER
: >"$MARKER"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
is "install entry: its command ran the folder's python3" 0 "gate-list: exit 0 — python3 scripts/check-bare-install.py --module $install_entry"
holds "which logged the check" test "$(cat "$MARKER")" = "scripts/check-bare-install.py --module $install_entry"
: >"$MARKER"
run_in "$list" sh scripts/gate-list.sh --run guide
is "the guide: both its commands ran the folder's python3" 0 "gate-list: exit 0 — python3 scripts/check-install-guide.py
gate-list: exit 0 — python3 scripts/check-install-guide.py --self-test"
holds "which logged both" test "$(cat "$MARKER")" = "scripts/check-install-guide.py
scripts/check-install-guide.py --self-test"
: >"$MARKER"
run_in "$list" sh scripts/gate-list.sh --run schema-mirror
holds "another entry ran the real python3, which has no such script here" test "$got" -eq 2
holds "and the folder's python3 did not run" test ! -s "$MARKER"
run_in "$list" sh scripts/gate-list.sh --run meta-types
holds "a module's scan, the same" test ! -s "$MARKER"
chmod -x "$bin/claude"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
holds "a folder whose claude is not executable is not on PATH for the install entry" test ! -s "$MARKER"
rm -rf "$list/.claude-code-pinned"
run_in "$list" sh scripts/gate-list.sh --run "install-$install_entry"
is "no folder, again: the person's own claude, as CI runs it" 1 "$(off_pin 2.1.286)
$ran"

# the folder goes first on PATH for the install entries and the guide ALONE, over every entry of the list.
# A tree of the list alone, where every command fails fast, and a sh in the folder that logs the command
# it is given and runs the real sh: run_entry runs each command as sh -c, so that sh is reached exactly
# when the folder is first on PATH
git init -q -b main "$tmp/sweep" && mkdir "$tmp/sweep/scripts" && cp "$kit/scripts/gate-list.sh" "$tmp/sweep/scripts/" || exit 1
git -C "$tmp/sweep" add -A && git -C "$tmp/sweep" -c user.name=fixture -c user.email=fixture@example.invalid commit -q -m list || exit 1
sweep=$tmp/sweep
sweep_bin=$sweep/.claude-code-pinned/node_modules/.bin
mkdir -p "$sweep_bin"
printf '#!/bin/sh\nprintf "%%s\\n" "$2" >>"$MARKER"\nexec /bin/sh "$@"\n' >"$sweep_bin/sh"
printf '#!/bin/sh\nexit 0\n' >"$sweep_bin/claude"
chmod +x "$sweep_bin/sh" "$sweep_bin/claude"
entries=$(cd "$sweep" && sh scripts/gate-list.sh --names all)
: >"$MARKER"; : >"$tmp/want.all"; ran=0
for entry in $entries; do
    (cd "$sweep" && sh scripts/gate-list.sh --run "$entry") >/dev/null 2>&1
    ran=$((ran + 1))
    case $entry in
        install-* | guide) (cd "$sweep" && sh scripts/gate-list.sh --show "$entry") >>"$tmp/want.all" ;;
    esac
done
holds "every entry of the list was run alone ($ran)" test "$ran" -gt 50
holds "the commands of the install entries and the guide were all that reached the folder's sh" cmp -s "$MARKER" "$tmp/want.all"
holds "and they are not none: a command for each install entry and two for the guide" test "$(wc -l <"$tmp/want.all" | tr -d ' ')" -ge 11
holds "the guide's two among them" test "$(grep -c 'check-install-guide.py' "$tmp/want.all")" -eq 2
: >"$MARKER"
(cd "$sweep" && sh scripts/gate-list.sh --run "$install_entry") >/dev/null 2>&1
printf 'python3 scripts/check-bare-install.py --module %s\n' "$install_entry" >"$tmp/want.one"
holds "a job run goes through run_entry the same way: a module's job reaches the folder with its install entry alone" cmp -s "$MARKER" "$tmp/want.one"
: >"$MARKER"
(cd "$sweep" && sh scripts/gate-list.sh --run install-guide) >/dev/null 2>&1
printf 'python3 scripts/check-install-guide.py\npython3 scripts/check-install-guide.py --self-test\n' >"$tmp/want.guide"
holds "the guide's job reaches it with the guide's two commands" cmp -s "$MARKER" "$tmp/want.guide"
: >"$MARKER"
(cd "$sweep" && sh scripts/gate-list.sh --run kit) >/dev/null 2>&1
holds "the kit's job, with the folder present, never reaches it" test ! -s "$MARKER"

# the list itself is unchanged by the folder
run_in "$list" sh scripts/gate-list.sh --show "install-$install_entry"
is "--show prints the command alone" 0 "python3 scripts/check-bare-install.py --module $install_entry"
run_in "$list" sh scripts/gate-list.sh --names extra
holds "the fixture is an extra entry of the list" grep -qx setup-claude "$tmp/out"

[ "$failed" -eq 0 ] && echo "GREEN: $cases cases as expected" && exit 0
echo "RED: a case went wrong — see above"; exit 2
