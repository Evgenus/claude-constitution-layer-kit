#!/bin/sh
# Kit routine, never shipped in a module: the Claude Code that scripts/claude-code.version pins, installed
# for local runs of the gate list. The install and session entries and the guide fail to run on any other version, and
# a person's own claude is rarely the pin; this puts the pin beside it, where scripts/gate-list.sh --run
# finds it and puts it first on PATH for those entries alone.
#   sh scripts/setup-claude.sh           install the pinned version into <main>/.claude-code-pinned, then --check
#   sh scripts/setup-claude.sh --check   exit 0 when that folder's claude answers the pinned version, 2 when not
# <main> is the folder that holds git's common directory, so every worktree of a clone shares the one copy.
# The folder is git-ignored, and the install replaces it whole, so this is also the fix for any folder
# --check finds red. Run it once per clone, and again after the pin moves. CI never installs with it: the
# workflow installs the pinned version globally, and the folder never exists there; only its fixture,
# scripts/tests/setup-claude.sh, runs it, in the kit job, on throwaway repositories with a fake npm.
# The pin is read as the file's bytes: exactly one version of three numbers, ASCII digits, with at most one
# final line feed, as pinned_claude of scripts/kit_module_doc.py reads it; anything else is BROKEN.
# Exit: 0 done / green; 1 BROKEN (a misuse, a missing tool, an unreadable pin, a failed install); 2 RED.

LC_ALL=C; export LC_ALL

PIN_FIX="write the one version Claude Code's npm package carries, e.g. 2.1.282, as the file's only line"

broken() {
    printf 'BROKEN: %s\n' "$1" >&2
    exit 1
}

[ "$#" -eq 0 ] || { [ "$#" -eq 1 ] && [ "$1" = "--check" ]; } || broken "unknown argument '$*' — fix: sh scripts/setup-claude.sh [--check]"

command -v git >/dev/null 2>&1 || broken "git is not installed, and the pinned folder is found through it — fix: install it and put it on PATH"
top=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ] && cd "$top" || broken "not inside a git repository — fix: run it from a clone of the kit"
common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) && [ -n "$common" ] || broken "git gave no common directory — fix: run it from a clone of the kit"
main=$(dirname "$common")
folder="$main/.claude-code-pinned"
claude="$folder/node_modules/.bin/claude"

pin_file="$top/scripts/claude-code.version"
[ -f "$pin_file" ] && [ -r "$pin_file" ] || broken "$pin_file cannot be read — fix: $PIN_FIX"
nl='
'
size=$(wc -c <"$pin_file") && size=$((size + 0))
[ "$size" -gt 0 ] || broken "$pin_file is empty — fix: $PIN_FIX"
# a NUL byte is dropped by the shell's read, so it is looked for first
[ "$(tr -d '\000' <"$pin_file" | wc -c | tr -d ' ')" -eq "$size" ] || broken "$pin_file is not one version — fix: $PIN_FIX"
raw=$(cat "$pin_file"; printf x) && raw=${raw%x}
pin=${raw%"$nl"}
case $pin in
    *[!0123456789.]* | .* | *. | *..* | *.*.*.*) broken "$pin_file is not one version — fix: $PIN_FIX" ;;
    *.*.*) ;;
    *) broken "$pin_file is not one version — fix: $PIN_FIX" ;;
esac

# check: exit 0 with a GREEN line when the folder's claude answers the pin, else the RED line and exit 2
check() {
    if [ ! -x "$claude" ]; then
        red "$folder has no executable node_modules/.bin/claude"
    fi
    config=$(mktemp -d "${TMPDIR:-/tmp}/claude-version.XXXXXX") || broken "no temporary folder could be made under ${TMPDIR:-/tmp} — fix: make TMPDIR name a folder you can write to"
    said=$(CLAUDE_CONFIG_DIR="$config" DISABLE_AUTOUPDATER=1 "$claude" --version 2>&1 </dev/null)
    code=$?
    rm -rf "$config"
    found=$(printf '%s\n' "$said" | awk 'NF { print $1; exit }')
    [ "$code" -eq 0 ] && [ -n "$found" ] || red "its claude exited $code without a version (${found:-no output})"
    [ "$found" = "$pin" ] || red "its claude answers $found, not $pin"
    echo "GREEN: $folder holds Claude Code $pin, which scripts/gate-list.sh --run puts first on PATH for the install and session entries and the guide"
    exit 0
}

red() {
    cat >&2 <<MSG
RED: the pinned Claude Code $pin is not set up — $1
  why: the install and session entries and the guide fail to run on any other version, and the gate list finds the pinned one only in $folder
  fix: sh scripts/setup-claude.sh
MSG
    exit 2
}

if [ "$1" = "--check" ]; then
    check
fi

command -v npm >/dev/null 2>&1 || broken "npm is not installed, and Claude Code is an npm package — fix: install Node.js with npm (https://nodejs.org/) and put npm on PATH"
# the folder is replaced whole: npm leaves a folder that already holds the package as it is ("up to date"),
# so a claude that was replaced, damaged or made non-executable would stay, and --check stay red
rm -rf "$folder" || broken "$folder could not be removed — fix: remove it by hand, then run sh scripts/setup-claude.sh again"
npm install --prefix "$folder" --no-audit --no-fund "@anthropic-ai/claude-code@$pin" || {
    broken "npm install exited $? — fix: run npm install --prefix \"$folder\" --no-audit --no-fund \"@anthropic-ai/claude-code@$pin\" by hand and read why it fails"
}
check
